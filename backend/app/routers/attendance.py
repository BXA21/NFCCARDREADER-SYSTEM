"""
Attendance router for recording and viewing attendance events.
"""

from typing import Optional
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.attendance import (
    AttendanceEventCreate,
    AttendanceEventResponse,
    AttendanceEventListItem,
    AttendanceSummary
)
from app.schemas.common import PaginatedResponse
from app.services.attendance_service import AttendanceService
from app.models.user import User
from app.models.device import Device
from app.models.attendance import EventSource
from app.utils.dependencies import verify_device_api_key, get_current_active_user
from math import ceil

router = APIRouter()


@router.post("/attendance-events", response_model=AttendanceEventResponse)
async def record_attendance_event(
    event_data: AttendanceEventCreate,
    db: AsyncSession = Depends(get_db),
    device: Device = Depends(verify_device_api_key)
):
    """
    Record an attendance event from an NFC card tap.
    
    **Smart Scan Mode:**
    - If card is not assigned, automatically routes to scan buffer for wizard
    - If card is assigned, records attendance normally
    
    **Authentication:**
    - Requires X-API-Key header with valid device API key
    
    **Request Body:**
    - card_uid: Card UID read from NFC reader
    - device_id: ID of the device/reader
    - event_timestamp: Timestamp of the tap (ISO 8601 format)
    - event_id: Optional client-generated UUID for idempotency
    - event_type: Optional event type (auto-detected if not provided)
    
    **Returns:**
    - Created attendance event with welcome message
    
    **Errors:**
    - 404: Card not found
    - 400: Card not active, employee not active, or duplicate event
    - 401: Invalid or missing API key
    
    **Business Logic:**
    - Validates card is active and employee is active
    - Auto-detects IN/OUT based on last event
    - Prevents duplicate events within 60 seconds
    - Updates device status to ONLINE
    - Returns personalized welcome/goodbye message
    
    **Example:**
    ```json
    {
      "card_uid": "04A2B3C4D5E6F7",
      "device_id": "GATE-MAIN-01",
      "event_timestamp": "2025-11-25T08:30:00Z",
      "event_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```
    """
    # Verify device_id matches authenticated device
    if event_data.device_id != device.device_id:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device ID mismatch"
        )
    
    # SMART SCAN MODE: Check if card exists
    # If not assigned, route to scan buffer for wizard
    from sqlalchemy import select
    from app.models.card import Card
    result = await db.execute(
        select(Card).where(Card.card_uid == event_data.card_uid)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        # Card not assigned - route to scan buffer for employee creation wizard
        from app.utils.scan_buffer import scan_buffer
        scan_buffer.add_card(event_data.card_uid)
        
        print(f"[ATTENDANCE] Unassigned card detected: {event_data.card_uid} - routing to scan buffer")
        
        # Return HTTP 202 with special message
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=202,
            content={
                "status": "scan_mode",
                "message": f"Card {event_data.card_uid} detected and queued for assignment",
                "card_uid": event_data.card_uid,
                "detected_at": datetime.utcnow().isoformat()
            }
        )
    
    # Record attendance event
    event, message = await AttendanceService.record_attendance_event(
        db=db,
        event_data=event_data,
        source=EventSource.ONLINE
    )
    
    # Load employee relationship for response
    await db.refresh(event, ["employee"])
    
    # Broadcast to WebSocket clients for real-time dashboard updates
    from app.routers.websocket import get_ws_manager
    from app.models.attendance import EntrySource
    import asyncio
    ws_manager = get_ws_manager()
    asyncio.create_task(ws_manager.send_attendance_event(
        event_type=event.event_type.value,
        employee_name=event.employee.full_name,
        employee_no=event.employee.employee_no,
        department=event.employee.department,
        timestamp=event.event_timestamp,
        device_id=event.device_id,
        message=message,
        entry_source=event.entry_source.value if hasattr(event, 'entry_source') and event.entry_source else EntrySource.NFC.value,
        notes=event.notes if hasattr(event, 'notes') else None
    ))
    
    # Build response
    response = AttendanceEventResponse(
        **event.__dict__,
        employee_name=event.employee.full_name,
        employee_no=event.employee.employee_no,
        message=message
    )
    
    return response


