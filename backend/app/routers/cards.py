"""
Card router for NFC card management operations.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.card import CardCreate, CardResponse, CardListItem
from app.schemas.common import MessageResponse
from app.services.card_service import CardService
from app.models.user import User
from app.utils.dependencies import require_hr_admin
from typing import List

router = APIRouter()


@router.post("/employees/{employee_id}/cards", response_model=CardResponse, status_code=201)
async def issue_card(
    employee_id: UUID = Path(..., description="Employee UUID"),
    card_data: CardCreate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Issue a new NFC card to an employee.
    
    **Path Parameters:**
    - employee_id: UUID of the employee
    
    **Request Body:**
    - card_uid: Card UID read from NFC reader (hex format)
    
    **Returns:**
    - Issued card details
    
    **Errors:**
    - 404: Employee not found
    - 400: Card UID already exists or employee already has active card
    
    **Authorization:**
    - HR_ADMIN only
    
    **Business Rules:**
    - Card UID must be unique across the system
    - Employee can only have one ACTIVE card at a time
    - Employee must be ACTIVE to receive a card
    """
    card = await CardService.issue_card(
        db=db,
        employee_id=employee_id,
        card_uid=card_data.card_uid
    )
    
    # Build response
    response = CardResponse(
        **card.__dict__,
        employee_name=card.employee.full_name,
        employee_no=card.employee.employee_no
    )
    
    return response


@router.get("/employees/{employee_id}/cards", response_model=List[CardListItem])
async def get_employee_cards(
    employee_id: UUID = Path(..., description="Employee UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Get all cards for an employee (including revoked/lost cards).
    
    **Path Parameters:**
    - employee_id: UUID of the employee
    
    **Returns:**
    - List of all cards for the employee
    
    **Authorization:**
    - HR_ADMIN only
    """
    cards = await CardService.get_employee_cards(db, employee_id)
    
    # Build response
    items = [
        CardListItem(
            id=card.id,
            card_uid=card.card_uid,
            status=card.status,
            issued_at=card.issued_at,
            employee_name=card.employee.full_name,
            employee_no=card.employee.employee_no
        )
        for card in cards
    ]
    
    return items


@router.put("/cards/{card_id}/revoke", response_model=CardResponse)
async def revoke_card(
    card_id: UUID = Path(..., description="Card UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Revoke a card (e.g., when issuing a replacement).
    
    **Path Parameters:**
    - card_id: UUID of the card
    
    **Returns:**
    - Updated card details
    
    **Errors:**
    - 404: Card not found
    - 400: Card already revoked or lost
    
    **Authorization:**
    - HR_ADMIN only
    
    **Business Rules:**
    - Only ACTIVE cards can be revoked
    - Revoked cards cannot be reactivated
    - After revoking, a new card can be issued to the employee
    """
    card = await CardService.revoke_card(db, card_id)
    
    # Build response
    response = CardResponse(
        **card.__dict__,
        employee_name=card.employee.full_name,
        employee_no=card.employee.employee_no
    )
    
    return response


@router.put("/cards/{card_id}/mark-lost", response_model=CardResponse)
async def mark_card_lost(
    card_id: UUID = Path(..., description="Card UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Mark a card as lost.
    
    **Path Parameters:**
    - card_id: UUID of the card
    
    **Returns:**
    - Updated card details
    
    **Errors:**
    - 404: Card not found
    - 400: Card already revoked or lost
    
    **Authorization:**
    - HR_ADMIN only
    
    **Business Rules:**
    - Only ACTIVE cards can be marked as lost
    - Lost cards cannot be reactivated
    - After marking as lost, a new card can be issued to the employee
    """
    card = await CardService.mark_card_lost(db, card_id)
    
    # Build response
    response = CardResponse(
        **card.__dict__,
        employee_name=card.employee.full_name,
        employee_no=card.employee.employee_no
    )
    
    return response



