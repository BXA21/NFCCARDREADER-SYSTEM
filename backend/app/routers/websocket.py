"""
WebSocket router for real-time attendance updates.
Allows the frontend dashboard to receive instant notifications when cards are tapped.
"""

import asyncio
import json
from datetime import datetime
from typing import Set, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    Supports multiple clients subscribing to attendance events.
    """
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        async with self._lock:
            self.active_connections.discard(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message, default=str)
        
        # Send to all connections, handling failures gracefully
        disconnected = set()
        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    print(f"[WS] Failed to send to client: {e}")
                    disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            await self.disconnect(conn)
    
    async def send_attendance_event(
        self,
        event_type: str,
        employee_name: str,
        employee_no: str,
        department: str,
        timestamp: datetime,
        device_id: str,
        message: str,
        entry_source: str = "NFC",
        notes: str = None
    ):
        """
        Broadcast an attendance event to all connected clients.
        
        Args:
            event_type: "IN" or "OUT"
            employee_name: Full name of employee
            employee_no: Employee number
            department: Employee's department
            timestamp: Event timestamp
            device_id: ID of the reader device
            message: Welcome/goodbye message
            entry_source: How the entry was made (NFC, MANUAL_HR, MANUAL_EMPLOYEE, BULK_IMPORT)
            notes: Additional notes (for manual entries)
        """
        await self.broadcast({
            "type": "attendance_event",
            "data": {
                "event_type": event_type,
                "employee_name": employee_name,
                "employee_no": employee_no,
                "department": department,
                "timestamp": timestamp.isoformat(),
                "device_id": device_id,
                "message": message,
                "entry_source": entry_source,
                "notes": notes
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def send_card_scanned(self, card_uid: str, is_assigned: bool, assigned_to: str = None):
        """
        Broadcast a card scan event (for unassigned cards).
        
        Args:
            card_uid: Card UID that was scanned
            is_assigned: Whether card is assigned to an employee
            assigned_to: Employee name if assigned
        """
        await self.broadcast({
            "type": "card_scanned",
            "data": {
                "card_uid": card_uid,
                "is_assigned": is_assigned,
                "assigned_to": assigned_to
            },
            "timestamp": datetime.utcnow().isoformat()
        })


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/attendance")
async def websocket_attendance(websocket: WebSocket):
    """
    WebSocket endpoint for real-time attendance updates.
    
    Clients connect here to receive instant notifications of:
    - New attendance events (clock in/out)
    - Card scan events (for wizard)
    - System notifications
    
    Usage:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/attendance');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Attendance event:', data);
    };
    ```
    """
    await manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": "Connected to attendance feed",
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for ping or other messages from client
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30  # 30 second timeout for ping
                )
                
                # Handle ping/pong for keepalive
                if data == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    
            except asyncio.TimeoutError:
                # Send keepalive ping if no message received
                try:
                    await websocket.send_text(json.dumps({
                        "type": "ping",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                except:
                    break
                    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS] Error: {e}")
    finally:
        await manager.disconnect(websocket)


# Export manager for use in attendance router
def get_ws_manager() -> ConnectionManager:
    """Get the global WebSocket connection manager."""
    return manager