@router.get("/attendance/me", response_model=PaginatedResponse[AttendanceEventListItem])
async def get_my_attendance(
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance history for the current logged-in user.
    
    **Query Parameters:**
    - from_date: Start date (required)
    - to_date: End date (required)
    
    **Returns:**
    - List of attendance events for the user
    
    **Authorization:**
    - All authenticated users (EMPLOYEE, SUPERVISOR, HR_ADMIN)
    """
    # Get employee_id from current_user
    employee_id = current_user.employee_id
    
    # Get attendance events
    events = await AttendanceService.get_employee_attendance(
        db=db,
        employee_id=employee_id,
        from_date=from_date,
        to_date=to_date
    )
    
    # Convert to list items
    items = [
        AttendanceEventListItem(
            id=event.id,
            employee_name=event.employee.full_name,
            employee_no=event.employee.employee_no,
            event_type=event.event_type,
            event_timestamp=event.event_timestamp,
            device_id=event.device_id
        )
        for event in events
    ]
    
    return PaginatedResponse(
        items=items,
        total=len(items),
        page=1,
        page_size=len(items),
        total_pages=1
    )


@router.get("/attendance/report", response_model=PaginatedResponse[AttendanceEventListItem])
async def get_attendance_report(
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    employee_id: Optional[UUID] = Query(None, description="Filter by employee"),
    department: Optional[str] = Query(None, description="Filter by department"),
    entry_source: Optional[str] = Query(None, description="Filter by entry source (NFC, MANUAL_HR, MANUAL_EMPLOYEE, BULK_IMPORT)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance report with filters (for supervisors and HR).
    
    **Query Parameters:**
    - from_date: Start date (required)
    - to_date: End date (required)
    - employee_id: Filter by specific employee (optional)
    - department: Filter by department (optional)
    - entry_source: Filter by entry source (optional) - NFC, MANUAL_HR, MANUAL_EMPLOYEE, BULK_IMPORT
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    
    **Returns:**
    - Paginated list of attendance events with entry source
    
    **Authorization:**
    - All authenticated users
    - TODO: Restrict to SUPERVISOR and HR_ADMIN with proper scoping
    """
    from app.models.attendance import EntrySource
    
    # Get attendance events
    events, total = await AttendanceService.get_attendance_events(
        db=db,
        from_date=from_date,
        to_date=to_date,
        employee_id=employee_id,
        department=department,
        page=page,
        page_size=page_size
    )
    
    # Convert to list items with entry source
    items = [
        AttendanceEventListItem(
            id=event.id,
            employee_name=event.employee.full_name,
            employee_no=event.employee.employee_no,
            department=event.employee.department,
            event_type=event.event_type,
            event_timestamp=event.event_timestamp,
            device_id=event.device_id,
            entry_source=event.entry_source if hasattr(event, 'entry_source') and event.entry_source else EntrySource.NFC,
            notes=event.notes if hasattr(event, 'notes') else None
        )
        for event in events
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size)
    )


@router.get("/attendance/summary", response_model=AttendanceSummary)
async def get_attendance_summary(
    target_date: date = Query(..., description="Date to summarize (YYYY-MM-DD)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get attendance summary for a specific date.
    
    **Query Parameters:**
    - target_date: Date to summarize (required)
    - department: Filter by department (optional)
    
    **Returns:**
    - Summary with present, absent, late, and early leave counts
    
    **Authorization:**
    - All authenticated users
    """
    summary = await AttendanceService.calculate_daily_summary(
        db=db,
        target_date=target_date,
        department=department
    )
    
    return AttendanceSummary(**summary)



