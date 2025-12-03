/**
 * Audit Logs Page
 */

import { useState } from 'react'
import { Shield, User, FileText, Clock } from 'lucide-react'

export const AuditLogsPage = () => {
  const [logs] = useState([
    {
      id: '1',
      action: 'USER_LOGIN',
      actor: 'admin',
      description: 'User logged in successfully',
      timestamp: '2025-11-27 09:15:23',
      ipAddress: '192.168.1.100',
      status: 'SUCCESS'
    },
    {
      id: '2',
      action: 'EMPLOYEE_CREATED',
      actor: 'admin',
      description: 'Created new employee: John Smith',
      timestamp: '2025-11-27 09:10:15',
      ipAddress: '192.168.1.100',
      status: 'SUCCESS'
    },
    {
      id: '3',
      action: 'CARD_ISSUED',
      actor: 'admin',
      description: 'Issued NFC card to employee: Sarah Johnson',
      timestamp: '2025-11-27 09:05:45',
      ipAddress: '192.168.1.100',
      status: 'SUCCESS'
    },
    {
      id: '4',
      action: 'ATTENDANCE_RECORDED',
      actor: 'SYSTEM',
      description: 'Attendance recorded for employee: Mike Wilson',
      timestamp: '2025-11-27 08:30:12',
      ipAddress: '192.168.1.50',
      status: 'SUCCESS'
    },
    {
      id: '5',
      action: 'CORRECTION_APPROVED',
      actor: 'supervisor',
      description: 'Approved correction request from Sarah Johnson',
      timestamp: '2025-11-27 08:15:30',
      ipAddress: '192.168.1.101',
      status: 'SUCCESS'
    },
    {
      id: '6',
      action: 'LOGIN_FAILED',
      actor: 'unknown',
      description: 'Failed login attempt',
      timestamp: '2025-11-27 07:45:10',
      ipAddress: '192.168.1.200',
      status: 'FAILED'
    }
  ])

  const getActionIcon = (action: string) => {
    if (action.includes('USER') || action.includes('LOGIN')) {
      return <User className="w-5 h-5" />
    } else if (action.includes('EMPLOYEE') || action.includes('CARD')) {
      return <FileText className="w-5 h-5" />
    } else if (action.includes('ATTENDANCE') || action.includes('CORRECTION')) {
      return <Clock className="w-5 h-5" />
    } else {
      return <Shield className="w-5 h-5" />
    }
  }

  const getStatusBadge = (status: string) => {
    return status === 'SUCCESS' 
      ? <span className="badge badge-success">Success</span>
      : <span className="badge badge-danger">Failed</span>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Audit Logs</h1>
        <p className="text-gray-600 mt-1">Track all system activities and user actions</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Actions</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">1,234</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Today's Logs</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">48</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Users</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">3</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <User className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Failed Attempts</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">1</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Action Type
            </label>
            <select className="input">
              <option value="">All Actions</option>
              <option value="USER">User Actions</option>
              <option value="EMPLOYEE">Employee Actions</option>
              <option value="ATTENDANCE">Attendance Actions</option>
              <option value="CARD">Card Actions</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Actor
            </label>
            <select className="input">
              <option value="">All Users</option>
              <option value="admin">Admin</option>
              <option value="supervisor">Supervisor</option>
              <option value="SYSTEM">System</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date From
            </label>
            <input type="date" className="input" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date To
            </label>
            <input type="date" className="input" />
          </div>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="card">
        <div className="border-b border-gray-200 pb-4 mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Action</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Actor</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Description</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Timestamp</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">IP Address</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        log.status === 'SUCCESS' ? 'bg-blue-100 text-blue-600' : 'bg-red-100 text-red-600'
                      }`}>
                        {getActionIcon(log.action)}
                      </div>
                      <span className="font-medium text-gray-900">{log.action.replace('_', ' ')}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      log.actor === 'SYSTEM' 
                        ? 'bg-gray-100 text-gray-700'
                        : 'bg-primary-100 text-primary-700'
                    }`}>
                      {log.actor}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <p className="text-sm text-gray-900">{log.description}</p>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-gray-600">{log.timestamp}</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-sm text-gray-600 font-mono">{log.ipAddress}</span>
                  </td>
                  <td className="px-4 py-4">
                    {getStatusBadge(log.status)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}



