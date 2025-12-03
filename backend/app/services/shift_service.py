"""
Shift service containing business logic for shift operations.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.shift import Shift, EmployeeShift
from app.models.employee import Employee
from app.schemas.shift import ShiftCreate, ShiftUpdate, EmployeeShiftCreate


class ShiftService:
    """Service class for shift operations."""
    
    @staticmethod
    async def get_shift_by_id(
        db: AsyncSession,
        shift_id: UUID
    ) -> Optional[Shift]:
        """
        Get a shift by ID.
        
        Args:
            db: Database session
            shift_id: Shift UUID
            
        Returns:
            Shift object or None if not found
        """
        result = await db.execute(
            select(Shift).where(Shift.id == shift_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_shifts(
        db: AsyncSession,
        include_inactive: bool = False
    ) -> List[Shift]:
        """
        Get all shifts.
        
        Args:
            db: Database session
            include_inactive: Whether to include inactive shifts
            
        Returns:
            List of shifts
        """
        query = select(Shift)
        
        if not include_inactive:
            query = query.where(Shift.is_active == True)
        
        query = query.order_by(Shift.start_time)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def create_shift(
        db: AsyncSession,
        shift_data: ShiftCreate
    ) -> Shift:
        """
        Create a new shift.
        
        Args:
            db: Database session
            shift_data: Shift creation data
            
        Returns:
            Created shift object
            
        Raises:
            HTTPException: If shift name already exists
        """
        # Check if shift name exists
        result = await db.execute(
            select(Shift).where(Shift.name == shift_data.name)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Shift with name '{shift_data.name}' already exists"
            )
        
        # Create shift
        shift = Shift(**shift_data.model_dump())
        
        db.add(shift)
        await db.commit()
        await db.refresh(shift)
        
        return shift
    
    @staticmethod
    async def update_shift(
        db: AsyncSession,
        shift_id: UUID,
        shift_data: ShiftUpdate
    ) -> Shift:
        """
        Update a shift.
        
        Args:
            db: Database session
            shift_id: Shift UUID
            shift_data: Shift update data
            
        Returns:
            Updated shift object
            
        Raises:
            HTTPException: If shift not found or validation fails
        """
        shift = await ShiftService.get_shift_by_id(db, shift_id)
        
        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found"
            )
        
        # Check name uniqueness if changing
        if shift_data.name and shift_data.name != shift.name:
            result = await db.execute(
                select(Shift).where(
                    Shift.name == shift_data.name,
                    Shift.id != shift_id
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Shift with name '{shift_data.name}' already exists"
                )
        
        # Update fields
        update_data = shift_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(shift, field, value)
        
        await db.commit()
        await db.refresh(shift)
        
        return shift
    
    @staticmethod
    async def delete_shift(
        db: AsyncSession,
        shift_id: UUID
    ) -> None:
        """
        Soft delete a shift by setting is_active to False.
        
        Args:
            db: Database session
            shift_id: Shift UUID
            
        Raises:
            HTTPException: If shift not found or has active assignments
        """
        shift = await ShiftService.get_shift_by_id(db, shift_id)
        
        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found"
            )
        
        # Check for active assignments
        result = await db.execute(
            select(func.count()).select_from(EmployeeShift).where(
                EmployeeShift.shift_id == shift_id,
                EmployeeShift.effective_to.is_(None) | (EmployeeShift.effective_to >= date.today())
            )
        )
        active_count = result.scalar_one()
        
        if active_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete shift with {active_count} active employee assignments"
            )
        
        # Soft delete
        shift.is_active = False
        await db.commit()
    
    @staticmethod
    async def assign_shift_to_employee(
        db: AsyncSession,
        employee_id: UUID,
        shift_assignment: EmployeeShiftCreate
    ) -> EmployeeShift:
        """
        Assign a shift to an employee.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            shift_assignment: Shift assignment data
            
        Returns:
            Created employee shift object
            
        Raises:
            HTTPException: If employee or shift not found, or validation fails
        """
        # Verify employee exists
        result = await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Verify shift exists and is active
        shift = await ShiftService.get_shift_by_id(db, shift_assignment.shift_id)
        
        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shift not found"
            )
        
        if not shift.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign inactive shift"
            )
        
        # Check for overlapping assignments
        result = await db.execute(
            select(EmployeeShift).where(
                EmployeeShift.employee_id == employee_id,
                EmployeeShift.effective_to.is_(None) | (EmployeeShift.effective_to >= shift_assignment.effective_from)
            )
        )
        existing_assignments = result.scalars().all()
        
        # End any overlapping assignments
        for assignment in existing_assignments:
            if assignment.effective_from <= shift_assignment.effective_from:
                # Set effective_to to one day before new assignment starts
                from datetime import timedelta
                assignment.effective_to = shift_assignment.effective_from - timedelta(days=1)
        
        # Create new assignment
        employee_shift = EmployeeShift(
            employee_id=employee_id,
            shift_id=shift_assignment.shift_id,
            effective_from=shift_assignment.effective_from,
            effective_to=shift_assignment.effective_to
        )
        
        db.add(employee_shift)
        await db.commit()
        await db.refresh(employee_shift)
        
        # Load relationships
        await db.refresh(employee_shift, ["shift", "employee"])
        
        return employee_shift
    
    @staticmethod
    async def get_employee_shifts(
        db: AsyncSession,
        employee_id: UUID
    ) -> List[EmployeeShift]:
        """
        Get all shift assignments for an employee.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            
        Returns:
            List of employee shifts
        """
        result = await db.execute(
            select(EmployeeShift)
            .where(EmployeeShift.employee_id == employee_id)
            .options(
                selectinload(EmployeeShift.shift),
                selectinload(EmployeeShift.employee)
            )
            .order_by(EmployeeShift.effective_from.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_current_employee_shift(
        db: AsyncSession,
        employee_id: UUID,
        target_date: Optional[date] = None
    ) -> Optional[EmployeeShift]:
        """
        Get the current shift assignment for an employee on a specific date.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            target_date: Date to check (defaults to today)
            
        Returns:
            Current employee shift or None
        """
        if not target_date:
            target_date = date.today()
        
        result = await db.execute(
            select(EmployeeShift)
            .where(
                EmployeeShift.employee_id == employee_id,
                EmployeeShift.effective_from <= target_date,
                (EmployeeShift.effective_to.is_(None)) | (EmployeeShift.effective_to >= target_date)
            )
            .options(selectinload(EmployeeShift.shift))
        )
        
        return result.scalar_one_or_none()



