"""
User model for system authentication and authorization.
"""

import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUID


class UserRole(str, enum.Enum):
    """User role enumeration for authorization."""
    EMPLOYEE = "EMPLOYEE"
    SUPERVISOR = "SUPERVISOR"
    HR_ADMIN = "HR_ADMIN"


class User(Base):
    """
    User entity for system access and authentication.
    Each user is linked to an employee record.
    """
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Authorization
    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.EMPLOYEE,
        index=True
    )
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Foreign Keys
    employee_id = Column(UUID(), ForeignKey("employees.id"), nullable=False, unique=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="user")
    correction_approvals = relationship(
        "CorrectionRequest",
        foreign_keys="CorrectionRequest.approver_id",
        back_populates="approver"
    )
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role.value}')>"

