"""
Script to apply manual attendance schema changes to SQLite database.
Run this after starting the backend to add the new fields.
"""

import asyncio
import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from app.database import engine


async def apply_schema_changes():
    """Apply schema changes for manual attendance feature."""
    
    async with engine.begin() as conn:
        print("🔄 Applying schema changes for Manual Attendance System...")
        
        # Check if columns already exist (SQLite doesn't support IF NOT EXISTS for ADD COLUMN)
        result = await conn.execute(text("PRAGMA table_info(attendance_events)"))
        existing_columns = [row[1] for row in result.fetchall()]
        
        # Add new columns to attendance_events
        if 'entry_source' not in existing_columns:
            await conn.execute(text("ALTER TABLE attendance_events ADD COLUMN entry_source VARCHAR(20) DEFAULT 'NFC'"))
            print("  ✅ Added entry_source column to attendance_events")
        else:
            print("  ⏭️  entry_source column already exists")
        
        if 'notes' not in existing_columns:
            await conn.execute(text("ALTER TABLE attendance_events ADD COLUMN notes TEXT"))
            print("  ✅ Added notes column to attendance_events")
        else:
            print("  ⏭️  notes column already exists")
        
        if 'entered_by' not in existing_columns:
            await conn.execute(text("ALTER TABLE attendance_events ADD COLUMN entered_by VARCHAR(100)"))
            print("  ✅ Added entered_by column to attendance_events")
        else:
            print("  ⏭️  entered_by column already exists")
        
        if 'edited_at' not in existing_columns:
            await conn.execute(text("ALTER TABLE attendance_events ADD COLUMN edited_at DATETIME"))
            print("  ✅ Added edited_at column to attendance_events")
        else:
            print("  ⏭️  edited_at column already exists")
        
        if 'edited_by' not in existing_columns:
            await conn.execute(text("ALTER TABLE attendance_events ADD COLUMN edited_by VARCHAR(100)"))
            print("  ✅ Added edited_by column to attendance_events")
        else:
            print("  ⏭️  edited_by column already exists")
        
        # Check employees table
        result = await conn.execute(text("PRAGMA table_info(employees)"))
        emp_columns = [row[1] for row in result.fetchall()]
        
        if 'pin_hash' not in emp_columns:
            await conn.execute(text("ALTER TABLE employees ADD COLUMN pin_hash VARCHAR(255)"))
            print("  ✅ Added pin_hash column to employees")
        else:
            print("  ⏭️  pin_hash column already exists")
        
        if 'phone' not in emp_columns:
            await conn.execute(text("ALTER TABLE employees ADD COLUMN phone VARCHAR(50)"))
            print("  ✅ Added phone column to employees")
        else:
            print("  ⏭️  phone column already exists")
        
        if 'position' not in emp_columns:
            await conn.execute(text("ALTER TABLE employees ADD COLUMN position VARCHAR(100)"))
            print("  ✅ Added position column to employees")
        else:
            print("  ⏭️  position column already exists")
        
        # Check if leave_types table exists
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='leave_types'"))
        if not result.fetchone():
            await conn.execute(text("""
                CREATE TABLE leave_types (
                    id VARCHAR(36) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    is_paid BOOLEAN NOT NULL DEFAULT 1,
                    max_days_per_year INTEGER,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """))
            print("  ✅ Created leave_types table")
            
            # Insert default leave types
            import uuid
            from datetime import datetime
            now = datetime.utcnow().isoformat()
            
            leave_types = [
                ('Annual Leave', 'Paid annual vacation leave', True, 21),
                ('Sick Leave', 'Paid sick leave', True, 14),
                ('Personal Leave', 'Unpaid personal leave', False, None),
                ('Maternity Leave', 'Paid maternity leave', True, 90),
                ('Paternity Leave', 'Paid paternity leave', True, 5),
                ('Bereavement Leave', 'Paid bereavement leave', True, 5),
                ('Other', 'Other leave types', False, None),
            ]
            
            for name, desc, is_paid, max_days in leave_types:
                await conn.execute(
                    text("INSERT INTO leave_types (id, name, description, is_paid, max_days_per_year, is_active, created_at, updated_at) VALUES (:id, :name, :desc, :is_paid, :max_days, 1, :created, :updated)"),
                    {"id": str(uuid.uuid4()), "name": name, "desc": desc, "is_paid": is_paid, "max_days": max_days, "created": now, "updated": now}
                )
            print("  ✅ Inserted default leave types")
        else:
            print("  ⏭️  leave_types table already exists")
        
        # Check if leave_records table exists
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='leave_records'"))
        if not result.fetchone():
            await conn.execute(text("""
                CREATE TABLE leave_records (
                    id VARCHAR(36) PRIMARY KEY,
                    employee_id VARCHAR(36) NOT NULL REFERENCES employees(id),
                    leave_type_id VARCHAR(36) NOT NULL REFERENCES leave_types(id),
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    notes TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT 'APPROVED',
                    entered_by VARCHAR(100),
                    approved_by VARCHAR(100),
                    approved_at DATETIME,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
            """))
            await conn.execute(text("CREATE INDEX ix_leave_records_employee_id ON leave_records(employee_id)"))
            await conn.execute(text("CREATE INDEX ix_leave_records_start_date ON leave_records(start_date)"))
            await conn.execute(text("CREATE INDEX ix_leave_records_status ON leave_records(status)"))
            print("  ✅ Created leave_records table with indexes")
        else:
            print("  ⏭️  leave_records table already exists")
        
        await conn.commit()
        print("\n✅ Schema changes applied successfully!")
        print("\n📋 New features available:")
        print("   - Manual attendance entry (HR)")
        print("   - Employee self-service clock in/out")
        print("   - Leave management")
        print("   - Entry source tracking on dashboard")


if __name__ == "__main__":
    asyncio.run(apply_schema_changes())

