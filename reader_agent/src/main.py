"""
Main entry point for the NFC Reader Agent.
"""

import logging
import sys
import time
import signal
import threading
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager
from nfc_reader import NFCReader
from api_client import APIClient
from offline_buffer import OfflineBuffer
from sync_manager import SyncManager
from display import DisplayManager


class ReaderAgent:
    """Main application class for the reader agent."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the reader agent.
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.display = DisplayManager()
        self.nfc_reader = NFCReader()
        self.api_client = APIClient(
            base_url=self.config.api_base_url,
            api_key=self.config.device_api_key,
            timeout=self.config.api_timeout
        )
        self.offline_buffer = OfflineBuffer(self.config.offline_db_path)
        self.sync_manager = SyncManager(
            api_client=self.api_client,
            offline_buffer=self.offline_buffer,
            sync_interval=self.config.sync_interval
        )
        
        # Runtime state
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        
        # File handler
        file_handler = logging.FileHandler(self.config.log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the reader agent."""
        self.running = True
        
        # Show startup banner
        self.display.show_startup_banner(
            device_id=self.config.device_id,
            api_url=self.config.api_base_url
        )
        
        # Connect to NFC reader
        if not self.nfc_reader.connect():
            self.display.show_error("Failed to connect to NFC reader")
            return
        
        self.display.show_reader_status(True)
        
        # Start sync manager in background thread
        sync_thread = threading.Thread(target=self.sync_manager.run, daemon=True)
        sync_thread.start()
        self.sync_manager.start()
        
        # Main loop
        self.logger.info("Starting main loop")
        self._main_loop()
    
    def _main_loop(self):
        """Main event loop for reading cards."""
        while self.running:
            try:
                # Check if reader is still connected
                if not self.nfc_reader.is_connected():
                    self.display.show_reader_status(False)
                    time.sleep(self.config.reconnect_delay)
                    self.nfc_reader.connect()
                    continue
                
                # Wait for card tap
                card_uid = self.nfc_reader.wait_for_card(timeout=self.config.poll_interval)
                
                if card_uid:
                    self._handle_card_tap(card_uid)
                
                # Small delay to avoid busy waiting
                time.sleep(self.config.poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(1)  # Prevent tight error loop
    
    def _handle_card_tap(self, card_uid: str):
        """
        Handle a card tap event.
        
        Args:
            card_uid: Card UID
        """
        self.display.show_card_detected(card_uid)
        
        try:
            # Try to send to API
            response = self.api_client.record_attendance(
                card_uid=card_uid,
                device_id=self.config.device_id,
                event_timestamp=datetime.utcnow()
            )
            
            # Show success message
            message = response.get('message', 'Attendance recorded')
            employee_name = response.get('employee_name')
            self.display.show_success(message, employee_name)
            
        except Exception as e:
            # API unavailable - save to offline buffer
            self.logger.warning(f"API unavailable: {e}")
            
            event_id = self.offline_buffer.add_event(
                card_uid=card_uid,
                device_id=self.config.device_id,
                timestamp=datetime.utcnow()
            )
            
            self.display.show_offline_mode()
            
            # Try immediate sync
            synced = self.sync_manager.sync_once()
            if synced > 0:
                stats = self.offline_buffer.get_stats()
                self.display.show_sync_status(synced, stats['PENDING'])
    
    def stop(self):
        """Stop the reader agent."""
        self.running = False
        self.sync_manager.stop()
        self.nfc_reader.disconnect()
        self.api_client.close()
        
        # Show final stats
        stats = self.offline_buffer.get_stats()
        if stats['PENDING'] > 0:
            self.display.show_warning(
                f"{stats['PENDING']} events pending sync. "
                "They will be synced on next startup."
            )
        
        self.logger.info("Reader agent stopped")
        print("\nGoodbye! 👋")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='NFC Attendance Reader Agent')
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    try:
        agent = ReaderAgent(config_path=args.config)
        agent.start()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()



