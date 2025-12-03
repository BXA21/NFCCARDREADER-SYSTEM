"""
NFC Card Writer for writing employee data to MIFARE Classic cards.
Supports writing employee information to specific card sectors.
"""

import logging
from typing import Optional, Dict, Any
from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException
from smartcard.util import toHexString, toBytes

class CardWriter:
    """
    Writes employee data to NFC cards (MIFARE Classic).
    
    Card Structure:
    - Sector 1, Block 4: Employee Number (16 bytes ASCII)
    - Sector 1, Block 5: Employee Name (16 bytes ASCII)
    - Sector 1, Block 6: Department (16 bytes ASCII)
    - Sector 2, Block 8: Employee ID (16 bytes hex)
    """
    
    # Default MIFARE Classic keys (change in production!)
    DEFAULT_KEY_A = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    DEFAULT_KEY_B = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    
    # APDU Commands
    LOAD_KEY = [0xFF, 0x82, 0x00, 0x00, 0x06]  # Load authentication key
    AUTHENTICATE = [0xFF, 0x86, 0x00, 0x00, 0x05]  # Authenticate
    UPDATE_BINARY = [0xFF, 0xD6, 0x00]  # Write to block
    
    def __init__(self, reader=None):
        """
        Initialize card writer.
        
        Args:
            reader: Optional pre-connected reader
        """
        self.logger = logging.getLogger(__name__)
        self.reader = reader
        self.connection = None
    
    def connect(self) -> bool:
        """
        Connect to reader if not already connected.
        
        Returns:
            True if connection successful
        """
        if self.reader:
            return True
        
        try:
            available_readers = readers()
            if not available_readers:
                self.logger.error("No readers found")
                return False
            
            self.reader = available_readers[0]
            self.logger.info(f"Connected to reader: {self.reader}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to reader: {e}")
            return False
    
    def authenticate_sector(self, sector: int, key_type: str = 'A') -> bool:
        """
        Authenticate to a card sector using Key A or Key B.
        
        Args:
            sector: Sector number (0-15)
            key_type: 'A' or 'B'
            
        Returns:
            True if authentication successful
        """
        try:
            if not self.connection:
                self.connection = self.reader.createConnection()
                self.connection.connect()
            
            # Load key into reader memory
            key = self.DEFAULT_KEY_A if key_type == 'A' else self.DEFAULT_KEY_B
            load_key_cmd = self.LOAD_KEY + key
            
            response, sw1, sw2 = self.connection.transmit(load_key_cmd)
            if sw1 != 0x90 or sw2 != 0x00:
                self.logger.error(f"Failed to load key: SW1={sw1:02X} SW2={sw2:02X}")
                return False
            
            # Authenticate to sector
            # Calculate block number (first block of sector)
            block = sector * 4
            key_number = 0x00  # Key slot in reader memory
            key_type_byte = 0x60 if key_type == 'A' else 0x61
            
            auth_cmd = self.AUTHENTICATE + [key_type_byte, block, key_number, 0x00]
            
            response, sw1, sw2 = self.connection.transmit(auth_cmd)
            if sw1 != 0x90 or sw2 != 0x00:
                self.logger.error(f"Authentication failed: SW1={sw1:02X} SW2={sw2:02X}")
                return False
            
            self.logger.debug(f"Authenticated to sector {sector} with key {key_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def write_block(self, block: int, data: bytes) -> bool:
        """
        Write 16 bytes to a specific block.
        
        Args:
            block: Block number (0-63 for MIFARE Classic 1K)
            data: Exactly 16 bytes to write
            
        Returns:
            True if write successful
        """
        if len(data) != 16:
            self.logger.error(f"Data must be exactly 16 bytes, got {len(data)}")
            return False
        
        try:
            # Write binary data to block
            write_cmd = self.UPDATE_BINARY + [block, 0x10] + list(data)
            
            response, sw1, sw2 = self.connection.transmit(write_cmd)
            if sw1 != 0x90 or sw2 != 0x00:
                self.logger.error(f"Write failed: SW1={sw1:02X} SW2={sw2:02X}")
                return False
            
            self.logger.debug(f"Wrote to block {block}: {toHexString(data)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Write error: {e}")
            return False
    
    def write_employee_data(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write complete employee data to card.
        
        Args:
            employee_data: Dictionary with:
                - employee_no: Employee number (str)
                - full_name: Full name (str)
                - department: Department (str)
                - employee_id: Employee UUID (str)
        
        Returns:
            Dictionary with write status
        """
        if not self.connect():
            return {"success": False, "message": "Failed to connect to reader"}
        
        try:
            # Prepare data blocks (16 bytes each, padded with spaces)
            employee_no = employee_data.get('employee_no', '').ljust(16)[:16].encode('ascii')
            full_name = employee_data.get('full_name', '').ljust(16)[:16].encode('ascii')
            department = employee_data.get('department', '').ljust(16)[:16].encode('ascii')
            employee_id = employee_data.get('employee_id', '').replace('-', '')[:32]
            
            # Convert UUID to bytes (first 16 chars = 8 bytes, padded to 16 bytes)
            id_bytes = bytes.fromhex(employee_id[:16].ljust(32, '0'))
            
            blocks_written = 0
            
            # Write to Sector 1 (blocks 4, 5, 6)
            if self.authenticate_sector(1, 'A'):
                if self.write_block(4, employee_no):
                    blocks_written += 1
                if self.write_block(5, full_name):
                    blocks_written += 1
                if self.write_block(6, department):
                    blocks_written += 1
            else:
                return {"success": False, "message": "Authentication to Sector 1 failed"}
            
            # Write to Sector 2 (block 8)
            if self.authenticate_sector(2, 'A'):
                if self.write_block(8, id_bytes):
                    blocks_written += 1
            else:
                return {"success": False, "message": "Authentication to Sector 2 failed"}
            
            if blocks_written == 4:
                return {
                    "success": True,
                    "message": "Employee data written successfully",
                    "blocks_written": blocks_written
                }
            else:
                return {
                    "success": False,
                    "message": f"Partial write: {blocks_written}/4 blocks written",
                    "blocks_written": blocks_written
                }
        
        except Exception as e:
            self.logger.error(f"Failed to write employee data: {e}")
            return {"success": False, "message": str(e)}
        
        finally:
            if self.connection:
                try:
                    self.connection.disconnect()
                except:
                    pass
                self.connection = None
    
    def read_employee_data(self) -> Optional[Dict[str, str]]:
        """
        Read employee data from card.
        
        Returns:
            Dictionary with employee data or None if read failed
        """
        if not self.connect():
            return None
        
        try:
            data = {}
            
            # Read from Sector 1
            if self.authenticate_sector(1, 'A'):
                # Read blocks 4, 5, 6
                # This would require READ BINARY APDU commands
                # For now, return None as this is just for testing
                pass
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to read employee data: {e}")
            return None
        
        finally:
            if self.connection:
                try:
                    self.connection.disconnect()
                except:
                    pass
                self.connection = None

