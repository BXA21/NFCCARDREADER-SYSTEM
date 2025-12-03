"""
Employee service containing business logic for employee operations.
"""

from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.employee import Employee, EmployeeStatus
from app.models.user import User, UserRole
from app.models.card import Card, CardStatus
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.utils.security import hash_password


class EmployeeService:
    """Service class for employee operations."""
    
    @staticmethod
    async def get_employee_by_id(
        db: AsyncSession,
        employee_id: UUID
    ) -> Optional[Employee]:
        """
        Get an employee by ID.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            
        Returns:
            Employee object or None if not found
        """
        result = await db.execute(
            select(Employee)
            .where(Employee.id == employee_id)
            .options(
                selectinload(Employee.supervisor),
                selectinload(Employee.cards),
                selectinload(Employee.user)
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_employees(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        department: Optional[str] = None,
        status: Optional[EmployeeStatus] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Employee], int]:
        """
        Get a paginated list of employees with optional filters.
        
        Args:
            db: Database session
            page: Page number (1-indexed)
            page_size: Number of items per page
            department: Filter by department
            status: Filter by status
            search: Search in name, email, or employee number
            
        Returns:
            Tuple of (list of employees, total count)
        """
        # Build query
        query = select(Employee).options(
            selectinload(Employee.supervisor),
            selectinload(Employee.cards)
        )
        
        # Apply filters
        if department:
            query = query.where(Employee.department == department)
        
        if status:
            query = query.where(Employee.status == status)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Employee.full_name.ilike(search_pattern),
                    Employee.email.ilike(search_pattern),
                    Employee.employee_no.ilike(search_pattern)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(Employee)
        if department:
            count_query = count_query.where(Employee.department == department)
        if status:
            count_query = count_query.where(Employee.status == status)
        if search:
            search_pattern = f"%{search}%"
            count_query = count_query.where(
                or_(
                    Employee.full_name.ilike(search_pattern),
                    Employee.email.ilike(search_pattern),
                    Employee.employee_no.ilike(search_pattern)
                )
            )
        
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(Employee.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        employees = result.scalars().all()
        
        return list(employees), total
    
    @staticmethod
    async def create_employee(
        db: AsyncSession,
        employee_data: EmployeeCreate
    ) -> Employee:
        """
        Create a new employee.
        
        Args:
            db: Database session
            employee_data: Employee creation data
            
        Returns:
            Created employee object
            
        Raises:
            HTTPException: If employee number or email already exists
        """
        # Check if employee number exists
        result = await db.execute(
            select(Employee).where(Employee.employee_no == employee_data.employee_no)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee number {employee_data.employee_no} already exists"
            )
        
        # Check if email exists
        result = await db.execute(
            select(Employee).where(Employee.email == employee_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {employee_data.email} already exists"
            )
        
        # Verify supervisor exists if provided
        if employee_data.supervisor_id:
            result = await db.execute(
                select(Employee).where(Employee.id == employee_data.supervisor_id)
            )
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supervisor not found"
                )
        
        # Create employee
        employee = Employee(**employee_data.model_dump())
        
        db.add(employee)
        await db.commit()
        await db.refresh(employee)
        
        # Create default user account for the employee
        await EmployeeService._create_default_user(db, employee)
        
        return employee
    
    @staticmethod
    async def update_employee(
        db: AsyncSession,
        employee_id: UUID,
        employee_data: EmployeeUpdate
    ) -> Employee:
        """
        Update an employee.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            employee_data: Employee update data
            
        Returns:
            Updated employee object
            
        Raises:
            HTTPException: If employee not found or validation fails
        """
        # Get employee
        employee = await EmployeeService.get_employee_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Check email uniqueness if changing
        if employee_data.email and employee_data.email != employee.email:
            result = await db.execute(
                select(Employee).where(
                    Employee.email == employee_data.email,
                    Employee.id != employee_id
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email {employee_data.email} already exists"
                )
        
        # Verify supervisor exists if provided
        if employee_data.supervisor_id:
            if employee_data.supervisor_id == employee_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Employee cannot be their own supervisor"
                )
            
            result = await db.execute(
                select(Employee).where(Employee.id == employee_data.supervisor_id)
            )
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supervisor not found"
                )
        
        # Update fields
        update_data = employee_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)
        
        await db.commit()
        await db.refresh(employee)
        
        return employee
    
    @staticmethod
    async def delete_employee(
        db: AsyncSession,
        employee_id: UUID
    ) -> None:
        """
        Soft delete an employee by setting status to TERMINATED.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            
        Raises:
            HTTPException: If employee not found
        """
        employee = await EmployeeService.get_employee_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Soft delete
        employee.status = EmployeeStatus.TERMINATED
        
        # Deactivate user account if exists
        if employee.user:
            employee.user.is_active = False
        
        await db.commit()
    
    @staticmethod
    async def _create_default_user(
        db: AsyncSession,
        employee: Employee
    ) -> User:
        """
        Create a default user account for an employee.
        Username is generated from employee number.
        Default password is Employee@123 (should be changed on first login).
        
        Args:
            db: Database session
            employee: Employee object
            
        Returns:
            Created user object
        """
        # Generate username from employee number
        username = employee.employee_no.lower()
        
        # Create user
        user = User(
            username=username,
            password_hash=hash_password("Employee@123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
            employee_id=employee.id
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def get_employee_with_card_status(
        db: AsyncSession,
        employee_id: UUID
    ) -> Tuple[Employee, bool]:
        """
        Get an employee with their active card status.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            
        Returns:
            Tuple of (employee, has_active_card)
        """
        employee = await EmployeeService.get_employee_by_id(db, employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Check if employee has an active card
        has_active_card = any(
            card.status == CardStatus.ACTIVE for card in employee.cards
        )
        
        return employee, has_active_card



