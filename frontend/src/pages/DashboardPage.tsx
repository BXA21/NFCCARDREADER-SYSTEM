/**
 * Dashboard page with live attendance feed and summary statistics
 */

import { useQuery } from '@tanstack/react-query'
import { useState, useEffect, useRef } from 'react'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import { AttendanceSummary } from '@/types'
import { Users, Clock, AlertCircle, Calendar, Wifi, WifiOff, LogIn, LogOut } from 'lucide-react'
import { formatDate, formatDateTime, cn } from '@/lib/utils'

interface LiveAttendanceEvent {
  event_type: 'IN' | 'OUT'
  employee_name: string
  employee_no: string
  department: string
  timestamp: string
  device_id: string
  message: string
  entry_source?: 'NFC' | 'MANUAL_HR' | 'MANUAL_EMPLOYEE' | 'BULK_IMPORT' | 'SYSTEM'
  notes?: string
}

// Entry source display configuration
const entrySourceConfig: Record<string, { label: string; color: string; bgColor: string; icon: string }> = {
  NFC: { label: 'NFC', color: 'text-blue-700', bgColor: 'bg-blue-100', icon: '🔵' },
  MANUAL_HR: { label: 'HR Manual', color: 'text-purple-700', bgColor: 'bg-purple-100', icon: '🟣' },
  MANUAL_EMPLOYEE: { label: 'Self-Service', color: 'text-orange-700', bgColor: 'bg-orange-100', icon: '🟠' },
  BULK_IMPORT: { label: 'Bulk Import', color: 'text-gray-700', bgColor: 'bg-gray-100', icon: '⚪' },
  SYSTEM: { label: 'System', color: 'text-gray-700', bgColor: 'bg-gray-100', icon: '⚙️' },
}

