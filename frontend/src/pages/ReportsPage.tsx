/**
 * Reports & Export Page
 */

import { useState } from 'react'
import { Download, Calendar, FileText, TrendingUp } from 'lucide-react'

export const ReportsPage = () => {
  const [reportType, setReportType] = useState('daily')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports & Export</h1>
        <p className="text-gray-600 mt-1">Generate and export attendance reports</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Today's Present</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">48</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Today's Absent</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">6</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">On Leave</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">2</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Late Arrivals</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">3</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Report Generation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Report Builder */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Generate Report</h2>
          
          <div className="space-y-4">
            {/* Report Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Report Type
              </label>
              <select 
                className="input"
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
              >
                <option value="daily">Daily Report</option>
                <option value="weekly">Weekly Report</option>
                <option value="monthly">Monthly Report</option>
                <option value="custom">Custom Date Range</option>
                <option value="payroll">Payroll Report</option>
              </select>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <input type="date" className="input" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date
                </label>
                <input type="date" className="input" />
              </div>
            </div>

            {/* Export Format */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Export Format
              </label>
              <div className="flex gap-3">
                <button className="flex-1 py-3 px-4 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors">
                  <FileText className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">CSV</span>
                </button>
                <button className="flex-1 py-3 px-4 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors">
                  <FileText className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">Excel</span>
                </button>
                <button className="flex-1 py-3 px-4 border-2 border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors">
                  <FileText className="w-5 h-5 mx-auto mb-1 text-gray-600" />
                  <span className="text-sm font-medium text-gray-700">PDF</span>
                </button>
              </div>
            </div>

            {/* Generate Button */}
            <button className="w-full btn btn-primary flex items-center justify-center gap-2">
              <Download className="w-5 h-5" />
              Generate & Download Report
            </button>
          </div>
        </div>

        {/* Quick Reports */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Reports</h2>
          
          <div className="space-y-3">
            <button className="w-full p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg hover:shadow-md transition-shadow text-left">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                    <Calendar className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">Today's Attendance</p>
                    <p className="text-sm text-gray-600">Current day summary</p>
                  </div>
                </div>
                <Download className="w-5 h-5 text-blue-600" />
              </div>
            </button>

            <button className="w-full p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-lg hover:shadow-md transition-shadow text-left">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">Weekly Summary</p>
                    <p className="text-sm text-gray-600">Last 7 days</p>
                  </div>
                </div>
                <Download className="w-5 h-5 text-green-600" />
              </div>
            </button>

            <button className="w-full p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg hover:shadow-md transition-shadow text-left">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
                    <FileText className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">Monthly Report</p>
                    <p className="text-sm text-gray-600">Current month</p>
                  </div>
                </div>
                <Download className="w-5 h-5 text-purple-600" />
              </div>
            </button>

            <button className="w-full p-4 bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg hover:shadow-md transition-shadow text-left">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
                    <Download className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">Payroll Export</p>
                    <p className="text-sm text-gray-600">Ready for payroll</p>
                  </div>
                </div>
                <Download className="w-5 h-5 text-orange-600" />
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}



