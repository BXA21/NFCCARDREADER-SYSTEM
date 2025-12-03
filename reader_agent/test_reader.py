"""
Simple test script to verify ACR122U can read NFC cards
Run this first to make sure your hardware is working!
"""
import sys
import io
# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from smartcard.System import readers
from smartcard.util import toHexString
import time

def test_reader():
    print("\n" + "=" * 60)
    print("  🔍 NFC CARD READER HARDWARE TEST")
    print("=" * 60)
    
    # Step 1: Check for available readers
    print("\n[STEP 1] Checking for card readers...")
    try:
        available_readers = readers()
    except Exception as e:
        print(f"❌ ERROR: Cannot access smart card system: {e}")
        print("\n   Troubleshooting:")
        print("   - Install PC/SC service (Windows Smart Card service)")
        print("   - Install ACR122U driver from ACS website")
        print("   - Restart your PC after installation")
        return False
    
    if not available_readers:
        print("❌ ERROR: No card readers found!")
        print("\n   Troubleshooting:")
        print("   1. Check USB connection (try different USB port)")
        print("   2. Check Device Manager for ACR122U device")
        print("   3. Install driver from: https://www.acs.com.hk/en/driver/3/acr122u-usb-nfc-reader/")
        return False
    
    print(f"✅ Found {len(available_readers)} reader(s):")
    for idx, reader in enumerate(available_readers):
        print(f"   {idx + 1}. {reader}")
    
    # Step 2: Connect to first reader
    print("\n[STEP 2] Connecting to reader...")
    reader = available_readers[0]
    reader_name = str(reader)
    print(f"   Using: {reader_name}")
    
    if 'acr122' in reader_name.lower():
        print("   ✅ ACR122U detected!")
    else:
        print(f"   ⚠️  Warning: Expected ACR122U, but found: {reader_name}")
        print("   Continuing anyway...")
    
    # Step 3: Wait for card
    print("\n[STEP 3] Waiting for NFC card...")
    print("   " + "─" * 54)
    print("   👉 PLACE YOUR NFC CARD ON THE READER NOW!")
    print("   " + "─" * 54)
    print("   Waiting for 30 seconds...")
    
    connection = None
    card_detected = False
    
    # Try for 30 seconds
    for attempt in range(60):  # 60 attempts * 0.5s = 30 seconds
        try:
            if connection is None:
                connection = reader.createConnection()
            
            connection.connect()
            card_detected = True
            break
            
        except Exception as e:
            if "No smartcard" in str(e) or "Card is unpowered" in str(e):
                # No card yet, wait
                time.sleep(0.5)
                if attempt % 4 == 0:  # Print every 2 seconds
                    dots = "." * (attempt // 4 % 4)
                    print(f"   Waiting{dots:<4}", end="\r")
            else:
                # Other error
                print(f"\n   ⚠️  Connection error: {e}")
                time.sleep(0.5)
    
    print()  # New line after waiting
    
    if not card_detected:
        print("❌ No card detected within 30 seconds")
        print("\n   Troubleshooting:")
        print("   1. Make sure you're using an NFC card (MIFARE, NTAG, etc.)")
        print("   2. Place card flat on the center of reader")
        print("   3. Reader LED should light up when card is near")
        print("   4. Try removing and placing card again")
        return False
    
    print("✅ Card detected!")
    
    # Step 4: Read card UID
    print("\n[STEP 4] Reading card UID...")
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    
    try:
        response, sw1, sw2 = connection.transmit(GET_UID)
        
        if sw1 == 0x90 and sw2 == 0x00:
            uid = toHexString(response).replace(" ", "")
            
            print("✅ SUCCESS! Card read successfully!")
            print("\n" + "─" * 60)
            print("   📇 CARD INFORMATION:")
            print("─" * 60)
            print(f"   Card UID (HEX):     {uid}")
            print(f"   UID Length:         {len(uid)} characters ({len(response)} bytes)")
            print(f"   Format (spaced):    {toHexString(response)}")
            print(f"   Raw bytes:          {response}")
            print("─" * 60)
            
            print("\n   💡 IMPORTANT: Save this UID!")
            print(f"   You'll need to register this card UID in the system:")
            print(f"   Card UID: {uid}")
            
            return True
        else:
            print(f"❌ Failed to read UID")
            print(f"   Status: SW1={sw1:02X} SW2={sw2:02X}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR reading card: {e}")
        return False
    
    finally:
        if connection:
            try:
                connection.disconnect()
            except:
                pass

def main():
    print("\n")
    print("+" + "=" * 58 + "+")
    print("|" + " " * 10 + "NFC ATTENDANCE SYSTEM - HARDWARE TEST" + " " * 11 + "|")
    print("+" + "=" * 58 + "+")
    
    try:
        result = test_reader()
        
        print("\n" + "=" * 60)
        if result:
            print("  🎉 ALL TESTS PASSED!")
            print("  Your NFC reader hardware is working correctly!")
            print("\n  Next steps:")
            print("  1. Make sure backend is running")
            print("  2. Register the card UID in the system")
            print("  3. Run the reader agent: python src/main.py")
        else:
            print("  ⚠️  TESTS FAILED")
            print("  Please fix the issues above before continuing")
        print("=" * 60 + "\n")
        
        return result
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test cancelled by user\n")
        return False
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    # Keep window open
    input("\nPress Enter to exit...")
    exit(0 if success else 1)

