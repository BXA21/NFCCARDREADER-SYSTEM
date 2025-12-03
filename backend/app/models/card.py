"""
NFC Card model for employee identification.
"""

import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUID


class CardStatus(str, enum.Enum):
    """Card status enumeration."""
    ACTIVE = "ACTIVE"
    LOST = "LOST"
    REVOKED = "REVOKED"


class Card(Base):
    """
    NFC Card entity linked to an employee.
    Each card has a unique UID read from the physical NFC card.
    """
    
    __tablename__ = "cards"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Card Information
    card_uid = Column(String(50), unique=True, nullable=False, index=True)
    
    # Foreign Keys
    employee_id = Column(UUID(), ForeignKey("employees.id"), nullable=False)
    
    # Status
    status = Column(
        SQLEnum(CardStatus),
        nullable=False,
        default=CardStatus.ACTIVE,
        index=True
    )
    
    # Timestamps
    issued_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="cards")
    attendance_events = relationship("AttendanceEvent", back_populates="card")
    
    def __repr__(self):
        return f"<Card(card_uid='{self.card_uid}', status='{self.status.value}')>"

