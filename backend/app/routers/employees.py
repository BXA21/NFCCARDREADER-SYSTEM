"""
Employee router for CRUD operations on employees.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListItem
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.employee_service import EmployeeService
from app.models.user import User
from app.models.employee import EmployeeStatus
from app.utils.dependencies import require_hr_admin, get_current_active_user
from math import ceil

router = APIRouter()


@router.get("", response_model=PaginatedResponse[EmployeeListItem])
async def get_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    department: Optional[str] = Query(None, description="Filter by department"),
    status: Optional[EmployeeStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name, email, or employee number"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a paginated list of employees.
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - department: Filter by department
    - status: Filter by status (ACTIVE, INACTIVE, TERMINATED)
    - search: Search in name, email, or employee number
    
    **Returns:**
    - Paginated list of employees with total count
    
    **Authorization:**
    - All authenticated users can view employees
    """
    employees, total = await EmployeeService.get_employees(
        db=db,
        page=page,
        page_size=page_size,
        department=department,
        status=status,
        search=search
    )
    
    # Convert to list items with card status
    items = []
    for employee in employees:
        has_active_card = any(card.status.value == "ACTIVE" for card in employee.cards)
        item = EmployeeListItem(
            id=employee.id,
            employee_no=employee.employee_no,
            full_name=employee.full_name,
            email=employee.email,
            department=employee.department,
            status=employee.status,
            has_active_card=has_active_card
        )
        items.append(item)
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size)
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single employee by ID.
    
    **Path Parameters:**
    - employee_id: UUID of the employee
    
    **Returns:**
    - Employee details
    
    **Errors:**
    - 404: Employee not found
    
    **Authorization:**
    - All authenticated users can view employee details
    """
    employee, has_active_card = await EmployeeService.get_employee_with_card_status(
        db, employee_id
    )
    
    # Build response
    response = EmployeeResponse(
        **employee.__dict__,
        has_active_card=has_active_card,
        supervisor_name=employee.supervisor.full_name if employee.supervisor else None
    )
    
    return response


@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    employee_data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Create a new employee.
    
    **Request Body:**
    - employee_no: Employee number (e.g., EMP-001)
    - full_name: Full name
    - email: Email address
    - department: Department name
    - hire_date: Hire date
    - supervisor_id: Optional supervisor UUID
    - status: Employee status (default: ACTIVE)
    
    **Returns:**
    - Created employee details
    
    **Errors:**
    - 400: Employee number or email already exists
    - 404: Supervisor not found
    
    **Authorization:**
    - HR_ADMIN only
    
    **Side Effects:**
    - Creates a default user account with username = employee_no
    - Default password: Employee@123 (should be changed on first login)
    """
    employee = await EmployeeService.create_employee(db, employee_data)
    
    # Build response
    response = EmployeeResponse(
        **employee.__dict__,
        has_active_card=False,
        supervisor_name=employee.supervisor.full_name if employee.supervisor else None
    )
    
    return response


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    employee_data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Update an employee.
    
    **Path Parameters:**
    - employee_id: UUID of the employee
    
    **Request Body:**
    - full_name: Full name (optional)
    - email: Email address (optional)
    - department: Department name (optional)
    - supervisor_id: Supervisor UUID (optional)
    - status: Employee status (optional)
    
    **Returns:**
    - Updated employee details
    
    **Errors:**
    - 404: Employee or supervisor not found
    - 400: Email already exists or validation error
    
    **Authorization:**
    - HR_ADMIN only
    """
    employee = await EmployeeService.update_employee(db, employee_id, employee_data)
    
    # Get card status
    _, has_active_card = await EmployeeService.get_employee_with_card_status(db, employee_id)
    
    # Build response
    response = EmployeeResponse(
        **employee.__dict__,
        has_active_card=has_active_card,
        supervisor_name=employee.supervisor.full_name if employee.supervisor else None
    )
    
    return response


@router.delete("/{employee_id}", response_model=MessageResponse)
async def delete_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Delete (terminate) an employee.
    
    This performs a soft delete by setting the employee status to TERMINATED
    and deactivating their user account.
    
    **Path Parameters:**
    - employee_id: UUID of the employee
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 404: Employee not found
    
    **Authorization:**
    - HR_ADMIN only
    """
    await EmployeeService.delete_employee(db, employee_id)
    
    return MessageResponse(message="Employee terminated successfully")



