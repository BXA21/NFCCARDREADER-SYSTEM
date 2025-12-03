"""
Database initialization utilities for creating initial data.
"""

import asyncio
import uuid
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.employee import Employee, EmployeeStatus
from app.models.user import User, UserRole
from app.models.shift import Shift
from app.utils.security import hash_password


async def create_initial_admin():
    """
    Create an initial admin user for system access.
    This should be run once during initial setup.
    """
    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("❌ Admin user already exists")
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
            password_hash=hash_password("Admin@123"),  # Change this in production!
            role=UserRole.HR_ADMIN,
            is_active=True,
            employee_id=admin_employee.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        await db.commit()
        
        print("✅ Initial admin user created successfully")
        print("   Username: admin")
        print("   Password: Admin@123")
        print("   ⚠️  IMPORTANT: Change the password after first login!")


async def create_default_shifts():
    """
    Create default shift schedules.
    """
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from datetime import time
        
        # Check if shifts already exist
        result = await db.execute(select(Shift))
        existing_shifts = result.scalars().all()
        
        if existing_shifts:
            print("❌ Shifts already exist")
            return
        
        # Create default shifts
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
            Shift(
                id=uuid.uuid4(),
                name="Night Shift",
                start_time=time(0, 0),
                end_time=time(8, 0),
                grace_minutes=15,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        for shift in shifts:
            db.add(shift)
        
        await db.commit()
        
        print("✅ Default shifts created successfully")
        print("   - Morning Shift (08:00 - 16:00)")
        print("   - Evening Shift (16:00 - 00:00)")
        print("   - Night Shift (00:00 - 08:00)")


async def initialize_database():
    """
    Initialize the database with essential data.
    Run this after creating the database schema.
    """
    print("🔧 Initializing database...")
    await create_initial_admin()
    await create_default_shifts()
    print("✅ Database initialization complete!")


def create_admin():
    """
    Synchronous wrapper for creating admin user.
    Can be called from command line.
    """
    asyncio.run(create_initial_admin())


def create_shifts():
    """
    Synchronous wrapper for creating shifts.
    Can be called from command line.
    """
    asyncio.run(create_default_shifts())


def init_db():
    """
    Synchronous wrapper for full database initialization.
    Can be called from command line.
    """
    asyncio.run(initialize_database())


if __name__ == "__main__":
    # Run full initialization
    init_db()



