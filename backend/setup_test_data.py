"""
Setup script to create test data for NFC attendance system
Run this to register device, employee, and card
"""
import asyncio
import sys
import io
from datetime import date
sys.path.insert(0, '.')

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from app.database import AsyncSessionLocal
from app.models.device import Device, DeviceStatus
from app.models.employee import Employee, EmployeeStatus
from app.models.card import Card, CardStatus
from app.models.user import User, UserRole
from app.models.shift import Shift
from app.utils.security import hash_password
import uuid

async def setup_test_data():
    """Create test data for the NFC system"""
    
    print("\n" + "="*60)
    print("  NFC ATTENDANCE SYSTEM - TEST DATA SETUP")
    print("="*60 + "\n")
    
    async with AsyncSessionLocal() as db:
        
        # 1. Create Test Device
        print("[1] Creating test device...")
        device_api_key = "test-reader-api-key-12345"
        
        # Check if device already exists
        from sqlalchemy import select
        result = await db.execute(
            select(Device).where(Device.device_id == "MAIN-GATE-READER")
        )
        existing_device = result.scalar_one_or_none()
        
        if existing_device:
            print(f"   ✅ Device already exists: {existing_device.device_id}")
            device = existing_device
        else:
            device = Device(
                id=uuid.uuid4(),
                device_id="MAIN-GATE-READER",
                name="Main Gate Reader Station",
                location="Main Entrance",
                api_key=device_api_key,
                status=DeviceStatus.ONLINE
            )
            db.add(device)
            await db.commit()
            await db.refresh(device)
            print(f"   ✅ Device created: {device.device_id}")
        
        print(f"   📝 API Key: {device_api_key}")
        print(f"   📍 Location: {device.location}")
        
        # 2. Create Test Shift
        print("\n[2] Creating test shift...")
        result = await db.execute(
            select(Shift).where(Shift.name == "Day Shift")
        )
        existing_shift = result.scalar_one_or_none()
        
        if existing_shift:
            print(f"   ✅ Shift already exists: {existing_shift.name}")
            shift = existing_shift
        else:
            from datetime import time
            shift = Shift(
                id=uuid.uuid4(),
                name="Day Shift",
                start_time=time(8, 0, 0),
                end_time=time(17, 0, 0),
                grace_minutes=15,
                is_active=True
            )
            db.add(shift)
            await db.commit()
            await db.refresh(shift)
            print(f"   ✅ Shift created: {shift.name}")
        
        print(f"   ⏰ Hours: {shift.start_time} - {shift.end_time}")
        
        # 3. Create Test Employee
        print("\n[3] Creating test employee...")
        result = await db.execute(
            select(Employee).where(Employee.employee_no == "EMP-TEST-001")
        )
        existing_employee = result.scalar_one_or_none()
        
        if existing_employee:
            print(f"   ✅ Employee already exists: {existing_employee.employee_no}")
            employee = existing_employee
        else:
            employee = Employee(
                id=uuid.uuid4(),
                employee_no="EMP-TEST-001",
                full_name="Test Employee",
                email="test.employee@company.com",
                department="Testing Department",
                hire_date=date.today(),
                status=EmployeeStatus.ACTIVE
            )
            db.add(employee)
            await db.commit()
            await db.refresh(employee)
            print(f"   ✅ Employee created: {employee.employee_no}")
        
        print(f"   👤 Name: {employee.full_name}")
        print(f"   📧 Email: {employee.email}")
        print(f"   🏢 Department: {employee.department}")
        
        # 4. Create User Account for Employee
        print("\n[4] Creating user account...")
        result = await db.execute(
            select(User).where(User.username == "EMP-TEST-001")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"   ✅ User already exists: {existing_user.username}")
            user = existing_user
        else:
            user = User(
                id=uuid.uuid4(),
                username="EMP-TEST-001",
                password_hash=hash_password("password123"),
                role=UserRole.EMPLOYEE,
                is_active=True,
                employee_id=employee.id
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"   ✅ User created: {user.username}")
        
        print(f"   🔑 Username: {user.username}")
        print(f"   🔐 Password: password123")
        print(f"   👔 Role: {user.role.value}")
        
        # 5. Issue Card to Employee
        print("\n[5] Issuing NFC card...")
        card_uid = "043BBE1B6F6180"  # The UID we read from your card
        
        result = await db.execute(
            select(Card).where(Card.card_uid == card_uid)
        )
        existing_card = result.scalar_one_or_none()
        
        if existing_card:
            print(f"   ✅ Card already exists: {existing_card.card_uid}")
            card = existing_card
            # Update status if needed
            if card.status != CardStatus.ACTIVE:
                card.status = CardStatus.ACTIVE
                await db.commit()
                print(f"   ✅ Card status updated to ACTIVE")
        else:
            card = Card(
                id=uuid.uuid4(),
                employee_id=employee.id,
                card_uid=card_uid,
                status=CardStatus.ACTIVE
            )
            db.add(card)
            await db.commit()
            await db.refresh(card)
            print(f"   ✅ Card issued: {card.card_uid}")
        
        print(f"   🎴 Card UID: {card.card_uid}")
        print(f"   ✅ Status: {card.status.value}")
        
        # 6. Create HR Admin User (for dashboard access)
        print("\n[6] Creating HR Admin account...")
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print(f"   ✅ Admin already exists: {existing_admin.username}")
        else:
            # Create admin employee
            admin_employee = Employee(
                id=uuid.uuid4(),
                employee_no="EMP-ADMIN",
                full_name="System Administrator",
                email="admin@company.com",
                department="IT",
                hire_date=date.today(),
                status=EmployeeStatus.ACTIVE
            )
            db.add(admin_employee)
            await db.flush()
            
            admin_user = User(
                id=uuid.uuid4(),
                username="admin",
                password_hash=hash_password("admin123"),
                role=UserRole.HR_ADMIN,
                is_active=True,
                employee_id=admin_employee.id
            )
            db.add(admin_user)
            await db.commit()
            print(f"   ✅ Admin created: admin")
        
        print(f"   🔑 Username: admin")
        print(f"   🔐 Password: admin123")
        print(f"   👔 Role: HR_ADMIN")
    
    print("\n" + "="*60)
    print("  ✅ SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 SUMMARY:")
    print("-" * 60)
    print("Device ID:        MAIN-GATE-READER")
    print("API Key:          test-reader-api-key-12345")
    print()
    print("Test Employee:    EMP-TEST-001 (Test Employee)")
    print("Username:         EMP-TEST-001")
    print("Password:         password123")
    print()
    print("Admin User:       admin")
    print("Password:         admin123")
    print()
    print("Card UID:         043BBE1B6F6180")
    print("Card Status:      ACTIVE")
    print("-" * 60)
    
    print("\n🚀 NEXT STEPS:")
    print("1. Start frontend: cd frontend && npm run dev")
    print("2. Set API key: $env:DEVICE_API_KEY='test-reader-api-key-12345'")
    print("3. Start reader agent: cd reader_agent && python src/main.py")
    print("4. Tap your card on the reader!")
    print("5. Login to dashboard at http://localhost:5173")
    print("   - Username: admin")
    print("   - Password: admin123")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(setup_test_data())
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

