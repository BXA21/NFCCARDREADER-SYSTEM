"""
Shift router for shift and employee shift assignment operations.
"""

from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.schemas.shift import (
    ShiftCreate,
    ShiftUpdate,
    ShiftResponse,
    EmployeeShiftCreate,
    EmployeeShiftResponse
)
from app.schemas.common import MessageResponse
from app.services.shift_service import ShiftService
from app.models.user import User
from app.models.shift import EmployeeShift
from app.utils.dependencies import require_hr_admin

router = APIRouter()


@router.get("", response_model=List[ShiftResponse])
async def get_shifts(
    include_inactive: bool = Query(False, description="Include inactive shifts"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Get all shifts.
    
    **Query Parameters:**
    - include_inactive: Include inactive shifts (default: false)
    
    **Returns:**
    - List of shifts with employee count
    
    **Authorization:**
    - HR_ADMIN only
    """
    shifts = await ShiftService.get_all_shifts(db, include_inactive)
    
    # Build response with employee counts
    items = []
    for shift in shifts:
        # Count active employee assignments
        result = await db.execute(
            select(func.count()).select_from(EmployeeShift).where(
                EmployeeShift.shift_id == shift.id,
                (EmployeeShift.effective_to.is_(None)) | (EmployeeShift.effective_to >= func.current_date())
            )
        )
        employee_count = result.scalar_one()
        
        item = ShiftResponse(
            **shift.__dict__,
            employee_count=employee_count
        )
        items.append(item)
    
    return items


@router.get("/{shift_id}", response_model=ShiftResponse)
async def get_shift(
    shift_id: UUID = Path(..., description="Shift UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Get a single shift by ID.
    
    **Path Parameters:**
    - shift_id: UUID of the shift
    
    **Returns:**
    - Shift details with employee count
    
    **Errors:**
    - 404: Shift not found
    
    **Authorization:**
    - HR_ADMIN only
    """
    shift = await ShiftService.get_shift_by_id(db, shift_id)
    
    if not shift:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    
    # Count active employee assignments
    result = await db.execute(
        select(func.count()).select_from(EmployeeShift).where(
            EmployeeShift.shift_id == shift_id,
            (EmployeeShift.effective_to.is_(None)) | (EmployeeShift.effective_to >= func.current_date())
        )
    )
    employee_count = result.scalar_one()
    
    return ShiftResponse(
        **shift.__dict__,
        employee_count=employee_count
    )


@router.post("", response_model=ShiftResponse, status_code=201)
async def create_shift(
    shift_data: ShiftCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Create a new shift.
    
    **Request Body:**
    - name: Shift name
    - start_time: Start time (HH:MM:SS)
    - end_time: End time (HH:MM:SS)
    - grace_minutes: Late tolerance in minutes (default: 15)
    - is_active: Active status (default: true)
    
    **Returns:**
    - Created shift details
    
    **Errors:**
    - 400: Shift name already exists or validation error
    
    **Authorization:**
    - HR_ADMIN only
    """
    shift = await ShiftService.create_shift(db, shift_data)
    
    return ShiftResponse(
        **shift.__dict__,
        employee_count=0
    )


@router.put("/{shift_id}", response_model=ShiftResponse)
async def update_shift(
    shift_id: UUID = Path(..., description="Shift UUID"),
    shift_data: ShiftUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Update a shift.
    
    **Path Parameters:**
    - shift_id: UUID of the shift
    
    **Request Body:**
    - name: Shift name (optional)
    - start_time: Start time (optional)
    - end_time: End time (optional)
    - grace_minutes: Late tolerance in minutes (optional)
    - is_active: Active status (optional)
    
    **Returns:**
    - Updated shift details
    
    **Errors:**
    - 404: Shift not found
    - 400: Shift name already exists or validation error
    
    **Authorization:**
    - HR_ADMIN only
    """
    shift = await ShiftService.update_shift(db, shift_id, shift_data)
    
    # Count active employee assignments
    result = await db.execute(
        select(func.count()).select_from(EmployeeShift).where(
            EmployeeShift.shift_id == shift_id,
            (EmployeeShift.effective_to.is_(None)) | (EmployeeShift.effective_to >= func.current_date())
        )
    )
    employee_count = result.scalar_one()
    
    return ShiftResponse(
        **shift.__dict__,
        employee_count=employee_count
    )


@router.delete("/{shift_id}", response_model=MessageResponse)
async def delete_shift(
    shift_id: UUID = Path(..., description="Shift UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Delete (deactivate) a shift.
    
    **Path Parameters:**
    - shift_id: UUID of the shift
    
    **Returns:**
    - Success message
    
    **Errors:**
    - 404: Shift not found
    - 400: Shift has active employee assignments
    
    **Authorization:**
    - HR_ADMIN only
    
    **Business Rules:**
    - Cannot delete shifts with active employee assignments
    - Performs soft delete (sets is_active to false)
    """
    await ShiftService.delete_shift(db, shift_id)
    
    return MessageResponse(message="Shift deactivated successfully")


@router.post("/employees/{employee_id}/shifts", response_model=EmployeeShiftResponse, status_code=201)
async def assign_shift_to_employee(
    employee_id: UUID = Path(..., description="Employee UUID"),
    shift_assignment: EmployeeShiftCreate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Assign a shift to an employee.
    
    **Path Parameters:**
    - employee_id: UUID of the employee
    
    **Request Body:**
    - shift_id: UUID of the shift
    - effective_from: Start date of assignment
    - effective_to: End date of assignment (optional, null for ongoing)
    
    **Returns:**
    - Created shift assignment details
    
    **Errors:**
    - 404: Employee or shift not found
    - 400: Shift is inactive or validation error
    
    **Authorization:**
    - HR_ADMIN only
    
    **Business Rules:**
    - Automatically ends overlapping shift assignments
    - Shift must be active to be assigned
    - effective_to must be after effective_from if provided
    """
    employee_shift = await ShiftService.assign_shift_to_employee(
        db, employee_id, shift_assignment
    )
    
    # Build response
    response = EmployeeShiftResponse(
        **employee_shift.__dict__,
        shift_name=employee_shift.shift.name,
        employee_name=employee_shift.employee.full_name
    )
    
    return response


@router.get("/employees/{employee_id}/shifts", response_model=List[EmployeeShiftResponse])
async def get_employee_shifts(
    employee_id: UUID = Path(..., description="Employee UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Get all shift assignments for an employee.
    
    **Path Parameters:**
    - employee_id: UUID of the employee
    
    **Returns:**
    - List of shift assignments (past and current)
    
    **Authorization:**
    - HR_ADMIN only
    """
    employee_shifts = await ShiftService.get_employee_shifts(db, employee_id)
    
    # Build response
    items = [
        EmployeeShiftResponse(
            **es.__dict__,
            shift_name=es.shift.name,
            employee_name=es.employee.full_name
        )
        for es in employee_shifts
    ]
    
    return items



