"""
Authentication router for login, logout, and token refresh endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    UserResponse
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate a user and return access and refresh tokens.
    
    **Request Body:**
    - username: User's username
    - password: User's password
    
    **Response:**
    - access_token: JWT access token (expires in 15 minutes)
    - refresh_token: JWT refresh token (expires in 7 days)
    - token_type: "bearer"
    - user: User information
    
    **Errors:**
    - 401: Invalid credentials
    """
    # Authenticate user
    user = await AuthService.authenticate_user(db, request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token, refresh_token = await AuthService.create_tokens(user)
    
    # Update last login time
    await AuthService.update_last_login(db, user)
    
    # Prepare user response
    user_response = UserResponse.model_validate(user)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh an access token using a refresh token.
    
    **Request Body:**
    - refresh_token: Valid JWT refresh token
    
    **Response:**
    - access_token: New JWT access token
    - refresh_token: New JWT refresh token
    - token_type: "bearer"
    
    **Errors:**
    - 401: Invalid or expired refresh token
    """
    # Refresh tokens
    access_token, new_refresh_token = await AuthService.refresh_access_token(
        db,
        request.refresh_token
    )
    
    return RefreshTokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(request: LogoutRequest):
    """
    Logout a user by invalidating their refresh token.
    
    Note: In a production system, you would want to maintain a blacklist
    of invalidated tokens in Redis or similar. For now, this is a placeholder.
    
    **Request Body:**
    - refresh_token: Refresh token to invalidate
    
    **Response:**
    - message: Success message
    """
    # TODO: In production, add token to blacklist (Redis)
    # For now, just return success
    return MessageResponse(message="Logged out successfully")



