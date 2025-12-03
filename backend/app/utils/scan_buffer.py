"""
Shared scan buffer for card detection in employee creation wizard.
Uses a simple in-memory store (would be Redis in production).
"""

from datetime import datetime
from typing import Optional, Dict

class ScanBuffer:
    """Singleton scan buffer for card detection"""
    _instance = None
    _buffer: Dict = {"card_uid": None, "detected_at": None}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScanBuffer, cls).__new__(cls)
        return cls._instance
    
    def add_card(self, card_uid: str) -> None:
        """Add a card to the scan buffer"""
        self._buffer["card_uid"] = card_uid
        self._buffer["detected_at"] = datetime.utcnow()
        print(f"[SCAN BUFFER] Card added: {card_uid} at {self._buffer['detected_at']}")
    
    def get_card(self) -> Optional[Dict]:
        """Get the card from scan buffer"""
        if not self._buffer["card_uid"]:
            return None
        
        # Check if card is still fresh (within 60 seconds)
        if self._buffer["detected_at"]:
            time_diff = (datetime.utcnow() - self._buffer["detected_at"]).total_seconds()
            if time_diff > 60:
                print(f"[SCAN BUFFER] Card expired (age: {time_diff}s)")
                self.clear()
                return None
        
        print(f"[SCAN BUFFER] Card retrieved: {self._buffer['card_uid']}")
        return self._buffer.copy()
    
    def clear(self) -> None:
        """Clear the scan buffer"""
        print(f"[SCAN BUFFER] Cleared")
        self._buffer = {"card_uid": None, "detected_at": None}
    
    def get_status(self) -> Dict:
        """Get buffer status for debugging"""
        if self._buffer["card_uid"]:
            age = (datetime.utcnow() - self._buffer["detected_at"]).total_seconds() if self._buffer["detected_at"] else 0
            return {
                "has_card": True,
                "card_uid": self._buffer["card_uid"],
                "detected_at": self._buffer["detected_at"].isoformat() if self._buffer["detected_at"] else None,
                "age_seconds": age
            }
        return {"has_card": False, "card_uid": None, "detected_at": None, "age_seconds": 0}

# Global instance
scan_buffer = ScanBuffer()

