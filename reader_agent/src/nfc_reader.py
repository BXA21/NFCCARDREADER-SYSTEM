"""
NFC Reader interface for ACR122U using pyscard.
"""

import logging
from typing import Optional
from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException
from smartcard.util import toHexString


class NFCReader:
    """
    Interface for ACR122U NFC card reader.
    Uses PC/SC protocol via pyscard library.
    """
    
    # APDU command to get card UID (for MIFARE cards)
    GET_UID_COMMAND = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    
    def __init__(self):
        """Initialize NFC reader interface."""
        self.logger = logging.getLogger(__name__)
        self.reader = None
        self.connection = None
        self._last_uid = None  # Track last seen UID to avoid duplicates
    
    def connect(self) -> bool:
        """
        Connect to the ACR122U reader.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Get list of available readers
            available_readers = readers()
            
            if not available_readers:
                self.logger.error("No card readers found. Please connect ACR122U reader.")
                return False
            
            # Try to find ACR122U reader
            self.reader = None
            for reader in available_readers:
                reader_name = str(reader).lower()
                if 'acr122' in reader_name or 'acr 122' in reader_name:
                    self.reader = reader
                    break
            
            # If ACR122U not found, use first available reader
            if not self.reader:
                self.logger.warning(
                    f"ACR122U not found. Using first available reader: {available_readers[0]}"
                )
                self.reader = available_readers[0]
            
            self.logger.info(f"Connected to reader: {self.reader}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to reader: {e}")
            return False
    
    def wait_for_card(self, timeout: float = 1.0) -> Optional[str]:
        """
        Wait for a card to be placed on the reader.
        
        Args:
            timeout: Timeout in seconds (not strictly enforced)
            
        Returns:
            Card UID as hex string, or None if no card detected
        """
        if not self.reader:
            self.logger.error("Reader not connected")
            return None
        
        try:
            # Try to connect to the card
            if not self.connection:
                self.connection = self.reader.createConnection()
                self.connection.connect()
            
            # Send GET UID command
            response, sw1, sw2 = self.connection.transmit(self.GET_UID_COMMAND)
            
            # Check if command successful (sw1=0x90, sw2=0x00)
            if sw1 == 0x90 and sw2 == 0x00:
                # Convert response to hex string
                uid = toHexString(response).replace(" ", "")
                
                # Check if this is the same card as before (avoid duplicates)
                if uid == self._last_uid:
                    return None  # Same card still present
                
                self._last_uid = uid
                self.logger.debug(f"Card detected: {uid}")
                return uid
            else:
                self.logger.debug(f"GET UID failed: SW1={sw1:02X} SW2={sw2:02X}")
                return None
                
        except NoCardException:
            # No card present - this is normal
            if self.connection:
                self.connection.disconnect()
                self.connection = None
            self._last_uid = None  # Reset last UID when card removed
            return None
            
        except CardConnectionException as e:
            # Connection error - try to reconnect
            self.logger.warning(f"Card connection error: {e}")
            if self.connection:
                try:
                    self.connection.disconnect()
                except:
                    pass
                self.connection = None
            self._last_uid = None
            return None
            
        except Exception as e:
            self.logger.error(f"Error reading card: {e}")
            if self.connection:
                try:
                    self.connection.disconnect()
                except:
                    pass
                self.connection = None
            self._last_uid = None
            return None
    
    def disconnect(self):
        """Disconnect from the reader."""
        if self.connection:
            try:
                self.connection.disconnect()
            except:
                pass
            self.connection = None
        
        self.reader = None
        self._last_uid = None
        self.logger.info("Disconnected from reader")
    
    def is_connected(self) -> bool:
        """
        Check if reader is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self.reader is not None



