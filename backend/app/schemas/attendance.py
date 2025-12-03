"""
Pydantic schemas for Attendance events.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from app.models.attendance import AttendanceEventType, EventSource, EntrySource


class AttendanceEventBase(BaseModel):
    """Base attendance event schema."""
    card_uid: str = Field(..., description="Card UID from NFC reader")
    device_id: str = Field(..., description="Device ID of the reader")
    event_timestamp: datetime = Field(..., description="Timestamp of the event")


class AttendanceEventCreate(AttendanceEventBase):
    """Schema for creating an attendance event from reader agent."""
    event_id: Optional[UUID] = Field(None, description="Client-generated ID for idempotency")
    event_type: Optional[AttendanceEventType] = Field(None, description="Event type (auto-detected if not provided)")


class AttendanceEventInDB(BaseModel):
    """Schema for attendance event as stored in database."""
    id: UUID
    employee_id: UUID
    card_id: Optional[UUID] = None  # Nullable for manual entries
    event_type: AttendanceEventType
    event_timestamp: datetime
    device_id: str
    source: EventSource
    entry_source: EntrySource = EntrySource.NFC  # New field
    notes: Optional[str] = None  # New field
    entered_by: Optional[str] = None  # New field
    edited_at: Optional[datetime] = None  # New field
    edited_by: Optional[str] = None  # New field
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AttendanceEventResponse(AttendanceEventInDB):
    """Schema for attendance event in API responses."""
    employee_name: str
    employee_no: str
    department: Optional[str] = None  # New field for dashboard
    message: Optional[str] = None


class AttendanceEventListItem(BaseModel):
    """Schema for attendance event in list views."""
    id: UUID
    employee_name: str
    employee_no: str
    department: Optional[str] = None  # New field
    event_type: AttendanceEventType
    event_timestamp: datetime
    device_id: str
    entry_source: EntrySource = EntrySource.NFC  # New field
    notes: Optional[str] = None  # New field
    
    model_config = ConfigDict(from_attributes=True)


class AttendanceSummary(BaseModel):
    """Schema for attendance summary."""
    date: date
    present_count: int = 0
    absent_count: int = 0
    late_count: int = 0
    early_leave_count: int = 0
    total_employees: int = 0


class EmployeeAttendanceRecord(BaseModel):
    """Schema for individual employee attendance record."""
    date: date
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None
    status: str  # Present, Absent, Late, etc.
    hours_worked: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class AttendanceReportParams(BaseModel):
    """Schema for attendance report query parameters."""
    from_date: date = Field(..., description="Start date")
    to_date: date = Field(..., description="End date")
    employee_id: Optional[UUID] = Field(None, description="Filter by employee")
    department: Optional[str] = Field(None, description="Filter by department")



