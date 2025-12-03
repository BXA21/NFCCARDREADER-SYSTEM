"""
Manual Operations router for HR manual attendance and leave management.
Provides endpoints for manual attendance entry, editing, leave management, and employee self-service.
"""

from typing import Optional, List
from uuid import UUID
from datetime import date
from math import ceil
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.leave import LeaveStatus
from app.models.attendance import AttendanceEventType
from app.schemas.manual import (
    ManualAttendanceCreate,
    ManualAttendanceResponse,
    AttendanceEditRequest,
    AttendanceDeleteRequest,
    BulkAttendanceCreate,
    BulkAttendanceResponse,
    LeaveTypeResponse,
    LeaveRecordCreate,
    LeaveRecordUpdate,
    LeaveRecordResponse,
    LeaveRecordListItem,
    EmployeeSelfClockRequest,
    EmployeeSelfClockResponse,
    EmployeePinSetRequest,
    EmployeeTodayStatus,
    AttendanceRecordWithSource,
)
from app.schemas.common import PaginatedResponse
from app.services.manual_service import ManualService
from app.utils.dependencies import get_current_active_user, require_hr_admin

router = APIRouter()


# ============ Manual Attendance Endpoints ============

@router.post("/manual/attendance/clock", response_model=ManualAttendanceResponse)
async def manual_clock(
    data: ManualAttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Manually record a clock in/out for an employee.
    
    **Use Cases:**
    - Employee forgot NFC card
    - NFC reader malfunction
    - Retroactive attendance entry
    
    **Authorization:**
    - HR_ADMIN only
    """
    event, message = await ManualService.create_manual_attendance(
        db=db,
        data=data,
        entered_by=current_user.username
    )
    
    # Load employee relationship
    await db.refresh(event, ["employee"])
    
    # Broadcast to WebSocket for real-time dashboard update
    from app.routers.websocket import get_ws_manager
    import asyncio
    ws_manager = get_ws_manager()
    asyncio.create_task(ws_manager.send_attendance_event(
        event_type=event.event_type.value,
        employee_name=event.employee.full_name,
        employee_no=event.employee.employee_no,
        department=event.employee.department,
        timestamp=event.event_timestamp,
        device_id=event.device_id,
        message=message
    ))
    
    return ManualAttendanceResponse(
        id=event.id,
        employee_id=event.employee_id,
        employee_name=event.employee.full_name,
        employee_no=event.employee.employee_no,
        event_type=event.event_type,
        event_timestamp=event.event_timestamp,
        entry_source=event.entry_source,
        notes=event.notes,
        entered_by=event.entered_by,
        message=message
    )


@router.put("/manual/attendance/{record_id}", response_model=ManualAttendanceResponse)
async def edit_attendance_record(
    record_id: UUID,
    data: AttendanceEditRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Edit an existing attendance record.
    
    **Use Cases:**
    - Correct wrong clock in/out time
    - Change event type (IN/OUT)
    - Add notes to a record
    
    **Authorization:**
    - HR_ADMIN only
    """
    event = await ManualService.edit_attendance_record(
        db=db,
        record_id=record_id,
        data=data,
        edited_by=current_user.username
    )
    
    # Load employee relationship
    await db.refresh(event, ["employee"])
    
    return ManualAttendanceResponse(
        id=event.id,
        employee_id=event.employee_id,
        employee_name=event.employee.full_name,
        employee_no=event.employee.employee_no,
        event_type=event.event_type,
        event_timestamp=event.event_timestamp,
        entry_source=event.entry_source,
        notes=event.notes,
        entered_by=event.entered_by,
        message=f"Record updated by {current_user.username}"
    )


@router.delete("/manual/attendance/{record_id}")
async def delete_attendance_record(
    record_id: UUID,
    reason: str = Query(..., min_length=5, description="Reason for deletion"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Delete an attendance record.
    
    **Warning:** This permanently removes the record.
    
    **Authorization:**
    - HR_ADMIN only
    """
    await ManualService.delete_attendance_record(
        db=db,
        record_id=record_id,
        deleted_by=current_user.username,
        reason=reason
    )
    
    return {"message": "Attendance record deleted successfully"}


@router.post("/manual/attendance/bulk", response_model=BulkAttendanceResponse)
async def bulk_attendance_entry(
    data: BulkAttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Create bulk attendance entries for multiple employees.
    
    **Use Cases:**
    - Company event (all employees clock in at same time)
    - Office closure (mark all present employees as clocked out)
    - Import historical data
    
    **Authorization:**
    - HR_ADMIN only
    """
    success, failed, failed_list = await ManualService.create_bulk_attendance(
        db=db,
        data=data,
        entered_by=current_user.username
    )
    
    return BulkAttendanceResponse(
        success_count=success,
        failed_count=failed,
        failed_employees=failed_list,
        message=f"Created {success} attendance records. {failed} failed."
    )


# ============ Leave Management Endpoints ============

@router.get("/manual/leave/types", response_model=List[LeaveTypeResponse])
async def get_leave_types(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all available leave types.
    
    **Authorization:**
    - All authenticated users
    """
    leave_types = await ManualService.get_leave_types(db)
    return [LeaveTypeResponse.model_validate(lt) for lt in leave_types]


@router.post("/manual/leave", response_model=LeaveRecordResponse, status_code=201)
async def create_leave_record(
    data: LeaveRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Create a leave record for an employee.
    
    **Use Cases:**
    - Record approved leave
    - Enter sick leave retroactively
    - Mark employee as on leave
    
    **Authorization:**
    - HR_ADMIN only
    """
    record = await ManualService.create_leave_record(
        db=db,
        data=data,
        entered_by=current_user.username
    )
    
    # Load relationships
    await db.refresh(record, ["employee", "leave_type"])
    
    return LeaveRecordResponse(
        id=record.id,
        employee_id=record.employee_id,
        employee_name=record.employee.full_name,
        employee_no=record.employee.employee_no,
        leave_type_id=record.leave_type_id,
        leave_type_name=record.leave_type.name,
        start_date=record.start_date,
        end_date=record.end_date,
        days_count=record.days_count,
        notes=record.notes,
        status=record.status,
        entered_by=record.entered_by,
        approved_by=record.approved_by,
        approved_at=record.approved_at,
        created_at=record.created_at
    )


@router.get("/manual/leave", response_model=PaginatedResponse[LeaveRecordListItem])
async def get_leave_records(
    employee_id: Optional[UUID] = Query(None, description="Filter by employee"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date"),
    status: Optional[LeaveStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get leave records with filters.
    
    **Authorization:**
    - All authenticated users
    """
    records, total = await ManualService.get_leave_records(
        db=db,
        employee_id=employee_id,
        from_date=from_date,
        to_date=to_date,
        status_filter=status,
        page=page,
        page_size=page_size
    )
    
    items = []
    for record in records:
        items.append(LeaveRecordListItem(
            id=record.id,
            employee_name=record.employee.full_name,
            employee_no=record.employee.employee_no,
            leave_type_name=record.leave_type.name,
            start_date=record.start_date,
            end_date=record.end_date,
            days_count=record.days_count,
            status=record.status
        ))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total > 0 else 1
    )


@router.put("/manual/leave/{record_id}", response_model=LeaveRecordResponse)
async def update_leave_record(
    record_id: UUID,
    data: LeaveRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Update a leave record.
    
    **Authorization:**
    - HR_ADMIN only
    """
    record = await ManualService.update_leave_record(
        db=db,
        record_id=record_id,
        data=data,
        updated_by=current_user.username
    )
    
    return LeaveRecordResponse(
        id=record.id,
        employee_id=record.employee_id,
        employee_name=record.employee.full_name,
        employee_no=record.employee.employee_no,
        leave_type_id=record.leave_type_id,
        leave_type_name=record.leave_type.name,
        start_date=record.start_date,
        end_date=record.end_date,
        days_count=record.days_count,
        notes=record.notes,
        status=record.status,
        entered_by=record.entered_by,
        approved_by=record.approved_by,
        approved_at=record.approved_at,
        created_at=record.created_at
    )


@router.delete("/manual/leave/{record_id}")
async def delete_leave_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Delete a leave record.
    
    **Authorization:**
    - HR_ADMIN only
    """
    await ManualService.delete_leave_record(db, record_id)
    return {"message": "Leave record deleted successfully"}


# ============ Employee Self-Service Endpoints ============

@router.post("/employee/set-pin")
async def set_employee_pin(
    data: EmployeePinSetRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Set or update an employee's PIN for self-service.
    
    **PIN Requirements:**
    - 4-6 digits
    
    **Authorization:**
    - HR_ADMIN only
    """
    await ManualService.set_employee_pin(
        db=db,
        employee_id=data.employee_id,
        pin=data.pin
    )
    
    return {"message": "Employee PIN set successfully"}


@router.post("/employee/self-clock", response_model=EmployeeSelfClockResponse)
async def employee_self_clock(
    data: EmployeeSelfClockRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Employee self-service clock in/out.
    
    **No authentication required** - uses employee ID + PIN verification.
    
    **Use Cases:**
    - Employee forgot NFC card
    - NFC reader not working
    - Backup clock in/out method
    
    **Request Body:**
    - employee_id: Employee number (e.g., "EMP-001")
    - pin: 4-6 digit PIN
    - event_type: "IN" or "OUT"
    - reason: Why manual clock is needed
    """
    event, message = await ManualService.employee_self_clock(
        db=db,
        employee_no=data.employee_id,
        pin=data.pin,
        event_type=data.event_type,
        reason=data.reason
    )
    
    # Load employee relationship
    await db.refresh(event, ["employee"])
    
    # Broadcast to WebSocket
    from app.routers.websocket import get_ws_manager
    import asyncio
    ws_manager = get_ws_manager()
    asyncio.create_task(ws_manager.send_attendance_event(
        event_type=event.event_type.value,
        employee_name=event.employee.full_name,
        employee_no=event.employee.employee_no,
        department=event.employee.department,
        timestamp=event.event_timestamp,
        device_id=event.device_id,
        message=f"{event.employee.full_name} - Self-service: {data.reason}"
    ))
    
    return EmployeeSelfClockResponse(
        success=True,
        employee_name=event.employee.full_name,
        event_type=event.event_type,
        timestamp=event.event_timestamp,
        message=message
    )


@router.get("/employee/today-status", response_model=EmployeeTodayStatus)
async def get_employee_today_status(
    employee_no: str = Query(..., description="Employee number"),
    pin: str = Query(..., min_length=4, max_length=6, description="Employee PIN"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get employee's attendance status for today.
    
    **No authentication required** - uses employee ID + PIN verification.
    
    **Returns:**
    - Clock in time (if any)
    - Clock out time (if any)
    - Total hours worked
    - Current status
    """
    # Verify PIN
    employee = await ManualService.verify_employee_pin(db, employee_no, pin)
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee ID or PIN"
        )
    
    status_data = await ManualService.get_employee_today_status(db, employee.id)
    
    return EmployeeTodayStatus(**status_data)


# ============ Register Employee Without NFC ============

@router.post("/manual/employee/register-no-card")
async def register_employee_without_card(
    employee_no: str = Query(..., description="Employee number"),
    full_name: str = Query(..., description="Full name"),
    email: str = Query(..., description="Email address"),
    department: str = Query(..., description="Department"),
    position: Optional[str] = Query(None, description="Job position"),
    phone: Optional[str] = Query(None, description="Phone number"),
    hire_date: date = Query(..., description="Hire date"),
    pin: Optional[str] = Query(None, min_length=4, max_length=6, description="Self-service PIN"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Register a new employee without requiring an NFC card.
    
    **Use Cases:**
    - Remote employees who don't need NFC cards
    - Temporary employees
    - Employees waiting for card assignment
    
    **Card can be assigned later using the card management system.
    
    **Authorization:**
    - HR_ADMIN only
    """
    from app.schemas.employee import EmployeeCreate
    from app.services.employee_service import EmployeeService
    from app.models.employee import Employee
    from sqlalchemy import select
    
    # Create employee
    employee_data = EmployeeCreate(
        employee_no=employee_no,
        full_name=full_name,
        email=email,
        department=department,
        hire_date=hire_date
    )
    
    employee = await EmployeeService.create_employee(db, employee_data)
    
    # Update additional fields
    result = await db.execute(
        select(Employee).where(Employee.id == employee.id)
    )
    emp = result.scalar_one()
    
    if position:
        emp.position = position
    if phone:
        emp.phone = phone
    if pin:
        from app.utils.security import hash_password
        emp.pin_hash = hash_password(pin)
    
    await db.commit()
    await db.refresh(emp)
    
    return {
        "message": f"Employee {full_name} registered successfully",
        "employee_id": str(emp.id),
        "employee_no": emp.employee_no,
        "has_pin": emp.pin_hash is not None,
        "nfc_card_status": "Not assigned - can be assigned later"
    }