export const DashboardPage = () => {
  const [liveEvents, setLiveEvents] = useState<LiveAttendanceEvent[]>([])
  const [wsConnected, setWsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Fetch today's attendance summary
  const { data: summary, isLoading, refetch: refetchSummary } = useQuery({
    queryKey: ['attendance-summary', new Date().toISOString().split('T')[0]],
    queryFn: async () => {
      const today = new Date().toISOString().split('T')[0]
      const response = await axiosInstance.get<AttendanceSummary>(
        `${API_ENDPOINTS.ATTENDANCE_SUMMARY}?target_date=${today}`
      )
      return response.data
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      // Get WebSocket URL from API base URL
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const apiHost = import.meta.env.VITE_API_BASE_URL?.replace(/^https?:\/\//, '').replace(/\/api\/v1$/, '') || 'localhost:8000'
      const wsUrl = `${wsProtocol}//${apiHost}/ws/attendance`
      
      console.log('[WS] Connecting to:', wsUrl)
      
      try {
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
          console.log('[WS] Connected to attendance feed')
          setWsConnected(true)
          
          // Clear any pending reconnect
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
            reconnectTimeoutRef.current = null
          }
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            console.log('[WS] Received:', data.type)
            
            if (data.type === 'attendance_event') {
              // Add new event to the live feed
              setLiveEvents(prev => {
                const newEvents = [data.data, ...prev].slice(0, 20) // Keep last 20 events
                return newEvents
              })
              
              // Refetch summary to update stats
              refetchSummary()
            } else if (data.type === 'ping') {
              // Respond to server ping with pong
              ws.send('ping')
            }
          } catch (e) {
            console.error('[WS] Error parsing message:', e)
          }
        }

        ws.onclose = () => {
          console.log('[WS] Disconnected')
          setWsConnected(false)
          
          // Attempt to reconnect after 3 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('[WS] Attempting to reconnect...')
            connectWebSocket()
          }, 3000)
        }

        ws.onerror = (error) => {
          console.error('[WS] Error:', error)
          setWsConnected(false)
        }
      } catch (error) {
        console.error('[WS] Failed to create WebSocket:', error)
        setWsConnected(false)
        
        // Retry connection
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000)
      }
    }

    connectWebSocket()

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [refetchSummary])

  // Send keepalive ping every 25 seconds
  useEffect(() => {
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping')
      }
    }, 25000)

    return () => clearInterval(pingInterval)
  }, [])

  const stats = [
    {
      title: 'Total Employees',
      value: summary?.total_employees || 0,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      title: 'Present Today',
      value: summary?.present_count || 0,
      icon: Clock,
      color: 'bg-green-500',
    },
    {
      title: 'Absent Today',
      value: summary?.absent_count || 0,
      icon: AlertCircle,
      color: 'bg-red-500',
    },
    {
      title: 'Late Arrivals',
      value: summary?.late_count || 0,
      icon: Calendar,
      color: 'bg-yellow-500',
    },
  ]

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Overview for {formatDate(new Date().toISOString())}
          </p>
        </div>
        
        {/* Connection Status */}
        <div className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium',
          wsConnected 
            ? 'bg-green-100 text-green-700' 
            : 'bg-red-100 text-red-700'
        )}>
          {wsConnected ? (
            <>
              <Wifi className="w-4 h-4" />
              <span>Live</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4" />
              <span>Connecting...</span>
            </>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <div key={stat.title} className="card">
              <div className="flex items-center">
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Attendance Feed - Takes 2 columns */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <span className={cn(
                'w-2 h-2 rounded-full',
                wsConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
              )} />
              Live Attendance Feed
            </h3>
            <span className="text-sm text-gray-500">
              {liveEvents.length > 0 ? `${liveEvents.length} recent events` : 'Waiting for activity...'}
            </span>
          </div>

          <div className="space-y-3 max-h-[500px] overflow-y-auto">
            {liveEvents.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Clock className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg font-medium">No recent attendance events</p>
                <p className="text-sm mt-1">
                  Events will appear here in real-time when employees tap their NFC cards or clock in manually
                </p>
              </div>
            ) : (
              liveEvents.map((event, index) => {
                const sourceConfig = entrySourceConfig[event.entry_source || 'NFC']
                return (
                <div
                  key={`${event.employee_no}-${event.timestamp}-${index}`}
                  className={cn(
                    'p-4 rounded-lg border-2 transition-all duration-300',
                    event.event_type === 'IN'
                      ? 'bg-green-50 border-green-200 hover:border-green-300'
                      : 'bg-orange-50 border-orange-200 hover:border-orange-300',
                    index === 0 && 'ring-2 ring-offset-2',
                    index === 0 && event.event_type === 'IN' ? 'ring-green-400' : index === 0 ? 'ring-orange-400' : ''
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'p-2 rounded-full',
                        event.event_type === 'IN' ? 'bg-green-200' : 'bg-orange-200'
                      )}>
                        {event.event_type === 'IN' ? (
                          <LogIn className="w-5 h-5 text-green-700" />
                        ) : (
                          <LogOut className="w-5 h-5 text-orange-700" />
                        )}
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">{event.employee_name}</p>
                        <p className="text-sm text-gray-600">
                          {event.employee_no} • {event.department}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={cn(
                        'text-sm font-semibold',
                        event.event_type === 'IN' ? 'text-green-700' : 'text-orange-700'
                      )}>
                        {event.event_type === 'IN' ? '🟢 Clock IN' : '🔴 Clock OUT'}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </p>
                      {/* Entry Source Badge */}
                      <span className={cn(
                        'inline-flex items-center gap-1 mt-1 px-2 py-0.5 rounded-full text-xs font-medium',
                        sourceConfig.bgColor,
                        sourceConfig.color
                      )}>
                        {sourceConfig.icon} {sourceConfig.label}
                      </span>
                    </div>
                  </div>
                  <p className={cn(
                    'mt-2 text-sm',
                    event.event_type === 'IN' ? 'text-green-700' : 'text-orange-700'
                  )}>
                    {event.message}
                  </p>
                  {/* Show notes for manual entries */}
                  {event.notes && (
                    <p className="mt-1 text-xs text-gray-500 italic">
                      📝 {event.notes}
                    </p>
                  )}
                </div>
              )})
            )}
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Today's Summary */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Today's Summary
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Present</span>
                <span className="font-semibold text-green-600">
                  {summary?.present_count || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Absent</span>
                <span className="font-semibold text-red-600">
                  {summary?.absent_count || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Late</span>
                <span className="font-semibold text-yellow-600">
                  {summary?.late_count || 0}
                </span>
              </div>
              <div className="flex justify-between items-center border-t pt-3">
                <span className="text-gray-900 font-medium">Total</span>
                <span className="font-bold text-gray-900">
                  {summary?.total_employees || 0}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Quick Actions
            </h3>
            <div className="space-y-3">
              <a
                href="/manual"
                className="block px-4 py-3 bg-primary-50 hover:bg-primary-100 rounded-lg transition-colors border border-primary-200"
              >
                <p className="font-medium text-primary-900">📋 Manual Clock In/Out</p>
                <p className="text-sm text-primary-700">HR manual attendance entry</p>
              </a>
              <a
                href="/manual"
                className="block px-4 py-3 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors border border-purple-200"
              >
                <p className="font-medium text-purple-900">📅 Add Leave Record</p>
                <p className="text-sm text-purple-700">Record employee leave</p>
              </a>
              <a
                href="/employees"
                className="block px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <p className="font-medium text-gray-900">Manage Employees</p>
                <p className="text-sm text-gray-600">Add, edit, or view employees</p>
              </a>
              <a
                href="/attendance"
                className="block px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <p className="font-medium text-gray-900">View Attendance</p>
                <p className="text-sm text-gray-600">Check attendance records</p>
              </a>
              <a
                href="/reports"
                className="block px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <p className="font-medium text-gray-900">Generate Reports</p>
                <p className="text-sm text-gray-600">Export attendance data</p>
              </a>
            </div>
          </div>
          
          {/* Self-Service Link */}
          <div className="card bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200">
            <h3 className="text-sm font-semibold text-amber-800 mb-2">
              🔗 Employee Self-Service
            </h3>
            <p className="text-xs text-amber-700 mb-3">
              Share this link with employees who need to clock in/out without NFC cards
            </p>
            <a
              href="/self-service"
              target="_blank"
              className="block text-center px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Open Self-Service Kiosk →
            </a>
          </div>

          {/* Connection Info */}
          <div className="card bg-gray-50">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">
              System Status
            </h3>
            <div className="text-xs text-gray-600 space-y-1">
              <p>WebSocket: {wsConnected ? '✅ Connected' : '⏳ Reconnecting...'}</p>
              <p>Last refresh: {new Date().toLocaleTimeString()}</p>
              <p>Auto-refresh: Every 30 seconds</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
