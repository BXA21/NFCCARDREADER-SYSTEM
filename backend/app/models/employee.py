"""
Employee model representing company staff members.
"""

import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUID


class EmployeeStatus(str, enum.Enum):
    """Employee status enumeration."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TERMINATED = "TERMINATED"


class Employee(Base):
    """
    Employee entity representing a company staff member.
    Each employee can have one user account for system access.
    """
    
    __tablename__ = "employees"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Basic Information
    employee_no = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=False, index=True)
    position = Column(String(100), nullable=True)  # Job title/position
    phone = Column(String(50), nullable=True)  # Contact phone number
    
    # Self-Service Authentication
    pin_hash = Column(String(255), nullable=True)  # Hashed PIN for employee self-service
    
    # Relationships
    supervisor_id = Column(UUID(), ForeignKey("employees.id"), nullable=True)
    supervisor = relationship("Employee", remote_side=[id], backref="subordinates")
    
    # Status
    status = Column(
        SQLEnum(EmployeeStatus),
        nullable=False,
        default=EmployeeStatus.ACTIVE,
        index=True
    )
    
    # Dates
    hire_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="employee", uselist=False)
    cards = relationship("Card", back_populates="employee", cascade="all, delete-orphan")
    attendance_events = relationship("AttendanceEvent", back_populates="employee")
    correction_requests = relationship("CorrectionRequest", back_populates="employee")
    employee_shifts = relationship("EmployeeShift", back_populates="employee")
    leave_records = relationship("LeaveRecord", back_populates="employee")
    
    def __repr__(self):
        return f"<Employee(employee_no='{self.employee_no}', name='{self.full_name}')>"

