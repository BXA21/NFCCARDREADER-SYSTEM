"""
Common Pydantic schemas used across the application.
"""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field


# Generic type for paginated responses
T = TypeVar('T')


class PaginationParams(BaseModel):
    """
    Query parameters for pagination.
    """
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """
    Simple message response.
    """
    message: str
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """
    Error response schema.
    """
    error: str
    detail: Optional[str] = None
    
    class Config:
        from_attributes = True



