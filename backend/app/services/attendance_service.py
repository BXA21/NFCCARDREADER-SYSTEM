"""
Attendance service containing business logic for attendance operations.
"""

from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.attendance import AttendanceEvent, AttendanceEventType, EventSource
from app.models.employee import Employee, EmployeeStatus
from app.models.card import Card
from app.models.device import Device, DeviceStatus
from app.services.card_service import CardService
from app.schemas.attendance import AttendanceEventCreate
from app.utils.datetime_utils import get_time_difference_seconds


class AttendanceService:
    """Service class for attendance operations."""
    
    # Duplicate event threshold in seconds (1 minute)
    DUPLICATE_THRESHOLD_SECONDS = 60
    
    @staticmethod
    async def record_attendance_event(
        db: AsyncSession,
        event_data: AttendanceEventCreate,
        source: EventSource = EventSource.ONLINE
    ) -> Tuple[AttendanceEvent, str]:
        """
        Record an attendance event from a card tap.
        
        Args:
            db: Database session
            event_data: Event data from reader
            source: Event source (ONLINE or OFFLINE)
            
        Returns:
            Tuple of (created event, welcome message)
            
        Raises:
            HTTPException: If card not found, not active, or duplicate event
        """
        # Validate card and get employee
        card, employee = await CardService.validate_card_for_attendance(
            db, event_data.card_uid
        )
        
        # Check for duplicate events (within last 60 seconds)
        await AttendanceService._check_duplicate_event(
            db, employee.id, event_data.event_timestamp
        )
        
        # Determine event type (IN or OUT)
        event_type = event_data.event_type
        if not event_type:
            event_type = await AttendanceService._determine_event_type(
                db, employee.id, event_data.event_timestamp
            )
        
        # Update device last seen
        await AttendanceService._update_device_status(db, event_data.device_id)
        
        # Create attendance event
        attendance_event = AttendanceEvent(
            id=event_data.event_id,  # Use client-provided ID for idempotency
            employee_id=employee.id,
            card_id=card.id,
            event_type=event_type,
            event_timestamp=event_data.event_timestamp,
            device_id=event_data.device_id,
            source=source
        )
        
        db.add(attendance_event)
        await db.commit()
        await db.refresh(attendance_event)
        
        # Generate welcome message
        message = AttendanceService._generate_message(employee.full_name, event_type)
        
        return attendance_event, message
    
    @staticmethod
    async def _check_duplicate_event(
        db: AsyncSession,
        employee_id: UUID,
        event_timestamp: datetime
    ) -> None:
        """
        Check if this is a duplicate event within the threshold.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            event_timestamp: Timestamp of the new event
            
        Raises:
            HTTPException: If duplicate event detected
        """
        # Get last event for employee
        result = await db.execute(
            select(AttendanceEvent)
            .where(AttendanceEvent.employee_id == employee_id)
            .order_by(AttendanceEvent.event_timestamp.desc())
            .limit(1)
        )
        last_event = result.scalar_one_or_none()
        
        if last_event:
            time_diff = get_time_difference_seconds(
                event_timestamp, last_event.event_timestamp
            )
            
            if time_diff < AttendanceService.DUPLICATE_THRESHOLD_SECONDS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate event detected. Please wait {AttendanceService.DUPLICATE_THRESHOLD_SECONDS} seconds between taps."
                )
    
    @staticmethod
    async def _determine_event_type(
        db: AsyncSession,
        employee_id: UUID,
        event_timestamp: datetime
    ) -> AttendanceEventType:
        """
        Automatically determine if this should be an IN or OUT event.
        Logic: If last event was IN (or no event today), this is OUT. Otherwise, this is IN.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            event_timestamp: Timestamp of the new event
            
        Returns:
            Event type (IN or OUT)
        """
        # Get last event for today
        today_start = event_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        result = await db.execute(
            select(AttendanceEvent)
            .where(
                AttendanceEvent.employee_id == employee_id,
                AttendanceEvent.event_timestamp >= today_start,
                AttendanceEvent.event_timestamp < today_end
            )
            .order_by(AttendanceEvent.event_timestamp.desc())
            .limit(1)
        )
        last_event_today = result.scalar_one_or_none()
        
        # If no event today or last event was OUT, this is IN
        if not last_event_today or last_event_today.event_type == AttendanceEventType.OUT:
            return AttendanceEventType.IN
        else:
            return AttendanceEventType.OUT
    
    @staticmethod
    async def _update_device_status(
        db: AsyncSession,
        device_id: str
    ) -> None:
        """
        Update device last_seen_at and status to ONLINE.
        
        Args:
            db: Database session
            device_id: Device ID
        """
        result = await db.execute(
            select(Device).where(Device.device_id == device_id)
        )
        device = result.scalar_one_or_none()
        
        if device:
            device.last_seen_at = datetime.utcnow()
            device.status = DeviceStatus.ONLINE
            await db.commit()
    
    @staticmethod
    def _generate_message(employee_name: str, event_type: AttendanceEventType) -> str:
        """
        Generate a welcome/goodbye message for the employee.
        
        Args:
            employee_name: Employee's full name
            event_type: Event type (IN or OUT)
            
        Returns:
            Welcome/goodbye message
        """
        if event_type == AttendanceEventType.IN:
            return f"Welcome, {employee_name}!"
        else:
            return f"Goodbye, {employee_name}. Have a great day!"
    
    @staticmethod
    async def get_employee_attendance(
        db: AsyncSession,
        employee_id: UUID,
        from_date: date,
        to_date: date
    ) -> List[AttendanceEvent]:
        """
        Get attendance events for an employee within a date range.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            from_date: Start date
            to_date: End date
            
        Returns:
            List of attendance events
        """
        start_datetime = datetime.combine(from_date, datetime.min.time())
        end_datetime = datetime.combine(to_date, datetime.max.time())
        
        result = await db.execute(
            select(AttendanceEvent)
            .where(
                AttendanceEvent.employee_id == employee_id,
                AttendanceEvent.event_timestamp >= start_datetime,
                AttendanceEvent.event_timestamp <= end_datetime
            )
            .order_by(AttendanceEvent.event_timestamp.asc())
        )
        
        return list(result.scalars().all())
    
    @staticmethod
    async def get_attendance_events(
        db: AsyncSession,
        from_date: date,
        to_date: date,
        employee_id: Optional[UUID] = None,
        department: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[AttendanceEvent], int]:
        """
        Get attendance events with filters and pagination.
        
        Args:
            db: Database session
            from_date: Start date
            to_date: End date
            employee_id: Optional filter by employee
            department: Optional filter by department
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (list of events, total count)
        """
        start_datetime = datetime.combine(from_date, datetime.min.time())
        end_datetime = datetime.combine(to_date, datetime.max.time())
        
        # Build query
        query = select(AttendanceEvent).options(
            selectinload(AttendanceEvent.employee),
            selectinload(AttendanceEvent.card)
        ).where(
            AttendanceEvent.event_timestamp >= start_datetime,
            AttendanceEvent.event_timestamp <= end_datetime
        )
        
        # Apply filters
        if employee_id:
            query = query.where(AttendanceEvent.employee_id == employee_id)
        
        if department:
            query = query.join(Employee).where(Employee.department == department)
        
        # Get total count
        count_query = select(func.count()).select_from(AttendanceEvent).where(
            AttendanceEvent.event_timestamp >= start_datetime,
            AttendanceEvent.event_timestamp <= end_datetime
        )
        
        if employee_id:
            count_query = count_query.where(AttendanceEvent.employee_id == employee_id)
        
        if department:
            count_query = count_query.join(Employee).where(Employee.department == department)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(AttendanceEvent.event_timestamp.desc())
        
        # Execute query
        result = await db.execute(query)
        events = result.scalars().all()
        
        return list(events), total
    
    @staticmethod
    async def calculate_daily_summary(
        db: AsyncSession,
        target_date: date,
        department: Optional[str] = None
    ) -> dict:
        """
        Calculate attendance summary for a specific date.
        
        Args:
            db: Database session
            target_date: Date to summarize
            department: Optional filter by department
            
        Returns:
            Dictionary with summary statistics
        """
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        # Get all active employees
        employee_query = select(Employee).where(Employee.status == EmployeeStatus.ACTIVE)
        if department:
            employee_query = employee_query.where(Employee.department == department)
        
        result = await db.execute(employee_query)
        all_employees = result.scalars().all()
        total_employees = len(all_employees)
        
        # Get employees who clocked in today
        result = await db.execute(
            select(func.count(func.distinct(AttendanceEvent.employee_id)))
            .select_from(AttendanceEvent)
            .where(
                AttendanceEvent.event_timestamp >= start_datetime,
                AttendanceEvent.event_timestamp <= end_datetime,
                AttendanceEvent.event_type == AttendanceEventType.IN
            )
        )
        present_count = result.scalar_one()
        
        # Calculate absent count
        absent_count = total_employees - present_count
        
        # TODO: Calculate late count based on shift schedules
        # For now, return 0
        late_count = 0
        early_leave_count = 0
        
        return {
            "date": target_date,
            "total_employees": total_employees,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "early_leave_count": early_leave_count
        }



