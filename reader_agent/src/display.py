"""
Display manager for console output and user feedback.
"""

import sys
import io
import logging
from datetime import datetime
from typing import Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class DisplayManager:
    """Manages console output and user feedback."""
    
    def __init__(self):
        """Initialize display manager."""
        self.logger = logging.getLogger(__name__)
    
    def show_startup_banner(self, device_id: str, api_url: str):
        """
        Display startup banner.
        
        Args:
            device_id: Device ID
            api_url: API URL
        """
        banner = f"""
╔═══════════════════════════════════════════════════════════════╗
║       NFC ATTENDANCE SYSTEM - READER AGENT v1.0.0            ║
╠═══════════════════════════════════════════════════════════════╣
║  Device ID: {device_id:<50} ║
║  API URL:   {api_url:<50} ║
║  Status:    READY                                             ║
╠═══════════════════════════════════════════════════════════════╣
║  📱 Please tap your NFC card to clock in/out                  ║
║  ⌨️  Press Ctrl+C to exit                                      ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def show_card_detected(self, card_uid: str):
        """
        Display card detected message.
        
        Args:
            card_uid: Card UID
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n[{timestamp}] 📱 Card detected: {card_uid}")
    
    def show_success(self, message: str, employee_name: Optional[str] = None):
        """
        Display success message.
        
        Args:
            message: Success message
            employee_name: Optional employee name
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if employee_name:
            print(f"[{timestamp}] ✅ {message}")
            print(f"           👤 {employee_name}")
        else:
            print(f"[{timestamp}] ✅ {message}")
    
    def show_error(self, message: str):
        """
        Display error message.
        
        Args:
            message: Error message
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ❌ ERROR: {message}")
    
    def show_warning(self, message: str):
        """
        Display warning message.
        
        Args:
            message: Warning message
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ⚠️  WARNING: {message}")
    
    def show_offline_mode(self):
        """Display offline mode message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🔄 OFFLINE MODE: Event saved locally")
    
    def show_sync_status(self, synced_count: int, pending_count: int):
        """
        Display sync status.
        
        Args:
            synced_count: Number of events synced
            pending_count: Number of pending events
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 🔄 Synced {synced_count} events ({pending_count} pending)")
    
    def show_reader_status(self, is_connected: bool):
        """
        Display reader status.
        
        Args:
            is_connected: Whether reader is connected
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if is_connected:
            print(f"[{timestamp}] 🔌 Reader connected")
        else:
            print(f"[{timestamp}] 🔌 Reader disconnected - reconnecting...")



