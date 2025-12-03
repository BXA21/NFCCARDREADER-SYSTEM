"""
Attendance event model for recording clock-in/clock-out actions.
Supports both NFC and manual attendance entry.
"""

import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUID


class AttendanceEventType(str, enum.Enum):
    """Attendance event type enumeration."""
    IN = "IN"
    OUT = "OUT"


class EventSource(str, enum.Enum):
    """Event source enumeration (legacy - for backward compatibility)."""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class EntrySource(str, enum.Enum):
    """Entry source enumeration - tracks how the attendance was recorded."""
    NFC = "NFC"                       # Normal NFC card tap
    MANUAL_HR = "MANUAL_HR"           # HR manually entered
    MANUAL_EMPLOYEE = "MANUAL_EMPLOYEE"  # Employee self-service
    BULK_IMPORT = "BULK_IMPORT"       # Bulk import from CSV/Excel
    SYSTEM = "SYSTEM"                 # System-generated (corrections, etc.)


class AttendanceEvent(Base):
    """
    Attendance event representing a clock-in or clock-out action.
    Can be created via NFC card tap or manual entry.
    """
    
    __tablename__ = "attendance_events"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    employee_id = Column(UUID(), ForeignKey("employees.id"), nullable=False, index=True)
    card_id = Column(UUID(), ForeignKey("cards.id"), nullable=True)  # Nullable for manual entries
    
    # Event Information
    event_type = Column(
        SQLEnum(AttendanceEventType),
        nullable=False,
        index=True
    )
    event_timestamp = Column(DateTime, nullable=False, index=True)
    
    # Device Information
    device_id = Column(String(100), nullable=False, index=True)
    
    # Source (legacy field - kept for backward compatibility)
    source = Column(
        SQLEnum(EventSource),
        nullable=False,
        default=EventSource.ONLINE
    )
    
    # Entry Source - tracks how the attendance was recorded
    entry_source = Column(
        SQLEnum(EntrySource),
        nullable=False,
        default=EntrySource.NFC,
        index=True
    )
    
    # Manual Entry Fields
    notes = Column(Text, nullable=True)  # Reason for manual entry
    entered_by = Column(String(100), nullable=True)  # Who entered this record (for manual entries)
    
    # Edit Tracking
    edited_at = Column(DateTime, nullable=True)  # When was this record last edited
    edited_by = Column(String(100), nullable=True)  # Who edited this record
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="attendance_events")
    card = relationship("Card", back_populates="attendance_events")
    
    def __repr__(self):
        return f"<AttendanceEvent(employee_id='{self.employee_id}', type='{self.event_type.value}', source='{self.entry_source.value}', timestamp='{self.event_timestamp}')>"

