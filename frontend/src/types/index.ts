/**
 * TypeScript type definitions for the application
 */

// User roles
export enum UserRole {
  EMPLOYEE = 'EMPLOYEE',
  SUPERVISOR = 'SUPERVISOR',
  HR_ADMIN = 'HR_ADMIN',
}

// Employee status
export enum EmployeeStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  TERMINATED = 'TERMINATED',
}

// Card status
export enum CardStatus {
  ACTIVE = 'ACTIVE',
  LOST = 'LOST',
  REVOKED = 'REVOKED',
}

// Attendance event type
export enum AttendanceEventType {
  IN = 'IN',
  OUT = 'OUT',
}

// Entry source - how attendance was recorded
export enum EntrySource {
  NFC = 'NFC',
  MANUAL_HR = 'MANUAL_HR',
  MANUAL_EMPLOYEE = 'MANUAL_EMPLOYEE',
  BULK_IMPORT = 'BULK_IMPORT',
  SYSTEM = 'SYSTEM',
}

// Leave status
export enum LeaveStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  CANCELLED = 'CANCELLED',
}

// User
export interface User {
  id: string
  username: string
  role: UserRole
  is_active: boolean
  employee_id: string
  created_at: string
  updated_at: string
  last_login_at?: string
}

// Employee
export interface Employee {
  id: string
  employee_no: string
  full_name: string
  email: string
  department: string
  supervisor_id?: string
  status: EmployeeStatus
  hire_date: string
  created_at: string
  updated_at: string
  has_active_card?: boolean
  supervisor_name?: string
}

// Card
export interface Card {
  id: string
  card_uid: string
  employee_id: string
  status: CardStatus
  issued_at: string
  revoked_at?: string
  created_at: string
  updated_at: string
  employee_name?: string
  employee_no?: string
}

// Attendance Event
export interface AttendanceEvent {
  id: string
  employee_id: string
  card_id?: string
  event_type: AttendanceEventType
  event_timestamp: string
  device_id: string
  source: string
  entry_source: EntrySource
  notes?: string
  entered_by?: string
  edited_at?: string
  edited_by?: string
  created_at: string
  employee_name: string
  employee_no: string
  department?: string
}

// Shift
export interface Shift {
  id: string
  name: string
  start_time: string
  end_time: string
  grace_minutes: number
  is_active: boolean
  created_at: string
  updated_at: string
  employee_count?: number
}

// Correction Request
export interface CorrectionRequest {
  id: string
  employee_id: string
  date: string
  requested_event_type: string
  requested_time: string
  reason: string
  status: 'PENDING' | 'APPROVED' | 'REJECTED'
  approver_id?: string
  approver_comment?: string
  created_at: string
  updated_at: string
  reviewed_at?: string
}

// API Response Types
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface MessageResponse {
  message: string
}

export interface ErrorResponse {
  error: string
  detail?: string
}

// Attendance Summary
export interface AttendanceSummary {
  date: string
  present_count: number
  absent_count: number
  late_count: number
  early_leave_count: number
  total_employees: number
}

// Leave Type
export interface LeaveType {
  id: string
  name: string
  description?: string
  is_paid: boolean
  max_days_per_year?: number
  is_active: boolean
}

// Leave Record
export interface LeaveRecord {
  id: string
  employee_id: string
  employee_name: string
  employee_no: string
  leave_type_id: string
  leave_type_name: string
  start_date: string
  end_date: string
  days_count: number
  notes?: string
  status: LeaveStatus
  entered_by?: string
  approved_by?: string
  approved_at?: string
  created_at: string
}

// Manual Attendance Response
export interface ManualAttendanceResponse {
  id: string
  employee_id: string
  employee_name: string
  employee_no: string
  event_type: AttendanceEventType
  event_timestamp: string
  entry_source: EntrySource
  notes?: string
  entered_by?: string
  message: string
}

// Employee Today Status (for self-service)
export interface EmployeeTodayStatus {
  employee_id: string
  employee_name: string
  clock_in_time?: string
  clock_out_time?: string
  total_hours?: number
  status: string
}



