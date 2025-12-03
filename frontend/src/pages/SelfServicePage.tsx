/**
 * Employee Self-Service Kiosk page
 * Allows employees to clock in/out using their employee ID and PIN
 */

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import { AttendanceEventType, EmployeeTodayStatus } from '@/types'
import { cn, getErrorMessage } from '@/lib/utils'
import { LogIn, LogOut, Clock, User, AlertCircle, CheckCircle } from 'lucide-react'

export const SelfServicePage = () => {
  const [employeeId, setEmployeeId] = useState('')
  const [pin, setPin] = useState('')
  const [showStatus, setShowStatus] = useState(false)
  const [todayStatus, setTodayStatus] = useState<EmployeeTodayStatus | null>(null)
  const [reason, setReason] = useState('NFC card not working')
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  
  // Clear messages after timeout
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 5000)
      return () => clearTimeout(timer)
    }
  }, [successMessage])
  
  useEffect(() => {
    if (errorMessage) {
      const timer = setTimeout(() => setErrorMessage(''), 5000)
      return () => clearTimeout(timer)
    }
  }, [errorMessage])
  
  // Self clock mutation
  const selfClockMutation = useMutation({
    mutationFn: async (eventType: AttendanceEventType) => {
      const response = await axiosInstance.post(API_ENDPOINTS.EMPLOYEE_SELF_CLOCK, {
        employee_id: employeeId,
        pin: pin,
        event_type: eventType,
        reason: reason,
      })
      return response.data
    },
    onSuccess: (data) => {
      setSuccessMessage(data.message)
      setPin('')
      fetchTodayStatus()
    },
    onError: (error) => {
      setErrorMessage(getErrorMessage(error))
    },
  })
  
  // Fetch today's status
  const fetchTodayStatus = async () => {
    if (!employeeId || !pin || pin.length < 4) return
    
    try {
      const response = await axiosInstance.get<EmployeeTodayStatus>(
        `${API_ENDPOINTS.EMPLOYEE_TODAY_STATUS}?employee_no=${employeeId}&pin=${pin}`
      )
      setTodayStatus(response.data)
      setShowStatus(true)
      setErrorMessage('')
    } catch (error) {
      setErrorMessage(getErrorMessage(error))
      setShowStatus(false)
      setTodayStatus(null)
    }
  }
  
  const handleClockIn = () => {
    if (!employeeId || !pin || pin.length < 4) {
      setErrorMessage('Please enter your Employee ID and PIN')
      return
    }
    selfClockMutation.mutate(AttendanceEventType.IN)
  }
  
  const handleClockOut = () => {
    if (!employeeId || !pin || pin.length < 4) {
      setErrorMessage('Please enter your Employee ID and PIN')
      return
    }
    selfClockMutation.mutate(AttendanceEventType.OUT)
  }
  
  const reasons = [
    'NFC card not working',
    'Forgot card at home',
    'Reader malfunction',
    'Other',
  ]
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-full mb-4">
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Employee Self-Service</h1>
          <p className="text-gray-600 mt-1">Clock In/Out when NFC card is unavailable</p>
        </div>
        
        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-xl p-6">
          {/* Success Message */}
          {successMessage && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
              <span className="text-green-800 font-medium">{successMessage}</span>
            </div>
          )}
          
          {/* Error Message */}
          {errorMessage && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
              <span className="text-red-800">{errorMessage}</span>
            </div>
          )}
          
          {/* Form */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Employee ID
              </label>
              <input
                type="text"
                value={employeeId}
                onChange={(e) => {
                  setEmployeeId(e.target.value.toUpperCase())
                  setShowStatus(false)
                }}
                placeholder="e.g., EMP-001"
                className="input text-lg"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                PIN (4-6 digits)
              </label>
              <input
                type="password"
                value={pin}
                onChange={(e) => {
                  setPin(e.target.value)
                  setShowStatus(false)
                }}
                placeholder="••••"
                maxLength={6}
                className="input text-lg text-center tracking-widest"
                onBlur={fetchTodayStatus}
              />
            </div>
            
            {/* Today's Status */}
            {showStatus && todayStatus && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  Today's Status: {todayStatus.employee_name}
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Clocked In:</span>
                    <p className="font-medium">
                      {todayStatus.clock_in_time 
                        ? new Date(todayStatus.clock_in_time).toLocaleTimeString()
                        : '--:--'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Clocked Out:</span>
                    <p className="font-medium">
                      {todayStatus.clock_out_time 
                        ? new Date(todayStatus.clock_out_time).toLocaleTimeString()
                        : '--:--'}
                    </p>
                  </div>
                </div>
                {todayStatus.total_hours && (
                  <p className="mt-2 text-sm text-gray-600">
                    Total Hours: <span className="font-medium">{todayStatus.total_hours.toFixed(2)}</span>
                  </p>
                )}
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reason for manual entry
              </label>
              <select
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="input"
              >
                {reasons.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            
            {reason === 'Other' && (
              <input
                type="text"
                placeholder="Please specify reason..."
                onChange={(e) => setReason(e.target.value)}
                className="input"
              />
            )}
          </div>
          
          {/* Action Buttons */}
          <div className="mt-6 grid grid-cols-2 gap-4">
            <button
              onClick={handleClockIn}
              disabled={selfClockMutation.isPending}
              className={cn(
                'flex items-center justify-center gap-2 py-4 px-6 rounded-xl text-lg font-semibold transition-all',
                'bg-green-500 hover:bg-green-600 text-white shadow-lg hover:shadow-xl',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              <LogIn className="w-6 h-6" />
              Clock IN
            </button>
            
            <button
              onClick={handleClockOut}
              disabled={selfClockMutation.isPending}
              className={cn(
                'flex items-center justify-center gap-2 py-4 px-6 rounded-xl text-lg font-semibold transition-all',
                'bg-orange-500 hover:bg-orange-600 text-white shadow-lg hover:shadow-xl',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              <LogOut className="w-6 h-6" />
              Clock OUT
            </button>
          </div>
          
          {/* Loading State */}
          {selfClockMutation.isPending && (
            <div className="mt-4 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              <p className="text-gray-600 mt-2">Processing...</p>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Need help? Contact HR department</p>
          <p className="mt-1">
            <a href="/login" className="text-primary-600 hover:underline">
              Go to Admin Login →
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

