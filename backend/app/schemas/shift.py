"""
Pydantic schemas for Shift and Employee Shift assignments.
"""

from datetime import datetime, time, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID


class ShiftBase(BaseModel):
    """Base shift schema with common fields."""
    name: str = Field(..., min_length=2, max_length=100)
    start_time: time
    end_time: time
    grace_minutes: int = Field(15, ge=0, le=60, description="Late tolerance in minutes")


class ShiftCreate(ShiftBase):
    """Schema for creating a new shift."""
    is_active: bool = True
    
    @field_validator('end_time')
    @classmethod
    def validate_times(cls, v, info):
        """Validate that times are sensible (allow overnight shifts)."""
        start_time = info.data.get('start_time')
        if start_time and v == start_time:
            raise ValueError('End time must be different from start time')
        return v


class ShiftUpdate(BaseModel):
    """Schema for updating a shift."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    grace_minutes: Optional[int] = Field(None, ge=0, le=60)
    is_active: Optional[bool] = None


class ShiftInDB(ShiftBase):
    """Schema for shift as stored in database."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ShiftResponse(ShiftInDB):
    """Schema for shift in API responses."""
    employee_count: int = 0


class EmployeeShiftBase(BaseModel):
    """Base employee shift assignment schema."""
    shift_id: UUID
    effective_from: date


class EmployeeShiftCreate(EmployeeShiftBase):
    """Schema for assigning a shift to an employee."""
    effective_to: Optional[date] = None
    
    @field_validator('effective_to')
    @classmethod
    def validate_dates(cls, v, info):
        """Validate that effective_to is after effective_from."""
        effective_from = info.data.get('effective_from')
        if v and effective_from and v <= effective_from:
            raise ValueError('effective_to must be after effective_from')
        return v


class EmployeeShiftUpdate(BaseModel):
    """Schema for updating an employee shift assignment."""
    effective_to: Optional[date] = None


class EmployeeShiftInDB(EmployeeShiftBase):
    """Schema for employee shift as stored in database."""
    id: UUID
    employee_id: UUID
    effective_to: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeShiftResponse(EmployeeShiftInDB):
    """Schema for employee shift in API responses."""
    shift_name: str
    employee_name: str



