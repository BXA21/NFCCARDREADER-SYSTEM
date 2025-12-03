"""
Pydantic schemas for Manual Operations.
"""

from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from app.models.attendance import AttendanceEventType, EntrySource
from app.models.leave import LeaveStatus


# ============ Manual Attendance Schemas ============

class ManualAttendanceCreate(BaseModel):
    """Schema for creating a manual attendance entry."""
    employee_id: UUID = Field(..., description="Employee UUID")
    event_type: AttendanceEventType = Field(..., description="IN or OUT")
    event_date: date = Field(..., description="Date of the attendance event")
    event_time: time = Field(..., description="Time of the attendance event")
    notes: Optional[str] = Field(None, max_length=500, description="Reason for manual entry")


class ManualAttendanceResponse(BaseModel):
    """Schema for manual attendance response."""
    id: UUID
    employee_id: UUID
    employee_name: str
    employee_no: str
    event_type: AttendanceEventType
    event_timestamp: datetime
    entry_source: EntrySource
    notes: Optional[str] = None
    entered_by: Optional[str] = None
    message: str
    
    model_config = ConfigDict(from_attributes=True)


class AttendanceEditRequest(BaseModel):
    """Schema for editing an attendance record."""
    event_time: Optional[time] = Field(None, description="New time for the event")
    event_date: Optional[date] = Field(None, description="New date for the event")
    event_type: Optional[AttendanceEventType] = Field(None, description="Change event type")
    notes: Optional[str] = Field(None, max_length=500, description="Edit notes/reason")


class AttendanceDeleteRequest(BaseModel):
    """Schema for deleting an attendance record."""
    reason: str = Field(..., min_length=5, max_length=500, description="Reason for deletion")


class BulkAttendanceCreate(BaseModel):
    """Schema for bulk attendance entry."""
    employee_ids: List[UUID] = Field(..., description="List of employee UUIDs")
    event_type: AttendanceEventType = Field(..., description="IN or OUT")
    event_date: date = Field(..., description="Date of the attendance event")
    event_time: time = Field(..., description="Time of the attendance event")
    notes: Optional[str] = Field(None, max_length=500, description="Reason for bulk entry")


class BulkAttendanceResponse(BaseModel):
    """Schema for bulk attendance response."""
    success_count: int
    failed_count: int
    failed_employees: List[str] = []
    message: str


# ============ Leave Management Schemas ============

class LeaveTypeResponse(BaseModel):
    """Schema for leave type in responses."""
    id: UUID
    name: str
    description: Optional[str] = None
    is_paid: bool
    max_days_per_year: Optional[int] = None
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class LeaveRecordCreate(BaseModel):
    """Schema for creating a leave record."""
    employee_id: UUID = Field(..., description="Employee UUID")
    leave_type_id: UUID = Field(..., description="Leave type UUID")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    notes: Optional[str] = Field(None, max_length=500, description="Leave notes")
    status: LeaveStatus = Field(LeaveStatus.APPROVED, description="Leave status")


class LeaveRecordUpdate(BaseModel):
    """Schema for updating a leave record."""
    leave_type_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)
    status: Optional[LeaveStatus] = None


class LeaveRecordResponse(BaseModel):
    """Schema for leave record in responses."""
    id: UUID
    employee_id: UUID
    employee_name: str
    employee_no: str
    leave_type_id: UUID
    leave_type_name: str
    start_date: date
    end_date: date
    days_count: int
    notes: Optional[str] = None
    status: LeaveStatus
    entered_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LeaveRecordListItem(BaseModel):
    """Schema for leave record in list views."""
    id: UUID
    employee_name: str
    employee_no: str
    leave_type_name: str
    start_date: date
    end_date: date
    days_count: int
    status: LeaveStatus
    
    model_config = ConfigDict(from_attributes=True)


# ============ Employee Self-Service Schemas ============

class EmployeeSelfClockRequest(BaseModel):
    """Schema for employee self-service clock in/out."""
    employee_id: str = Field(..., description="Employee number or ID")
    pin: str = Field(..., min_length=4, max_length=6, description="Employee PIN")
    event_type: AttendanceEventType = Field(..., description="IN or OUT")
    reason: str = Field(..., description="Reason for manual clock")


class EmployeeSelfClockResponse(BaseModel):
    """Schema for employee self-service response."""
    success: bool
    employee_name: str
    event_type: AttendanceEventType
    timestamp: datetime
    message: str


class EmployeePinSetRequest(BaseModel):
    """Schema for setting employee PIN."""
    employee_id: UUID = Field(..., description="Employee UUID")
    pin: str = Field(..., min_length=4, max_length=6, description="4-6 digit PIN")


class EmployeeTodayStatus(BaseModel):
    """Schema for employee's today attendance status."""
    employee_id: UUID
    employee_name: str
    clock_in_time: Optional[datetime] = None
    clock_out_time: Optional[datetime] = None
    total_hours: Optional[float] = None
    status: str  # "Present", "Not Clocked In", "Left Early", etc.


# ============ Attendance Record with Source ============

class AttendanceRecordWithSource(BaseModel):
    """Schema for attendance record with entry source information."""
    id: UUID
    employee_id: UUID
    employee_name: str
    employee_no: str
    department: str
    event_type: AttendanceEventType
    event_timestamp: datetime
    device_id: str
    entry_source: EntrySource
    notes: Optional[str] = None
    entered_by: Optional[str] = None
    edited_at: Optional[datetime] = None
    edited_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

