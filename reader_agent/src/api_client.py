"""
API client for communicating with the backend server.
"""

import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class APIClient:
    """Client for backend API communication."""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 10):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the API
            api_key: Device API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Create HTTP client
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
        )
    
    def record_attendance(
        self,
        card_uid: str,
        device_id: str,
        event_timestamp: Optional[datetime] = None,
        event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send attendance event to backend.
        
        Args:
            card_uid: Card UID from NFC reader
            device_id: Device ID
            event_timestamp: Event timestamp (defaults to now)
            event_id: Optional event ID for idempotency
            
        Returns:
            Response data from server
            
        Raises:
            Exception: If request fails
        """
        if not event_timestamp:
            event_timestamp = datetime.utcnow()
        
        if not event_id:
            event_id = str(uuid.uuid4())
        
        # Prepare request payload
        payload = {
            "card_uid": card_uid,
            "device_id": device_id,
            "event_timestamp": event_timestamp.isoformat() + 'Z',
            "event_id": event_id
        }
        
        self.logger.debug(f"Sending attendance event: {payload}")
        
        try:
            response = self.client.post(
                "/attendance-events",
                json=payload
            )
            
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Attendance recorded successfully: {data.get('message')}")
            
            return data
            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get('detail', str(e))
            except:
                error_detail = str(e)
            
            self.logger.error(f"API error ({e.response.status_code}): {error_detail}")
            raise Exception(f"API error: {error_detail}")
            
        except httpx.RequestError as e:
            self.logger.error(f"Request error: {e}")
            raise Exception(f"Request error: {str(e)}")
    
    def health_check(self) -> bool:
        """
        Check if API is reachable.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Try to hit the health endpoint (without auth)
            response = httpx.get(
                f"{self.base_url.replace('/api/v1', '')}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()



