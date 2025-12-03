"""
Correction request model for attendance corrections.
"""

import enum
import uuid
from datetime import datetime, date, time
from sqlalchemy import Column, String, DateTime, Date, Time, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUID


class CorrectionStatus(str, enum.Enum):
    """Correction request status enumeration."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CorrectionRequest(Base):
    """
    Correction request for attendance records.
    Employees can submit requests to correct missing or incorrect attendance.
    """
    
    __tablename__ = "correction_requests"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    employee_id = Column(UUID(), ForeignKey("employees.id"), nullable=False, index=True)
    requested_by_user_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    
    # Request Details
    date = Column(Date, nullable=False, index=True)
    requested_event_type = Column(String(10), nullable=False)  # IN or OUT
    requested_time = Column(Time, nullable=False)
    reason = Column(Text, nullable=False)
    
    # Status
    status = Column(
        SQLEnum(CorrectionStatus),
        nullable=False,
        default=CorrectionStatus.PENDING,
        index=True
    )
    
    # Approval Information
    approver_id = Column(UUID(), ForeignKey("users.id"), nullable=True)
    approver_comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="correction_requests")
    approver = relationship(
        "User",
        foreign_keys=[approver_id],
        back_populates="correction_approvals"
    )
    
    def __repr__(self):
        return f"<CorrectionRequest(employee_id='{self.employee_id}', date='{self.date}', status='{self.status.value}')>"

