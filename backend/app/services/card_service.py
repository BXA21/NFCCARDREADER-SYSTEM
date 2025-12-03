"""
Card service containing business logic for card operations.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.card import Card, CardStatus
from app.models.employee import Employee, EmployeeStatus


class CardService:
    """Service class for NFC card operations."""
    
    @staticmethod
    async def get_card_by_id(
        db: AsyncSession,
        card_id: UUID
    ) -> Optional[Card]:
        """
        Get a card by ID.
        
        Args:
            db: Database session
            card_id: Card UUID
            
        Returns:
            Card object or None if not found
        """
        result = await db.execute(
            select(Card)
            .where(Card.id == card_id)
            .options(selectinload(Card.employee))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_card_by_uid(
        db: AsyncSession,
        card_uid: str
    ) -> Optional[Card]:
        """
        Get a card by UID.
        
        Args:
            db: Database session
            card_uid: Card UID
            
        Returns:
            Card object or None if not found
        """
        # Normalize card UID (uppercase, no spaces or dashes)
        normalized_uid = card_uid.upper().replace(" ", "").replace("-", "").replace(":", "")
        
        result = await db.execute(
            select(Card)
            .where(Card.card_uid == normalized_uid)
            .options(selectinload(Card.employee))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_employee_cards(
        db: AsyncSession,
        employee_id: UUID
    ) -> List[Card]:
        """
        Get all cards for an employee.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            
        Returns:
            List of cards
        """
        result = await db.execute(
            select(Card)
            .where(Card.employee_id == employee_id)
            .order_by(Card.created_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def issue_card(
        db: AsyncSession,
        employee_id: UUID,
        card_uid: str
    ) -> Card:
        """
        Issue a new NFC card to an employee.
        
        Args:
            db: Database session
            employee_id: Employee UUID
            card_uid: Card UID from NFC reader
            
        Returns:
            Created card object
            
        Raises:
            HTTPException: If employee not found, card already exists, or employee already has active card
        """
        # Normalize card UID
        normalized_uid = card_uid.upper().replace(" ", "").replace("-", "").replace(":", "")
        
        # Check if employee exists and is active
        result = await db.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = result.scalar_one_or_none()
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        if employee.status != EmployeeStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot issue card to inactive employee"
            )
        
        # Check if card UID already exists
        existing_card = await CardService.get_card_by_uid(db, normalized_uid)
        if existing_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Card with UID {normalized_uid} already exists"
            )
        
        # Check if employee already has an active card
        result = await db.execute(
            select(Card).where(
                Card.employee_id == employee_id,
                Card.status == CardStatus.ACTIVE
            )
        )
        existing_active_card = result.scalar_one_or_none()
        
        if existing_active_card:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee already has an active card. Please revoke it first."
            )
        
        # Create card
        card = Card(
            card_uid=normalized_uid,
            employee_id=employee_id,
            status=CardStatus.ACTIVE,
            issued_at=datetime.utcnow()
        )
        
        db.add(card)
        await db.commit()
        await db.refresh(card)
        
        # Load employee relationship
        await db.refresh(card, ["employee"])
        
        return card
    
    @staticmethod
    async def revoke_card(
        db: AsyncSession,
        card_id: UUID,
        reason: Optional[str] = None
    ) -> Card:
        """
        Revoke a card.
        
        Args:
            db: Database session
            card_id: Card UUID
            reason: Optional reason for revocation
            
        Returns:
            Updated card object
            
        Raises:
            HTTPException: If card not found or already revoked
        """
        card = await CardService.get_card_by_id(db, card_id)
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        if card.status != CardStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Card is already {card.status.value.lower()}"
            )
        
        # Revoke card
        card.status = CardStatus.REVOKED
        card.revoked_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(card)
        
        return card
    
    @staticmethod
    async def mark_card_lost(
        db: AsyncSession,
        card_id: UUID
    ) -> Card:
        """
        Mark a card as lost.
        
        Args:
            db: Database session
            card_id: Card UUID
            
        Returns:
            Updated card object
            
        Raises:
            HTTPException: If card not found or not active
        """
        card = await CardService.get_card_by_id(db, card_id)
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        if card.status != CardStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Card is already {card.status.value.lower()}"
            )
        
        # Mark as lost
        card.status = CardStatus.LOST
        card.revoked_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(card)
        
        return card
    
    @staticmethod
    async def validate_card_for_attendance(
        db: AsyncSession,
        card_uid: str
    ) -> tuple[Card, Employee]:
        """
        Validate a card for attendance recording.
        Checks if card is active and employee is active.
        
        Args:
            db: Database session
            card_uid: Card UID
            
        Returns:
            Tuple of (card, employee)
            
        Raises:
            HTTPException: If card not found, not active, or employee not active
        """
        card = await CardService.get_card_by_uid(db, card_uid)
        
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found"
            )
        
        if card.status != CardStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Card is {card.status.value.lower()} and cannot be used"
            )
        
        if card.employee.status != EmployeeStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee is not active"
            )
        
        return card, card.employee



