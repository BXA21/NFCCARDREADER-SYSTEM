"""
Shift and employee shift assignment models.
"""

import uuid
from datetime import datetime, time, date
from sqlalchemy import Column, String, DateTime, Time, Date, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUID


class Shift(Base):
    """
    Shift definition representing a work schedule.
    Examples: Morning (8:00-16:00), Evening (16:00-00:00), Night (00:00-08:00)
    """
    
    __tablename__ = "shifts"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Shift Information
    name = Column(String(100), nullable=False, unique=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    grace_minutes = Column(Integer, nullable=False, default=15)  # Late tolerance
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee_shifts = relationship("EmployeeShift", back_populates="shift")
    
    def __repr__(self):
        return f"<Shift(name='{self.name}', start='{self.start_time}', end='{self.end_time}')>"


class EmployeeShift(Base):
    """
    Employee shift assignment linking employees to their work schedules.
    Supports time-based assignments (effective_from, effective_to).
    """
    
    __tablename__ = "employee_shifts"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    shift_id = Column(UUID(), ForeignKey("shifts.id"), nullable=False, index=True)
    employee_id = Column(UUID(), ForeignKey("employees.id"), nullable=False, index=True)
    
    # Effective Period
    effective_from = Column(Date, nullable=False, index=True)
    effective_to = Column(Date, nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shift = relationship("Shift", back_populates="employee_shifts")
    employee = relationship("Employee", back_populates="employee_shifts")
    
    def __repr__(self):
        return f"<EmployeeShift(employee_id='{self.employee_id}', shift_id='{self.shift_id}', from='{self.effective_from}')>"

