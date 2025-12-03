"""
Leave management models for tracking employee leave records.
"""

import enum
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Date, Text, Boolean, Integer, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUID


class LeaveStatus(str, enum.Enum):
    """Leave record status enumeration."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class LeaveType(Base):
    """
    Leave type definition.
    Examples: Annual Leave, Sick Leave, Personal Leave, etc.
    """
    
    __tablename__ = "leave_types"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Leave Type Information
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_paid = Column(Boolean, nullable=False, default=True)
    max_days_per_year = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leave_records = relationship("LeaveRecord", back_populates="leave_type")
    
    def __repr__(self):
        return f"<LeaveType(name='{self.name}', is_paid={self.is_paid})>"


class LeaveRecord(Base):
    """
    Leave record for tracking employee leaves.
    Can be created by HR manually or through leave request approval.
    """
    
    __tablename__ = "leave_records"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    employee_id = Column(UUID(), ForeignKey("employees.id"), nullable=False, index=True)
    leave_type_id = Column(UUID(), ForeignKey("leave_types.id"), nullable=False)
    
    # Leave Period
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    
    # Details
    notes = Column(Text, nullable=True)
    
    # Status
    status = Column(
        SQLEnum(LeaveStatus),
        nullable=False,
        default=LeaveStatus.APPROVED,
        index=True
    )
    
    # Tracking
    entered_by = Column(String(100), nullable=True)  # Who created this record
    approved_by = Column(String(100), nullable=True)  # Who approved this leave
    approved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="leave_records")
    leave_type = relationship("LeaveType", back_populates="leave_records")
    
    @property
    def days_count(self) -> int:
        """Calculate the number of days for this leave."""
        return (self.end_date - self.start_date).days + 1
    
    def __repr__(self):
        return f"<LeaveRecord(employee_id='{self.employee_id}', type='{self.leave_type_id}', from='{self.start_date}', to='{self.end_date}')>"

