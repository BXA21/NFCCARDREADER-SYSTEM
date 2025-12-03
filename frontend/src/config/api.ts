/**
 * API configuration and base URL
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REFRESH: '/auth/refresh',
  LOGOUT: '/auth/logout',
  
  // Employees
  EMPLOYEES: '/employees',
  EMPLOYEE_DETAIL: (id: string) => `/employees/${id}`,
  
  // Cards
  ISSUE_CARD: (employeeId: string) => `/employees/${employeeId}/cards`,
  EMPLOYEE_CARDS: (employeeId: string) => `/employees/${employeeId}/cards`,
  REVOKE_CARD: (cardId: string) => `/cards/${cardId}/revoke`,
  MARK_CARD_LOST: (cardId: string) => `/cards/${cardId}/mark-lost`,
  
  // Shifts
  SHIFTS: '/shifts',
  SHIFT_DETAIL: (id: string) => `/shifts/${id}`,
  ASSIGN_SHIFT: (employeeId: string) => `/employees/${employeeId}/shifts`,
  EMPLOYEE_SHIFTS: (employeeId: string) => `/employees/${employeeId}/shifts`,
  
  // Attendance
  ATTENDANCE_EVENTS: '/attendance-events',
  MY_ATTENDANCE: '/attendance/me',
  ATTENDANCE_REPORT: '/attendance/report',
  ATTENDANCE_SUMMARY: '/attendance/summary',
  
  // Corrections
  CORRECTIONS: '/corrections',
  CORRECTION_DETAIL: (id: string) => `/corrections/${id}`,
  APPROVE_CORRECTION: (id: string) => `/corrections/${id}/approve`,
  REJECT_CORRECTION: (id: string) => `/corrections/${id}/reject`,
  
  // Export
  EXPORT_PAYROLL: '/export/payroll',
  
  // Devices
  DEVICES: '/devices',
  
  // Audit Logs
  AUDIT_LOGS: '/audit-logs',
  
  // Manual Operations
  MANUAL_CLOCK: '/manual/attendance/clock',
  MANUAL_ATTENDANCE_EDIT: (id: string) => `/manual/attendance/${id}`,
  MANUAL_ATTENDANCE_BULK: '/manual/attendance/bulk',
  MANUAL_LEAVE_TYPES: '/manual/leave/types',
  MANUAL_LEAVE: '/manual/leave',
  MANUAL_LEAVE_DETAIL: (id: string) => `/manual/leave/${id}`,
  MANUAL_EMPLOYEE_REGISTER: '/manual/employee/register-no-card',
  EMPLOYEE_SET_PIN: '/employee/set-pin',
  EMPLOYEE_SELF_CLOCK: '/employee/self-clock',
  EMPLOYEE_TODAY_STATUS: '/employee/today-status',
}



