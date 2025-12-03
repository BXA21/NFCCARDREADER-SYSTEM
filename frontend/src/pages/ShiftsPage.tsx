/**
 * Shifts & Schedules Management Page
 */

import { useState } from 'react'
import { Clock, Plus, Edit2, Trash2, Users } from 'lucide-react'

export const ShiftsPage = () => {
  const [shifts] = useState([
    {
      id: '1',
      name: 'Morning Shift',
      startTime: '08:00',
      endTime: '16:00',
      gracePeriod: 15,
      employeeCount: 24
    },
    {
      id: '2',
      name: 'Evening Shift',
      startTime: '16:00',
      endTime: '00:00',
      gracePeriod: 15,
      employeeCount: 18
    },
    {
      id: '3',
      name: 'Night Shift',
      startTime: '00:00',
      endTime: '08:00',
      gracePeriod: 15,
      employeeCount: 12
    }
  ])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Shifts & Schedules</h1>
          <p className="text-gray-600 mt-1">Manage work shifts and employee schedules</p>
        </div>
        <button className="btn btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Create Shift
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Shifts</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">3</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Schedules</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">54</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg. Grace Period</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">15m</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Shifts Table */}
      <div className="card">
        <div className="border-b border-gray-200 pb-4 mb-4">
          <h2 className="text-xl font-semibold text-gray-900">All Shifts</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Shift Name</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Start Time</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">End Time</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Grace Period</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Employees</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody>
              {shifts.map((shift) => (
                <tr key={shift.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                        <Clock className="w-5 h-5 text-primary-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{shift.name}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-gray-900">{shift.startTime}</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="text-gray-900">{shift.endTime}</span>
                  </td>
                  <td className="px-4 py-4">
                    <span className="badge badge-info">{shift.gracePeriod} min</span>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-900">{shift.employeeCount}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-2">
                      <button className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
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



