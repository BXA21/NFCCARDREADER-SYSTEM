"""
Sync manager for uploading buffered events to the backend.
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional


class SyncManager:
    """Manages background synchronization of offline events."""
    
    def __init__(self, api_client, offline_buffer, sync_interval: int = 30):
        """
        Initialize sync manager.
        
        Args:
            api_client: API client instance
            offline_buffer: Offline buffer instance
            sync_interval: Sync interval in seconds
        """
        self.api_client = api_client
        self.offline_buffer = offline_buffer
        self.sync_interval = sync_interval
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    def start(self):
        """Start the background sync task."""
        if self._running:
            self.logger.warning("Sync manager already running")
            return
        
        self._running = True
        self.logger.info(f"Starting sync manager (interval: {self.sync_interval}s)")
    
    def stop(self):
        """Stop the background sync task."""
        self._running = False
        self.logger.info("Stopping sync manager")
    
    def sync_once(self) -> int:
        """
        Perform a single sync operation.
        
        Returns:
            Number of events successfully synced
        """
        if not self.api_client.health_check():
            self.logger.debug("API not reachable, skipping sync")
            return 0
        
        # Get pending events
        pending_events = self.offline_buffer.get_pending_events()
        
        if not pending_events:
            return 0
        
        self.logger.info(f"Syncing {len(pending_events)} buffered events...")
        
        synced_count = 0
        
        for event in pending_events:
            try:
                # Try to send the event
                self.api_client.record_attendance(
                    card_uid=event['card_uid'],
                    device_id=event['device_id'],
                    event_timestamp=datetime.fromisoformat(event['timestamp']),
                    event_id=event['id']
                )
                
                # Mark as synced
                self.offline_buffer.mark_synced(event['id'])
                synced_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to sync event {event['id']}: {e}")
                self.offline_buffer.mark_failed(event['id'])
        
        if synced_count > 0:
            self.logger.info(f"Successfully synced {synced_count}/{len(pending_events)} events")
        
        return synced_count
    
    def run(self):
        """Run the sync loop (blocking)."""
        import time
        
        while self._running:
            try:
                self.sync_once()
            except Exception as e:
                self.logger.error(f"Error during sync: {e}")
            
            # Wait for next sync interval
            for _ in range(self.sync_interval):
                if not self._running:
                    break
                time.sleep(1)



