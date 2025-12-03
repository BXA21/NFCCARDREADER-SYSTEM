/**
 * Corrections & Approvals Page
 */

import { useState } from 'react'
import { FileEdit, CheckCircle, XCircle, Clock } from 'lucide-react'

export const CorrectionsPage = () => {
  const [requests] = useState([
    {
      id: '1',
      employeeName: 'John Smith',
      date: '2025-11-27',
      originalTime: '09:30',
      requestedTime: '09:00',
      reason: 'Forgot to clock in on time',
      status: 'PENDING',
      submittedAt: '2025-11-27 10:15'
    },
    {
      id: '2',
      employeeName: 'Sarah Johnson',
      date: '2025-11-26',
      originalTime: '17:45',
      requestedTime: '18:00',
      reason: 'Had to stay for urgent meeting',
      status: 'APPROVED',
      submittedAt: '2025-11-26 18:30'
    },
    {
      id: '3',
      employeeName: 'Mike Wilson',
      date: '2025-11-25',
      originalTime: '08:45',
      requestedTime: '08:30',
      reason: 'System error, was actually on time',
      status: 'REJECTED',
      submittedAt: '2025-11-25 09:00'
    }
  ])

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <span className="badge badge-warning">Pending</span>
      case 'APPROVED':
        return <span className="badge badge-success">Approved</span>
      case 'REJECTED':
        return <span className="badge badge-danger">Rejected</span>
      default:
        return <span className="badge badge-info">{status}</span>
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Corrections & Approvals</h1>
        <p className="text-gray-600 mt-1">Review and approve attendance correction requests</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending Requests</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">1</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Approved</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">1</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Rejected</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">1</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Requests Table */}
      <div className="card">
        <div className="border-b border-gray-200 pb-4 mb-4">
          <h2 className="text-xl font-semibold text-gray-900">All Correction Requests</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Employee</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Date</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Original Time</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Requested Time</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Reason</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((request) => (
                <tr key={request.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-primary-700 font-semibold">
                          {request.employeeName.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{request.employeeName}</p>
                        <p className="text-sm text-gray-500">{request.submittedAt}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-gray-900">{request.date}</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-gray-900">{request.originalTime}</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-gray-900 font-semibold">{request.requestedTime}</span>
                  </td>
                  <td className="px-4 py-4">
                    <p className="text-sm text-gray-600 max-w-xs">{request.reason}</p>
                  </td>
                  <td className="px-4 py-4">
                    {getStatusBadge(request.status)}
                  </td>
                  <td className="px-4 py-4">
                    {request.status === 'PENDING' && (
                      <div className="flex items-center gap-2">
                        <button className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors">
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    )}
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



