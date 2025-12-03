"""
Complete system initialization script.
Creates database tables, admin user, default shifts, and test device.
"""

import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Setup path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import AsyncSessionLocal, engine, Base
from app.models.employee import Employee, EmployeeStatus
from app.models.user import User, UserRole
from app.models.shift import Shift
from app.models.device import Device, DeviceStatus
from app.utils.security import hash_password


async def create_tables():
    """Create all database tables."""
    # Import all models to ensure they're registered with Base
    from app.models import (
        Employee, User, Card, AttendanceEvent, 
        CorrectionRequest, Shift, EmployeeShift, 
        Device, AuditLog
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("[OK] Database tables created successfully")


async def create_admin_user():
    """Create initial admin user."""
    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("[INFO] Admin user already exists")
            return
        
        # Create admin employee
        admin_employee = Employee(
            id=uuid.uuid4(),
            employee_no="EMP-000",
            full_name="System Administrator",
            email="admin@company.om",
            department="IT",
            status=EmployeeStatus.ACTIVE,
            hire_date=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(admin_employee)
        await db.flush()
        
        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            username="admin",
            password_hash=hash_password("Admin@123"),
            role=UserRole.HR_ADMIN,
            is_active=True,
            employee_id=admin_employee.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        await db.commit()
        
        print("[OK] Admin user created")
        print("     Username: admin")
        print("     Password: Admin@123")
        print("     WARNING: Change password after first login!")


async def create_default_shifts():
    """Create default shift schedules."""
    async with AsyncSessionLocal() as db:
        from datetime import time
        
        result = await db.execute(select(Shift))
        existing_shifts = result.scalars().all()
        
        if existing_shifts:
            print("[INFO] Shifts already exist")
            return
        
        shifts = [
            Shift(
                id=uuid.uuid4(),
                name="Morning Shift",
                start_time=time(8, 0),
                end_time=time(16, 0),
                grace_minutes=15,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            Shift(
                id=uuid.uuid4(),
                name="Evening Shift",
                start_time=time(16, 0),
                end_time=time(0, 0),
                grace_minutes=15,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
        ]
        
        for shift in shifts:
            db.add(shift)
        
        await db.commit()
        
        print("[OK] Default shifts created")
        print("     Morning Shift (08:00 - 16:00)")
        print("     Evening Shift (16:00 - 00:00)")


async def create_test_device():
    """Create a test device for the NFC reader agent."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Device).where(Device.device_id == "MAIN-GATE-READER")
        )
        existing_device = result.scalar_one_or_none()
        
        if existing_device:
            print("[INFO] Test device already exists")
            print(f"     API Key: {existing_device.api_key}")
            return existing_device.api_key
        
        # Create test device
        api_key = f"dev-api-key-{uuid.uuid4().hex[:16]}"
        
        device = Device(
            id=uuid.uuid4(),
            device_id="MAIN-GATE-READER",
            name="Main Gate NFC Reader",
            location="Main Entrance",
            site_id="HQ",
            api_key=api_key,
            status=DeviceStatus.OFFLINE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(device)
        await db.commit()
        
        print("[OK] Test device created")
        print(f"     Device ID: MAIN-GATE-READER")
        print(f"     API Key: {api_key}")
        print(f"     Add this to reader_agent/config.yaml!")
        
        return api_key


async def create_test_employee():
    """Create a test employee with an NFC card."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Employee).where(Employee.employee_no == "EMP-001")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("[INFO] Test employee already exists")
            return
        
        # Create test employee
        test_employee = Employee(
            id=uuid.uuid4(),
            employee_no="EMP-001",
            full_name="Mohammed Ahmed",
            email="mohammed@company.om",
            department="Engineering",
            status=EmployeeStatus.ACTIVE,
            hire_date=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(test_employee)
        await db.flush()
        
        # Create user account for test employee
        test_user = User(
            id=uuid.uuid4(),
            username="EMP-001",
            password_hash=hash_password("Employee@123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
            employee_id=test_employee.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(test_user)
        await db.commit()
        
        print("[OK] Test employee created")
        print("     Name: Mohammed Ahmed")
        print("     Username: EMP-001")
        print("     Password: Employee@123")


async def initialize_system():
    """Run complete system initialization."""
    print("\n" + "="*60)
    print("[*] NFC ATTENDANCE SYSTEM - INITIALIZATION")
    print("="*60 + "\n")
    
    print("[1/5] Creating database tables...")
    await create_tables()
    print()
    
    print("[2/5] Setting up admin user...")
    await create_admin_user()
    print()
    
    print("[3/5] Creating default shifts...")
    await create_default_shifts()
    print()
    
    print("[4/5] Setting up test device...")
    api_key = await create_test_device()
    print()
    
    print("[5/5] Creating test employee...")
    await create_test_employee()
    print()
    
    print("="*60)
    print("[OK] INITIALIZATION COMPLETE!")
    print("="*60)
    print()
    print("NEXT STEPS:")
    print("   1. Start the backend: uvicorn app.main:app --reload")
    print("   2. Start the frontend: npm run dev")
    print("   3. Update reader_agent/config.yaml with the API key")
    print("   4. Start the reader agent: python src/main.py")
    print()
    print("LOGIN CREDENTIALS:")
    print("   Admin: admin / Admin@123")
    print("   Employee: EMP-001 / Employee@123")
    print()
    
    return api_key


if __name__ == "__main__":
    asyncio.run(initialize_system())

