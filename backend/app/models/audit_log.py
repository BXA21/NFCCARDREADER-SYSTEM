"""
Audit log model for tracking system actions.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, JSON
from app.database import Base
from app.models.base import UUID


class AuditLog(Base):
    """
    Audit log for tracking all sensitive system actions.
    Records who did what, when, and from where.
    """
    
    __tablename__ = "audit_logs"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Actor Information
    actor_user_id = Column(UUID(), nullable=True, index=True)  # Nullable for system actions
    
    # Action Information
    action_type = Column(String(100), nullable=False, index=True)  # EMPLOYEE_CREATED, CARD_ISSUED, etc.
    entity_type = Column(String(100), nullable=False, index=True)  # Employee, Card, User, etc.
    entity_id = Column(UUID(), nullable=True, index=True)
    
    # Details
    details = Column(JSON, nullable=True)  # Flexible JSON field for additional context
    description = Column(Text, nullable=True)
    
    # Request Information
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action_type}', entity='{self.entity_type}', timestamp='{self.timestamp}')>"

