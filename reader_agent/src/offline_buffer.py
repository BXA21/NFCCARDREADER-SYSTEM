"""
Offline buffer for storing attendance events when API is unavailable.
Uses SQLite for local persistence.
"""

import logging
import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class OfflineBuffer:
    """Manages offline event storage using SQLite."""
    
    def __init__(self, db_path: str):
        """
        Initialize offline buffer.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        # Create directory if it doesn't exist
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buffered_events (
                id TEXT PRIMARY KEY,
                card_uid TEXT NOT NULL,
                device_id TEXT NOT NULL,
                event_type TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL,
                sync_attempts INTEGER DEFAULT 0,
                last_sync_attempt TEXT,
                status TEXT DEFAULT 'PENDING'
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Offline buffer initialized: {self.db_path}")
    
    def add_event(
        self,
        card_uid: str,
        device_id: str,
        timestamp: datetime,
        event_id: Optional[str] = None
    ) -> str:
        """
        Add an event to the buffer.
        
        Args:
            card_uid: Card UID
            device_id: Device ID
            timestamp: Event timestamp
            event_id: Optional event ID (generated if not provided)
            
        Returns:
            Event ID
        """
        if not event_id:
            event_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO buffered_events 
                (id, card_uid, device_id, timestamp, created_at, status)
                VALUES (?, ?, ?, ?, ?, 'PENDING')
            ''', (
                event_id,
                card_uid,
                device_id,
                timestamp.isoformat(),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            self.logger.info(f"Event buffered offline: {event_id}")
            
        except sqlite3.IntegrityError:
            self.logger.warning(f"Event {event_id} already exists in buffer")
        finally:
            conn.close()
        
        return event_id
    
    def get_pending_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get pending events to sync.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of pending events
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM buffered_events
            WHERE status = 'PENDING'
            ORDER BY created_at ASC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append({
                'id': row['id'],
                'card_uid': row['card_uid'],
                'device_id': row['device_id'],
                'timestamp': row['timestamp'],
                'sync_attempts': row['sync_attempts']
            })
        
        return events
    
    def mark_synced(self, event_id: str):
        """
        Mark an event as successfully synced.
        
        Args:
            event_id: Event ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE buffered_events
            SET status = 'SYNCED', last_sync_attempt = ?
            WHERE id = ?
        ''', (datetime.utcnow().isoformat(), event_id))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Event marked as synced: {event_id}")
    
    def mark_failed(self, event_id: str):
        """
        Mark a sync attempt as failed.
        
        Args:
            event_id: Event ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE buffered_events
            SET 
                sync_attempts = sync_attempts + 1,
                last_sync_attempt = ?,
                status = CASE 
                    WHEN sync_attempts >= 5 THEN 'FAILED'
                    ELSE 'PENDING'
                END
            WHERE id = ?
        ''', (datetime.utcnow().isoformat(), event_id))
        
        conn.commit()
        conn.close()
        
        self.logger.warning(f"Event sync failed: {event_id}")
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get buffer statistics.
        
        Returns:
            Dictionary with counts by status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM buffered_events
            GROUP BY status
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        stats = {
            'PENDING': 0,
            'SYNCED': 0,
            'FAILED': 0
        }
        
        for row in rows:
            stats[row[0]] = row[1]
        
        return stats
    
    def cleanup_old_events(self, days: int = 30):
        """
        Remove old synced events from the buffer.
        
        Args:
            days: Remove events older than this many days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM buffered_events
            WHERE status = 'SYNCED' AND created_at < ?
        ''', (cutoff_date.isoformat(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            self.logger.info(f"Cleaned up {deleted} old events from buffer")


# Import for cleanup method
from datetime import timedelta



