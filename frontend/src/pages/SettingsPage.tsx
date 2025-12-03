/**
 * Settings Page
 */

import { useState } from 'react'
import { Settings, Bell, Lock, Users, Clock, Database } from 'lucide-react'

export const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('general')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Configure system settings and preferences</p>
      </div>

      {/* Settings Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <div className="flex gap-6 overflow-x-auto">
            <button
              onClick={() => setActiveTab('general')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'general'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <Settings className="w-5 h-5" />
              General
            </button>
            <button
              onClick={() => setActiveTab('notifications')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'notifications'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <Bell className="w-5 h-5" />
              Notifications
            </button>
            <button
              onClick={() => setActiveTab('security')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'security'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <Lock className="w-5 h-5" />
              Security
            </button>
            <button
              onClick={() => setActiveTab('attendance')}
              className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'attendance'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              <Clock className="w-5 h-5" />
              Attendance
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* General Settings */}
          {activeTab === 'general' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Company Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Company Name
                    </label>
                    <input type="text" className="input" defaultValue="Test Company" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Time Zone
                    </label>
                    <select className="input">
                      <option>UTC+0 (GMT)</option>
                      <option>UTC+1 (CET)</option>
                      <option>UTC-5 (EST)</option>
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Company Address
                    </label>
                    <textarea className="input" rows={3} defaultValue="123 Business Street, City, Country" />
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Working Hours</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Work Week Start
                    </label>
                    <select className="input">
                      <option>Monday</option>
                      <option>Sunday</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Standard Hours Per Day
                    </label>
                    <input type="number" className="input" defaultValue="8" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Notifications Settings */}
          {activeTab === 'notifications' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Email Notifications</h3>
              
              <div className="space-y-3">
                <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                  <div>
                    <p className="font-medium text-gray-900">Late Arrivals</p>
                    <p className="text-sm text-gray-600">Get notified when employees arrive late</p>
                  </div>
                  <input type="checkbox" className="w-5 h-5 text-primary-600 rounded" defaultChecked />
                </label>

                <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                  <div>
                    <p className="font-medium text-gray-900">Absent Employees</p>
                    <p className="text-sm text-gray-600">Daily summary of absent employees</p>
                  </div>
                  <input type="checkbox" className="w-5 h-5 text-primary-600 rounded" defaultChecked />
                </label>

                <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                  <div>
                    <p className="font-medium text-gray-900">Correction Requests</p>
                    <p className="text-sm text-gray-600">New attendance correction requests</p>
                  </div>
                  <input type="checkbox" className="w-5 h-5 text-primary-600 rounded" defaultChecked />
                </label>

                <label className="flex items-center justify-between p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                  <div>
                    <p className="font-medium text-gray-900">Weekly Reports</p>
                    <p className="text-sm text-gray-600">Automated weekly attendance reports</p>
                  </div>
                  <input type="checkbox" className="w-5 h-5 text-primary-600 rounded" />
                </label>
              </div>
            </div>
          )}

          {/* Security Settings */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Password Policy</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Minimum Password Length
                    </label>
                    <input type="number" className="input" defaultValue="8" />
                  </div>
                  
                  <label className="flex items-center gap-3">
                    <input type="checkbox" className="w-5 h-5 text-primary-600 rounded" defaultChecked />
                    <span className="text-gray-900">Require special characters</span>
                  </label>
                  
                  <label className="flex items-center gap-3">
                    <input type="checkbox" className="w-5 h-5 text-primary-600 rounded" defaultChecked />
                    <span className="text-gray-900">Require numbers</span>
                  </label>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Management</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Session Timeout (minutes)
                    </label>
                    <input type="number" className="input" defaultValue="60" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Attendance Settings */}
          {activeTab === 'attendance' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Attendance Rules</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Late Arrival Threshold (minutes)
                    </label>
                    <input type="number" className="input" defaultValue="15" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Early Departure Threshold (minutes)
                    </label>
                    <input type="number" className="input" defaultValue="15" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Minimum Hours Required
                    </label>
                    <input type="number" className="input" defaultValue="8" step="0.5" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Auto Clock-Out After (hours)
                    </label>
                    <input type="number" className="input" defaultValue="12" />
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Card Settings</h3>
                <div className="space-y-3">
                  <label className="flex items-center gap-3">
                    <input type="checkbox" className="w-5 h-5 text-primary-600 rounded" defaultChecked />
                    <span className="text-gray-900">Allow multiple cards per employee</span>
                  </label>
                  
                  <label className="flex items-center gap-3">
                    <input type="checkbox" className="w-5 h-5 text-primary-600 rounded" defaultChecked />
                    <span className="text-gray-900">Require supervisor approval for corrections</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Save Button */}
          <div className="border-t border-gray-200 pt-6">
            <button className="btn btn-primary">
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}



