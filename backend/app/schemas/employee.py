"""
Pydantic schemas for Employee.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from app.models.employee import EmployeeStatus


class EmployeeBase(BaseModel):
    """Base employee schema with common fields."""
    employee_no: str = Field(..., pattern=r'^EMP-[A-Z0-9-]{3,}$', description="Employee number (e.g., EMP-001, EMP-NFC-001)")
    full_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    department: str = Field(..., min_length=2, max_length=100)
    supervisor_id: Optional[UUID] = None


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""
    hire_date: date
    status: EmployeeStatus = EmployeeStatus.ACTIVE


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    supervisor_id: Optional[UUID] = None
    status: Optional[EmployeeStatus] = None


class EmployeeInDB(EmployeeBase):
    """Schema for employee as stored in database."""
    id: UUID
    status: EmployeeStatus
    hire_date: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeResponse(EmployeeInDB):
    """Schema for employee in API responses."""
    has_active_card: bool = False
    supervisor_name: Optional[str] = None


class EmployeeListItem(BaseModel):
    """Schema for employee in list views."""
    id: UUID
    employee_no: str
    full_name: str
    email: str
    department: str
    status: EmployeeStatus
    has_active_card: bool = False
    
    model_config = ConfigDict(from_attributes=True)



