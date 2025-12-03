"""Add manual attendance fields and leave management

Revision ID: 002
Revises: 001
Create Date: 2025-12-03 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create new entry_source enum with all values
    op.execute("CREATE TYPE entrysource AS ENUM ('NFC', 'MANUAL_HR', 'MANUAL_EMPLOYEE', 'BULK_IMPORT', 'SYSTEM')")
    
    # Add new columns to attendance_events table
    op.add_column('attendance_events', sa.Column('entry_source', sa.Enum('NFC', 'MANUAL_HR', 'MANUAL_EMPLOYEE', 'BULK_IMPORT', 'SYSTEM', name='entrysource'), nullable=True))
    op.add_column('attendance_events', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('attendance_events', sa.Column('entered_by', sa.String(length=100), nullable=True))
    op.add_column('attendance_events', sa.Column('edited_at', sa.DateTime(), nullable=True))
    op.add_column('attendance_events', sa.Column('edited_by', sa.String(length=100), nullable=True))
    
    # Make card_id nullable for manual entries
    op.alter_column('attendance_events', 'card_id',
                    existing_type=postgresql.UUID(as_uuid=True),
                    nullable=True)
    
    # Update existing records to have NFC as entry_source
    op.execute("UPDATE attendance_events SET entry_source = 'NFC' WHERE entry_source IS NULL")
    
    # Now make entry_source not nullable
    op.alter_column('attendance_events', 'entry_source',
                    existing_type=sa.Enum('NFC', 'MANUAL_HR', 'MANUAL_EMPLOYEE', 'BULK_IMPORT', 'SYSTEM', name='entrysource'),
                    nullable=False,
                    server_default='NFC')
    
    # Add index on entry_source
    op.create_index(op.f('ix_attendance_events_entry_source'), 'attendance_events', ['entry_source'], unique=False)
    
    # Add PIN hash to employees table for self-service authentication
    op.add_column('employees', sa.Column('pin_hash', sa.String(length=255), nullable=True))
    op.add_column('employees', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('employees', sa.Column('position', sa.String(length=100), nullable=True))
    
    # Create leave_types table
    op.create_table(
        'leave_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_paid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('max_days_per_year', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create leave_records table
    op.create_table(
        'leave_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('leave_type_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', name='leavestatus'), nullable=False, server_default='APPROVED'),
        sa.Column('entered_by', sa.String(length=100), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['leave_type_id'], ['leave_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_records_employee_id'), 'leave_records', ['employee_id'], unique=False)
    op.create_index(op.f('ix_leave_records_start_date'), 'leave_records', ['start_date'], unique=False)
    op.create_index(op.f('ix_leave_records_status'), 'leave_records', ['status'], unique=False)
    
    # Insert default leave types
    op.execute("""
        INSERT INTO leave_types (id, name, description, is_paid, max_days_per_year, is_active, created_at, updated_at)
        VALUES 
        (gen_random_uuid(), 'Annual Leave', 'Paid annual vacation leave', true, 21, true, NOW(), NOW()),
        (gen_random_uuid(), 'Sick Leave', 'Paid sick leave', true, 14, true, NOW(), NOW()),
        (gen_random_uuid(), 'Personal Leave', 'Unpaid personal leave', false, NULL, true, NOW(), NOW()),
        (gen_random_uuid(), 'Maternity Leave', 'Paid maternity leave', true, 90, true, NOW(), NOW()),
        (gen_random_uuid(), 'Paternity Leave', 'Paid paternity leave', true, 5, true, NOW(), NOW()),
        (gen_random_uuid(), 'Bereavement Leave', 'Paid bereavement leave', true, 5, true, NOW(), NOW()),
        (gen_random_uuid(), 'Other', 'Other leave types', false, NULL, true, NOW(), NOW())
    """)


def downgrade() -> None:
    # Drop leave tables
    op.drop_index(op.f('ix_leave_records_status'), table_name='leave_records')
    op.drop_index(op.f('ix_leave_records_start_date'), table_name='leave_records')
    op.drop_index(op.f('ix_leave_records_employee_id'), table_name='leave_records')
    op.drop_table('leave_records')
    op.drop_table('leave_types')
    
    # Remove employee columns
    op.drop_column('employees', 'position')
    op.drop_column('employees', 'phone')
    op.drop_column('employees', 'pin_hash')
    
    # Remove attendance_events columns and indexes
    op.drop_index(op.f('ix_attendance_events_entry_source'), table_name='attendance_events')
    op.drop_column('attendance_events', 'edited_by')
    op.drop_column('attendance_events', 'edited_at')
    op.drop_column('attendance_events', 'entered_by')
    op.drop_column('attendance_events', 'notes')
    op.drop_column('attendance_events', 'entry_source')
    
    # Make card_id not nullable again
    op.alter_column('attendance_events', 'card_id',
                    existing_type=postgresql.UUID(as_uuid=True),
                    nullable=False)
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS entrysource')
    op.execute('DROP TYPE IF EXISTS leavestatus')

