"""
Manual Operations service containing business logic for manual attendance and leave management.
"""

from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, date, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.attendance import AttendanceEvent, AttendanceEventType, EventSource, EntrySource
from app.models.employee import Employee, EmployeeStatus
from app.models.leave import LeaveRecord, LeaveType, LeaveStatus
from app.schemas.manual import (
    ManualAttendanceCreate,
    AttendanceEditRequest,
    BulkAttendanceCreate,
    LeaveRecordCreate,
    LeaveRecordUpdate,
)
from app.utils.security import hash_password, verify_password


class ManualService:
    """Service class for manual operations."""
    
    # ============ Manual Attendance Methods ============
    
    @staticmethod
    async def create_manual_attendance(
        db: AsyncSession,
        data: ManualAttendanceCreate,
        entered_by: str
    ) -> Tuple[AttendanceEvent, str]:
        """
        Create a manual attendance entry.
        
        Args:
            db: Database session
            data: Manual attendance data
            entered_by: Username of HR who entered this record
            
        Returns:
            Tuple of (created event, message)
        """
        # Verify employee exists and is active
        result = await db.execute(
            select(Employee).where(Employee.id == data.employee_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        if employee.status != EmployeeStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot record attendance for inactive employee"
            )
        
        # Combine date and time
        event_timestamp = datetime.combine(data.event_date, data.event_time)
        
        # Create attendance event
        attendance_event = AttendanceEvent(
            employee_id=employee.id,
            card_id=None,  # No card for manual entries
            event_type=data.event_type,
            event_timestamp=event_timestamp,
            device_id="MANUAL",  # Special device ID for manual entries
            source=EventSource.ONLINE,
            entry_source=EntrySource.MANUAL_HR,
            notes=data.notes,
            entered_by=entered_by
        )
        
        db.add(attendance_event)
        await db.commit()
        await db.refresh(attendance_event)
        
        # Generate message
        action = "clocked IN" if data.event_type == AttendanceEventType.IN else "clocked OUT"
        message = f"{employee.full_name} manually {action} by {entered_by}"
        
        return attendance_event, message
    
    @staticmethod
    async def edit_attendance_record(
        db: AsyncSession,
        record_id: UUID,
        data: AttendanceEditRequest,
        edited_by: str
    ) -> AttendanceEvent:
        """
        Edit an existing attendance record.
        
        Args:
            db: Database session
            record_id: Attendance event UUID
            data: Edit data
            edited_by: Username of HR who edited this record
            
        Returns:
            Updated attendance event
        """
        # Get existing record
        result = await db.execute(
            select(AttendanceEvent)
            .options(selectinload(AttendanceEvent.employee))
            .where(AttendanceEvent.id == record_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        
        # Update fields
        if data.event_time is not None or data.event_date is not None:
            current_date = event.event_timestamp.date() if data.event_date is None else data.event_date
            current_time = event.event_timestamp.time() if data.event_time is None else data.event_time
            event.event_timestamp = datetime.combine(current_date, current_time)
        
        if data.event_type is not None:
            event.event_type = data.event_type
        
        if data.notes is not None:
            # Append to existing notes
            if event.notes:
                event.notes = f"{event.notes}\n[Edit by {edited_by}]: {data.notes}"
            else:
                event.notes = f"[Edit by {edited_by}]: {data.notes}"
        
        # Track edit
        event.edited_at = datetime.utcnow()
        event.edited_by = edited_by
        
        await db.commit()
        await db.refresh(event)
        
        return event
    
    @staticmethod
    async def delete_attendance_record(
        db: AsyncSession,
        record_id: UUID,
        deleted_by: str,
        reason: str
    ) -> None:
        """
        Delete an attendance record.
        
        Args:
            db: Database session
            record_id: Attendance event UUID
            deleted_by: Username of HR who deleted this record
            reason: Reason for deletion
        """
        # Verify record exists
        result = await db.execute(
            select(AttendanceEvent).where(AttendanceEvent.id == record_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )
        
        # TODO: Log deletion to audit log before deleting
        # For now, just delete
        await db.delete(event)
        await db.commit()
    
    @staticmethod
    async def create_bulk_attendance(
        db: AsyncSession,
        data: BulkAttendanceCreate,
        entered_by: str
    ) -> Tuple[int, int, List[str]]:
        """
        Create bulk attendance entries.
        
        Args:
            db: Database session
            data: Bulk attendance data
            entered_by: Username of HR who entered these records
            
        Returns:
            Tuple of (success_count, failed_count, failed_employee_ids)
        """
        success_count = 0
        failed_count = 0
        failed_employees = []
        
        event_timestamp = datetime.combine(data.event_date, data.event_time)
        
        for employee_id in data.employee_ids:
            try:
                # Verify employee
                result = await db.execute(
                    select(Employee).where(
                        Employee.id == employee_id,
                        Employee.status == EmployeeStatus.ACTIVE
                    )
                )
                employee = result.scalar_one_or_none()
                
                if not employee:
                    failed_count += 1
                    failed_employees.append(str(employee_id))
                    continue
                
                # Create attendance event
                attendance_event = AttendanceEvent(
                    employee_id=employee.id,
                    card_id=None,
                    event_type=data.event_type,
                    event_timestamp=event_timestamp,
                    device_id="BULK_IMPORT",
                    source=EventSource.ONLINE,
                    entry_source=EntrySource.BULK_IMPORT,
                    notes=data.notes,
                    entered_by=entered_by
                )
                
                db.add(attendance_event)
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                failed_employees.append(str(employee_id))
        
        await db.commit()
        
        return success_count, failed_count, failed_employees
    
    # ============ Leave Management Methods ============
    
    @staticmethod
    async def get_leave_types(db: AsyncSession) -> List[LeaveType]:
        """Get all active leave types."""
        result = await db.execute(
            select(LeaveType).where(LeaveType.is_active == True)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create_leave_record(
        db: AsyncSession,
        data: LeaveRecordCreate,
        entered_by: str
    ) -> LeaveRecord:
        """
        Create a leave record.
        
        Args:
            db: Database session
            data: Leave record data
            entered_by: Username of HR who created this record
            
        Returns:
            Created leave record
        """
        # Verify employee exists
        result = await db.execute(
            select(Employee).where(Employee.id == data.employee_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Verify leave type exists
        result = await db.execute(
            select(LeaveType).where(LeaveType.id == data.leave_type_id)
        )
        leave_type = result.scalar_one_or_none()
        
        if not leave_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave type not found"
            )
        
        # Validate dates
        if data.end_date < data.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after or equal to start date"
            )
        
        # Check for overlapping leaves
        result = await db.execute(
            select(LeaveRecord).where(
                LeaveRecord.employee_id == data.employee_id,
                LeaveRecord.status != LeaveStatus.CANCELLED,
                LeaveRecord.start_date <= data.end_date,
                LeaveRecord.end_date >= data.start_date
            )
        )
        overlapping = result.scalar_one_or_none()
        
        if overlapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leave dates overlap with an existing leave record"
            )
        
        # Create leave record
        leave_record = LeaveRecord(
            employee_id=data.employee_id,
            leave_type_id=data.leave_type_id,
            start_date=data.start_date,
            end_date=data.end_date,
            notes=data.notes,
            status=data.status,
            entered_by=entered_by,
            approved_by=entered_by if data.status == LeaveStatus.APPROVED else None,
            approved_at=datetime.utcnow() if data.status == LeaveStatus.APPROVED else None
        )
        
        db.add(leave_record)
        await db.commit()
        await db.refresh(leave_record)
        
        return leave_record
    
    @staticmethod
    async def get_leave_records(
        db: AsyncSession,
        employee_id: Optional[UUID] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        status_filter: Optional[LeaveStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[LeaveRecord], int]:
        """
        Get leave records with filters.
        
        Returns:
            Tuple of (list of leave records, total count)
        """
        # Build query
        query = select(LeaveRecord).options(
            selectinload(LeaveRecord.employee),
            selectinload(LeaveRecord.leave_type)
        )
        
        count_query = select(func.count()).select_from(LeaveRecord)
        
        # Apply filters
        if employee_id:
            query = query.where(LeaveRecord.employee_id == employee_id)
            count_query = count_query.where(LeaveRecord.employee_id == employee_id)
        
        if from_date:
            query = query.where(LeaveRecord.end_date >= from_date)
            count_query = count_query.where(LeaveRecord.end_date >= from_date)
        
        if to_date:
            query = query.where(LeaveRecord.start_date <= to_date)
            count_query = count_query.where(LeaveRecord.start_date <= to_date)
        
        if status_filter:
            query = query.where(LeaveRecord.status == status_filter)
            count_query = count_query.where(LeaveRecord.status == status_filter)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(LeaveRecord.start_date.desc())
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        return list(records), total
    
    @staticmethod
    async def update_leave_record(
        db: AsyncSession,
        record_id: UUID,
        data: LeaveRecordUpdate,
        updated_by: str
    ) -> LeaveRecord:
        """Update a leave record."""
        result = await db.execute(
            select(LeaveRecord)
            .options(selectinload(LeaveRecord.employee), selectinload(LeaveRecord.leave_type))
            .where(LeaveRecord.id == record_id)
        )
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave record not found"
            )
        
        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        
        # Track approval changes
        if data.status == LeaveStatus.APPROVED and record.approved_at is None:
            record.approved_by = updated_by
            record.approved_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(record)
        
        return record
    
    @staticmethod
    async def delete_leave_record(db: AsyncSession, record_id: UUID) -> None:
        """Delete a leave record."""
        result = await db.execute(
            select(LeaveRecord).where(LeaveRecord.id == record_id)
        )
        record = result.scalar_one_or_none()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Leave record not found"
            )
        
        await db.delete(record)
        await db.commit()
    
    # ============ Employee Self-Service Methods ============
    
    @staticmethod
    async def set_employee_pin(
        db: AsyncSession,
        employee_id: UUID,
        pin: str
    ) -> None:
        """
        Set or update an employee's PIN for self-service.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            pin: 4-6 digit PIN
        """
        result = await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Hash and store PIN
        employee.pin_hash = hash_password(pin)
        await db.commit()
    
    @staticmethod
    async def verify_employee_pin(
        db: AsyncSession,
        employee_no: str,
        pin: str
    ) -> Optional[Employee]:
        """
        Verify employee PIN for self-service.
        
        Args:
            db: Database session
            employee_no: Employee number
            pin: PIN to verify
            
        Returns:
            Employee if PIN is valid, None otherwise
        """
        result = await db.execute(
            select(Employee).where(
                Employee.employee_no == employee_no,
                Employee.status == EmployeeStatus.ACTIVE
            )
        )
        employee = result.scalar_one_or_none()
        
        if not employee or not employee.pin_hash:
            return None
        
        if verify_password(pin, employee.pin_hash):
            return employee
        
        return None
    
    @staticmethod
    async def employee_self_clock(
        db: AsyncSession,
        employee_no: str,
        pin: str,
        event_type: AttendanceEventType,
        reason: str
    ) -> Tuple[AttendanceEvent, str]:
        """
        Employee self-service clock in/out.
        
        Args:
            db: Database session
            employee_no: Employee number
            pin: Employee PIN
            event_type: IN or OUT
            reason: Reason for manual clock
            
        Returns:
            Tuple of (created event, message)
        """
        # Verify PIN
        employee = await ManualService.verify_employee_pin(db, employee_no, pin)
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid employee ID or PIN"
            )
        
        # Create attendance event
        attendance_event = AttendanceEvent(
            employee_id=employee.id,
            card_id=None,
            event_type=event_type,
            event_timestamp=datetime.utcnow(),
            device_id="SELF_SERVICE",
            source=EventSource.ONLINE,
            entry_source=EntrySource.MANUAL_EMPLOYEE,
            notes=f"Self-service: {reason}",
            entered_by=employee.employee_no
        )
        
        db.add(attendance_event)
        await db.commit()
        await db.refresh(attendance_event)
        
        action = "clocked IN" if event_type == AttendanceEventType.IN else "clocked OUT"
        message = f"You have successfully {action}!"
        
        return attendance_event, message
    
    @staticmethod
    async def get_employee_today_status(
        db: AsyncSession,
        employee_id: UUID
    ) -> dict:
        """
        Get employee's attendance status for today.
        
        Returns:
            Dictionary with today's attendance info
        """
        today_start = datetime.combine(date.today(), time.min)
        today_end = datetime.combine(date.today(), time.max)
        
        # Get today's events for employee
        result = await db.execute(
            select(AttendanceEvent)
            .where(
                AttendanceEvent.employee_id == employee_id,
                AttendanceEvent.event_timestamp >= today_start,
                AttendanceEvent.event_timestamp <= today_end
            )
            .order_by(AttendanceEvent.event_timestamp.asc())
        )
        events = list(result.scalars().all())
        
        # Get employee info
        result = await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Calculate status
        clock_in_time = None
        clock_out_time = None
        
        for event in events:
            if event.event_type == AttendanceEventType.IN and clock_in_time is None:
                clock_in_time = event.event_timestamp
            elif event.event_type == AttendanceEventType.OUT:
                clock_out_time = event.event_timestamp
        
        total_hours = None
        if clock_in_time and clock_out_time:
            diff = clock_out_time - clock_in_time
            total_hours = round(diff.total_seconds() / 3600, 2)
        
        if not clock_in_time:
            status_text = "Not Clocked In"
        elif not clock_out_time:
            status_text = "Present"
        else:
            status_text = "Completed"
        
        return {
            "employee_id": employee.id,
            "employee_name": employee.full_name,
            "clock_in_time": clock_in_time,
            "clock_out_time": clock_out_time,
            "total_hours": total_hours,
            "status": status_text
        }

