/**
 * Manual Operations page for HR to manually manage attendance and leave
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import { 
  Employee, 
  LeaveType, 
  LeaveRecord, 
  AttendanceEventType, 
  LeaveStatus,
  PaginatedResponse 
} from '@/types'
import { formatDateTime, formatDate, cn, getErrorMessage } from '@/lib/utils'
import { 
  Clock, 
  UserPlus, 
  Calendar, 
  Edit3, 
  Trash2, 
  Users,
  FileText,
  CheckCircle,
  XCircle,
  AlertCircle,
  Search,
  Plus
} from 'lucide-react'

// Tab types
type TabType = 'attendance' | 'leave' | 'register' | 'bulk'

export const ManualOperationsPage = () => {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<TabType>('attendance')
  
  // Manual Attendance State
  const [selectedEmployeeId, setSelectedEmployeeId] = useState('')
  const [eventType, setEventType] = useState<'IN' | 'OUT'>('IN')
  const [eventDate, setEventDate] = useState(() => new Date().toISOString().split('T')[0])
  const [eventTime, setEventTime] = useState(() => {
    const now = new Date()
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  })
  const [attendanceNotes, setAttendanceNotes] = useState('')
  
  // Leave State
  const [leaveEmployeeId, setLeaveEmployeeId] = useState('')
  const [leaveTypeId, setLeaveTypeId] = useState('')
  const [leaveStartDate, setLeaveStartDate] = useState('')
  const [leaveEndDate, setLeaveEndDate] = useState('')
  const [leaveNotes, setLeaveNotes] = useState('')
  const [leaveStatus, setLeaveStatus] = useState<LeaveStatus>(LeaveStatus.APPROVED)
  
  // Register State
  const [regEmployeeNo, setRegEmployeeNo] = useState('')
  const [regFullName, setRegFullName] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regDepartment, setRegDepartment] = useState('')
  const [regPosition, setRegPosition] = useState('')
  const [regPhone, setRegPhone] = useState('')
  const [regHireDate, setRegHireDate] = useState('')
  const [regPin, setRegPin] = useState('')
  
  // Fetch employees for dropdown
  const { data: employees } = useQuery({
    queryKey: ['employees-all'],
    queryFn: async () => {
      const response = await axiosInstance.get<PaginatedResponse<Employee>>(
        `${API_ENDPOINTS.EMPLOYEES}?page_size=100&status=ACTIVE`
      )
      return response.data.items
    },
  })
  
  // Fetch leave types
  const { data: leaveTypes } = useQuery({
    queryKey: ['leave-types'],
    queryFn: async () => {
      const response = await axiosInstance.get<LeaveType[]>(API_ENDPOINTS.MANUAL_LEAVE_TYPES)
      return response.data
    },
  })
  
  // Fetch leave records
  const { data: leaveRecords, refetch: refetchLeave } = useQuery({
    queryKey: ['leave-records'],
    queryFn: async () => {
      const response = await axiosInstance.get<PaginatedResponse<LeaveRecord>>(
        `${API_ENDPOINTS.MANUAL_LEAVE}?page_size=50`
      )
      return response.data.items
    },
  })
  
  // Manual clock mutation
  const manualClockMutation = useMutation({
    mutationFn: async (data: {
      employee_id: string
      event_type: 'IN' | 'OUT'
      event_date: string
      event_time: string
      notes?: string
    }) => {
      const response = await axiosInstance.post(API_ENDPOINTS.MANUAL_CLOCK, data)
      return response.data
    },
    onSuccess: (data) => {
      alert(`✅ ${data.message}`)
      setAttendanceNotes('')
      queryClient.invalidateQueries({ queryKey: ['attendance'] })
    },
    onError: (error) => {
      alert(`❌ Error: ${getErrorMessage(error)}`)
    },
  })
  
  // Create leave mutation
  const createLeaveMutation = useMutation({
    mutationFn: async (data: {
      employee_id: string
      leave_type_id: string
      start_date: string
      end_date: string
      notes?: string
      status: LeaveStatus
    }) => {
      const response = await axiosInstance.post(API_ENDPOINTS.MANUAL_LEAVE, data)
      return response.data
    },
    onSuccess: () => {
      alert('✅ Leave record created successfully!')
      setLeaveNotes('')
      setLeaveStartDate('')
      setLeaveEndDate('')
      refetchLeave()
    },
    onError: (error) => {
      alert(`❌ Error: ${getErrorMessage(error)}`)
    },
  })
  
  // Delete leave mutation
  const deleteLeaveMutation = useMutation({
    mutationFn: async (id: string) => {
      await axiosInstance.delete(API_ENDPOINTS.MANUAL_LEAVE_DETAIL(id))
    },
    onSuccess: () => {
      refetchLeave()
    },
  })
  
  // Register employee mutation
  const registerMutation = useMutation({
    mutationFn: async () => {
      const params = new URLSearchParams({
        employee_no: regEmployeeNo,
        full_name: regFullName,
        email: regEmail,
        department: regDepartment,
        hire_date: regHireDate,
      })
      if (regPosition) params.append('position', regPosition)
      if (regPhone) params.append('phone', regPhone)
      if (regPin) params.append('pin', regPin)
      
      const response = await axiosInstance.post(
        `${API_ENDPOINTS.MANUAL_EMPLOYEE_REGISTER}?${params.toString()}`
      )
      return response.data
    },
    onSuccess: (data) => {
      alert(`✅ ${data.message}`)
      setRegEmployeeNo('')
      setRegFullName('')
      setRegEmail('')
      setRegDepartment('')
      setRegPosition('')
      setRegPhone('')
      setRegHireDate('')
      setRegPin('')
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
    onError: (error) => {
      alert(`❌ Error: ${getErrorMessage(error)}`)
    },
  })
  
  // Handle manual clock submission
  const handleManualClock = () => {
    if (!selectedEmployeeId) {
      alert('Please select an employee')
      return
    }
    
    manualClockMutation.mutate({
      employee_id: selectedEmployeeId,
      event_type: eventType,
      event_date: eventDate,
      event_time: eventTime,
      notes: attendanceNotes || undefined,
    })
  }
  
  // Handle leave creation
  const handleCreateLeave = () => {
    if (!leaveEmployeeId || !leaveTypeId || !leaveStartDate || !leaveEndDate) {
      alert('Please fill in all required fields')
      return
    }
    
    createLeaveMutation.mutate({
      employee_id: leaveEmployeeId,
      leave_type_id: leaveTypeId,
      start_date: leaveStartDate,
      end_date: leaveEndDate,
      notes: leaveNotes || undefined,
      status: leaveStatus,
    })
  }
  
  // Handle employee registration
  const handleRegisterEmployee = () => {
    if (!regEmployeeNo || !regFullName || !regEmail || !regDepartment || !regHireDate) {
      alert('Please fill in all required fields')
      return
    }
    
    registerMutation.mutate()
  }
  
  const tabs = [
    { id: 'attendance' as TabType, label: 'Manual Attendance', icon: Clock },
    { id: 'leave' as TabType, label: 'Leave Management', icon: Calendar },
    { id: 'register' as TabType, label: 'Register Employee', icon: UserPlus },
    { id: 'bulk' as TabType, label: 'Bulk Operations', icon: Users },
  ]

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Manual Operations</h1>
        <p className="text-gray-600 mt-1">
          HR tools for manual attendance entry, leave management, and employee registration
        </p>
      </div>

      {/* Tabs */}
      <div className="card mb-6">
        <div className="flex flex-wrap gap-2 border-b border-gray-200 pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'attendance' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-primary-600" />
            Manual Attendance Entry
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Employee *
              </label>
              <select
                value={selectedEmployeeId}
                onChange={(e) => setSelectedEmployeeId(e.target.value)}
                className="input"
              >
                <option value="">-- Select Employee --</option>
                {employees?.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.full_name} ({emp.employee_no}) - {emp.department}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Action *
              </label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="eventType"
                    value="IN"
                    checked={eventType === 'IN'}
                    onChange={() => setEventType('IN')}
                    className="text-primary-600"
                  />
                  <span className="text-green-600 font-medium">🟢 Clock IN</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    name="eventType"
                    value="OUT"
                    checked={eventType === 'OUT'}
                    onChange={() => setEventType('OUT')}
                    className="text-primary-600"
                  />
                  <span className="text-orange-600 font-medium">🔴 Clock OUT</span>
                </label>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date *
              </label>
              <input
                type="date"
                value={eventDate}
                onChange={(e) => setEventDate(e.target.value)}
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time *
              </label>
              <input
                type="time"
                value={eventTime}
                onChange={(e) => setEventTime(e.target.value)}
                className="input"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reason / Notes
              </label>
              <input
                type="text"
                value={attendanceNotes}
                onChange={(e) => setAttendanceNotes(e.target.value)}
                placeholder="e.g., Forgot NFC card, Reader malfunction..."
                className="input"
              />
            </div>
          </div>
          
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleManualClock}
              disabled={manualClockMutation.isPending}
              className="btn btn-primary"
            >
              {manualClockMutation.isPending ? 'Submitting...' : 'Submit Manual Entry'}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'leave' && (
        <div className="space-y-6">
          {/* Create Leave Form */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary-600" />
              Create Leave Record
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Employee *
                </label>
                <select
                  value={leaveEmployeeId}
                  onChange={(e) => setLeaveEmployeeId(e.target.value)}
                  className="input"
                >
                  <option value="">-- Select Employee --</option>
                  {employees?.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.full_name} ({emp.employee_no})
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Leave Type *
                </label>
                <select
                  value={leaveTypeId}
                  onChange={(e) => setLeaveTypeId(e.target.value)}
                  className="input"
                >
                  <option value="">-- Select Type --</option>
                  {leaveTypes?.map((lt) => (
                    <option key={lt.id} value={lt.id}>
                      {lt.name} {lt.is_paid ? '(Paid)' : '(Unpaid)'}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={leaveStatus}
                  onChange={(e) => setLeaveStatus(e.target.value as LeaveStatus)}
                  className="input"
                >
                  <option value={LeaveStatus.APPROVED}>Approved</option>
                  <option value={LeaveStatus.PENDING}>Pending</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date *
                </label>
                <input
                  type="date"
                  value={leaveStartDate}
                  onChange={(e) => setLeaveStartDate(e.target.value)}
                  className="input"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date *
                </label>
                <input
                  type="date"
                  value={leaveEndDate}
                  onChange={(e) => setLeaveEndDate(e.target.value)}
                  className="input"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes
                </label>
                <input
                  type="text"
                  value={leaveNotes}
                  onChange={(e) => setLeaveNotes(e.target.value)}
                  placeholder="Optional notes..."
                  className="input"
                />
              </div>
            </div>
            
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleCreateLeave}
                disabled={createLeaveMutation.isPending}
                className="btn btn-primary"
              >
                {createLeaveMutation.isPending ? 'Creating...' : 'Create Leave Record'}
              </button>
            </div>
          </div>
          
          {/* Leave Records Table */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Recent Leave Records
            </h3>
            
            {leaveRecords && leaveRecords.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Days</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {leaveRecords.map((record) => (
                      <tr key={record.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <div className="font-medium text-gray-900">{record.employee_name}</div>
                          <div className="text-sm text-gray-500">{record.employee_no}</div>
                        </td>
                        <td className="px-4 py-3 text-sm">{record.leave_type_name}</td>
                        <td className="px-4 py-3 text-sm">
                          {formatDate(record.start_date)} - {formatDate(record.end_date)}
                        </td>
                        <td className="px-4 py-3 text-sm font-medium">{record.days_count}</td>
                        <td className="px-4 py-3">
                          <span className={cn(
                            'badge',
                            record.status === LeaveStatus.APPROVED && 'badge-success',
                            record.status === LeaveStatus.PENDING && 'badge-warning',
                            record.status === LeaveStatus.REJECTED && 'badge-danger',
                            record.status === LeaveStatus.CANCELLED && 'badge-secondary'
                          )}>
                            {record.status}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => {
                              if (confirm('Delete this leave record?')) {
                                deleteLeaveMutation.mutate(record.id)
                              }
                            }}
                            className="text-red-600 hover:text-red-800"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No leave records found</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'register' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-primary-600" />
            Register Employee (Without NFC Card)
          </h2>
          
          <p className="text-sm text-gray-600 mb-4">
            Register employees who don't need NFC cards or will have cards assigned later.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Employee Number * <span className="text-gray-400">(e.g., EMP-001)</span>
              </label>
              <input
                type="text"
                value={regEmployeeNo}
                onChange={(e) => setRegEmployeeNo(e.target.value)}
                placeholder="EMP-001"
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <input
                type="text"
                value={regFullName}
                onChange={(e) => setRegFullName(e.target.value)}
                placeholder="John Doe"
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email *
              </label>
              <input
                type="email"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                placeholder="john.doe@company.com"
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Department *
              </label>
              <select
                value={regDepartment}
                onChange={(e) => setRegDepartment(e.target.value)}
                className="input"
              >
                <option value="">-- Select Department --</option>
                <option value="IT">IT</option>
                <option value="HR">HR</option>
                <option value="Finance">Finance</option>
                <option value="Operations">Operations</option>
                <option value="Marketing">Marketing</option>
                <option value="Sales">Sales</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Position / Role
              </label>
              <input
                type="text"
                value={regPosition}
                onChange={(e) => setRegPosition(e.target.value)}
                placeholder="Software Engineer"
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone
              </label>
              <input
                type="tel"
                value={regPhone}
                onChange={(e) => setRegPhone(e.target.value)}
                placeholder="+1 234 567 8900"
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hire Date *
              </label>
              <input
                type="date"
                value={regHireDate}
                onChange={(e) => setRegHireDate(e.target.value)}
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Self-Service PIN <span className="text-gray-400">(4-6 digits)</span>
              </label>
              <input
                type="password"
                value={regPin}
                onChange={(e) => setRegPin(e.target.value)}
                placeholder="••••"
                maxLength={6}
                className="input"
              />
              <p className="text-xs text-gray-500 mt-1">
                Optional: Set a PIN for employee self-service clock in/out
              </p>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">NFC Card Options:</h4>
            <div className="text-sm text-blue-800 space-y-1">
              <p>• NFC card can be assigned later from the Employees page</p>
              <p>• Employee can use self-service clock with PIN if set</p>
              <p>• HR can manually clock employee in/out anytime</p>
            </div>
          </div>
          
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleRegisterEmployee}
              disabled={registerMutation.isPending}
              className="btn btn-primary"
            >
              {registerMutation.isPending ? 'Registering...' : 'Register Employee'}
            </button>
          </div>
        </div>
      )}

      {activeTab === 'bulk' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-primary-600" />
            Bulk Operations
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Bulk Clock In/Out */}
            <div className="p-4 border border-gray-200 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">
                Mark Multiple Employees Present
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Use this for company events, meetings, etc.
              </p>
              <button className="btn btn-secondary w-full">
                Select Employees & Clock In
              </button>
            </div>
            
            {/* Import CSV */}
            <div className="p-4 border border-gray-200 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">
                Import from CSV/Excel
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Import historical attendance data.
              </p>
              <button className="btn btn-secondary w-full" disabled>
                Upload File (Coming Soon)
              </button>
            </div>
            
            {/* Export */}
            <div className="p-4 border border-gray-200 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">
                Export Attendance Records
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Download attendance data as CSV.
              </p>
              <button className="btn btn-secondary w-full" disabled>
                Export (Coming Soon)
              </button>
            </div>
            
            {/* Department-wide Leave */}
            <div className="p-4 border border-gray-200 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">
                Department-wide Leave
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Mark entire department as on leave (holiday, closure).
              </p>
              <button className="btn btn-secondary w-full" disabled>
                Mark Department Leave (Coming Soon)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

