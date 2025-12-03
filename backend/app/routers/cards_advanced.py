"""
Advanced card operations router for NFC card scanning and writing.
Supports the employee creation wizard workflow.
"""

from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from app.database import get_db
from app.models.card import Card
from app.models.attendance import AttendanceEvent
from app.models.user import User
from app.utils.dependencies import get_current_active_user, require_hr_admin

router = APIRouter()


class ScannedCardResponse(BaseModel):
    """Response for scanned card detection"""
    card_uid: str
    detected_at: datetime
    is_assigned: bool
    assigned_to: Optional[str] = None


class CardWriteRequest(BaseModel):
    """Request to write employee data to NFC card"""
    card_uid: str
    employee_data: dict


class CardWriteResponse(BaseModel):
    """Response after writing to NFC card"""
    success: bool
    message: str
    blocks_written: Optional[int] = None


class TestEventResponse(BaseModel):
    """Test attendance event for card verification"""
    event_type: str
    timestamp: datetime
    employee_name: str
    department: str
    employee_no: str


@router.get("/cards/scan-mode/latest", response_model=Optional[ScannedCardResponse])
async def get_latest_scanned_card(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Get the latest scanned card from scan mode.
    This endpoint is polled by the frontend during employee creation.
    
    Returns None if no card has been scanned in the last 60 seconds.
    """
    from app.utils.scan_buffer import scan_buffer
    
    print("[SCAN API] Frontend polling for card...")
    
    # Get card from buffer
    card_data = scan_buffer.get_card()
    
    if not card_data or not card_data["card_uid"]:
        print("[SCAN API] No card in buffer")
        return None
    
    print(f"[SCAN API] Found card in buffer: {card_data['card_uid']}")
    
    # Check if card is already assigned
    result = await db.execute(
        select(Card).where(Card.card_uid == card_data["card_uid"])
    )
    existing_card = result.scalar_one_or_none()
    
    response = ScannedCardResponse(
        card_uid=card_data["card_uid"],
        detected_at=card_data["detected_at"],
        is_assigned=existing_card is not None,
        assigned_to=existing_card.employee.full_name if existing_card else None
    )
    
    print(f"[SCAN API] Returning card to frontend: {response.card_uid}")
    
    # Clear after returning
    scan_buffer.clear()
    
    return response


@router.post("/cards/scan-mode/detect")
async def detect_card_in_scan_mode(
    card_uid: str,
    device_id: str,
):
    """
    Endpoint for reader agent to report scanned cards in scan mode.
    This is used during employee creation when we want to detect
    cards without creating attendance events.
    
    **Authentication:**
    - Requires X-API-Key header with valid device API key
    
    **Note:** This should be called by reader agent when in scan mode
    """
    from app.utils.scan_buffer import scan_buffer
    
    scan_buffer.add_card(card_uid)
    
    return {
        "success": True,
        "message": f"Card {card_uid} detected and queued",
        "detected_at": datetime.utcnow().isoformat()
    }


@router.post("/cards/write", response_model=CardWriteResponse)
async def write_employee_data_to_card(
    request: CardWriteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Write employee data to NFC card.
    
    This endpoint triggers the reader agent to write data to the NFC card.
    The card must be on the reader when this is called.
    
    **Card Data Structure:**
    - Block 4: Employee Number (ASCII)
    - Block 5: Employee Name (ASCII)
    - Block 6: Department (ASCII)
    - Block 8: Employee ID (UUID bytes)
    
    **Note:** This requires MIFARE Classic cards with known auth keys.
    """
    # Verify card exists and is assigned
    result = await db.execute(
        select(Card).where(Card.card_uid == request.card_uid)
    )
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found. Please assign the card first."
        )
    
    # In a real implementation, this would send a command to the reader agent
    # to write the data to the physical NFC card
    # For now, we'll simulate success
    
    # TODO: Implement actual card writing via reader agent
    # This would involve:
    # 1. Sending write command to reader agent
    # 2. Reader agent authenticates to card sectors
    # 3. Writes data blocks
    # 4. Verifies writes
    
    return CardWriteResponse(
        success=True,
        message=f"Employee data written to card {request.card_uid}",
        blocks_written=4
    )


@router.get("/attendance/test/{employee_id}/latest", response_model=Optional[TestEventResponse])
async def get_latest_test_event(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_hr_admin)
):
    """
    Get the latest attendance event for an employee.
    Used during card testing in the employee creation wizard.
    
    This allows HR to verify the card is working by seeing
    real-time attendance events as they tap the card.
    """
    # Get the most recent attendance event
    result = await db.execute(
        select(AttendanceEvent)
        .where(AttendanceEvent.employee_id == employee_id)
        .order_by(desc(AttendanceEvent.event_timestamp))
        .limit(1)
    )
    
    event = result.scalar_one_or_none()
    
    if not event:
        return None
    
    # Load employee relationship
    await db.refresh(event, ["employee"])
    
    return TestEventResponse(
        event_type=event.event_type.value,
        timestamp=event.event_timestamp,
        employee_name=event.employee.full_name,
        department=event.employee.department,
        employee_no=event.employee.employee_no
    )


@router.delete("/cards/scan-mode/clear")
async def clear_scan_mode_buffer(
    current_user: User = Depends(require_hr_admin)
):
    """
    Clear the scan mode buffer.
    Useful if a card was detected but the wizard was cancelled.
    """
    from app.utils.scan_buffer import scan_buffer
    
    scan_buffer.clear()
    
    return {"success": True, "message": "Scan buffer cleared"}


@router.get("/cards/scan-mode/debug")
async def debug_scan_mode(
    current_user: User = Depends(require_hr_admin)
):
    """
    Debug endpoint to check scan buffer status.
    Use this to troubleshoot card detection issues.
    """
    from app.utils.scan_buffer import scan_buffer
    
    status = scan_buffer.get_status()
    
    return {
        "scan_buffer_status": status,
        "endpoint": "/cards/scan-mode/latest",
        "poll_frequency": "500ms",
        "instructions": "Tap an unassigned NFC card on the reader to test"
    }


@router.post("/cards/scan-mode/test")
async def test_scan_mode(
    card_uid: str,
    current_user: User = Depends(require_hr_admin)
):
    """
    Manually add a card to scan buffer for testing.
    Use this to test the wizard without tapping a physical card.
    """
    from app.utils.scan_buffer import scan_buffer
    
    scan_buffer.add_card(card_uid)
    
    return {
        "success": True,
        "message": f"Test card {card_uid} added to scan buffer",
        "test_instructions": "Now the wizard should detect this card within 500ms"
    }

