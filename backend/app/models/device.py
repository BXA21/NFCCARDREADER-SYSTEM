"""
Device model for NFC readers.
"""

import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from app.database import Base
from app.models.base import UUID


class DeviceStatus(str, enum.Enum):
    """Device status enumeration."""
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"


class Device(Base):
    """
    Device entity representing an NFC card reader.
    Each reader has a unique device_id and API key for authentication.
    """
    
    __tablename__ = "devices"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Device Information
    device_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    site_id = Column(String(100), nullable=True, index=True)
    
    # Authentication
    api_key = Column(String(255), nullable=False, unique=True)
    
    # Status
    status = Column(
        SQLEnum(DeviceStatus),
        nullable=False,
        default=DeviceStatus.OFFLINE,
        index=True
    )
    
    # Timestamps
    last_seen_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Device(device_id='{self.device_id}', name='{self.name}', status='{self.status.value}')>"

