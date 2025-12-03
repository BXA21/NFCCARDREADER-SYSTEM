"""
Initialize the database with an admin user.
Run this once to set up your first admin account.
"""

import asyncio
import uuid
from datetime import date

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Employee, User, EmployeeStatus, UserRole
from app.utils.security import hash_password


async def init_admin():
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create employee
        employee = Employee(
            id=uuid.uuid4(),
            employee_no="ADM001",
            full_name="Admin User",
            email="admin@company.com",
            department="Administration",
            hire_date=date.today(),
            status=EmployeeStatus.ACTIVE
        )
        session.add(employee)
        await session.flush()
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            username="admin",
            password_hash=hash_password("admin123"),
            role=UserRole.HR_ADMIN,
            is_active=True,
            employee_id=employee.id
        )
        session.add(user)
        
        await session.commit()
        
        print("=" * 60)
        print("[SUCCESS] Admin user created successfully!")
        print("=" * 60)
        print("  Username: admin")
        print("  Password: admin123")
        print("  Role: HR_ADMIN")
        print("=" * 60)
        print("You can now log in to the system!")


if __name__ == "__main__":
    asyncio.run(init_admin())

