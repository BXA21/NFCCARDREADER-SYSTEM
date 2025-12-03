"""
Authentication service containing business logic for authentication operations.
"""

from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.models.employee import Employee
from app.utils.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)


class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            db: Database session
            username: Username
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Get user with employee relationship loaded
        result = await db.execute(
            select(User)
            .where(User.username == username)
            .options(selectinload(User.employee))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    async def create_tokens(user: User) -> Tuple[str, str]:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user: User object
            
        Returns:
            Tuple of (access_token, refresh_token)
        """
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return access_token, refresh_token
    
    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str
    ) -> Tuple[str, str]:
        """
        Refresh access token using a refresh token.
        
        Args:
            db: Database session
            refresh_token: Refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify token type
        if not verify_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        return await AuthService.create_tokens(user)
    
    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> None:
        """
        Update the last login timestamp for a user.
        
        Args:
            db: Database session
            user: User object
        """
        user.last_login_at = datetime.utcnow()
        await db.commit()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        password: str,
        employee_id: str,
        role: str
    ) -> User:
        """
        Create a new user account.
        
        Args:
            db: Database session
            username: Username
            password: Plain text password
            employee_id: Employee ID
            role: User role
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If username already exists or employee not found
        """
        # Check if username exists
        result = await db.execute(
            select(User).where(User.username == username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if employee exists
        result = await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = result.scalar_one_or_none()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        # Check if employee already has a user account
        result = await db.execute(
            select(User).where(User.employee_id == employee_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee already has a user account"
            )
        
        # Create user
        user = User(
            username=username,
            password_hash=hash_password(password),
            employee_id=employee_id,
            role=role,
            is_active=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user


# Import for eager loading
from sqlalchemy.orm import selectinload



