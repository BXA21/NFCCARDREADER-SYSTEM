"""
Pydantic schemas for Card.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from app.models.card import CardStatus


class CardBase(BaseModel):
    """Base card schema with common fields."""
    card_uid: str = Field(..., min_length=8, max_length=50, description="Card UID in hex format")


class CardCreate(CardBase):
    """Schema for issuing a new card to an employee."""
    pass


class CardUpdate(BaseModel):
    """Schema for updating a card."""
    status: CardStatus


class CardInDB(CardBase):
    """Schema for card as stored in database."""
    id: UUID
    employee_id: UUID
    status: CardStatus
    issued_at: datetime
    revoked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CardResponse(CardInDB):
    """Schema for card in API responses."""
    employee_name: Optional[str] = None
    employee_no: Optional[str] = None


class CardListItem(BaseModel):
    """Schema for card in list views."""
    id: UUID
    card_uid: str
    status: CardStatus
    issued_at: datetime
    employee_name: str
    employee_no: str
    
    model_config = ConfigDict(from_attributes=True)



