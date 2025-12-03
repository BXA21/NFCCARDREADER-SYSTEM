/**
 * Sidebar navigation component
 */

import { NavLink } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { 
  LayoutDashboard, 
  Users, 
  Clock, 
  Edit3, 
  Calendar, 
  FileText, 
  Download, 
  Settings,
  FileCheck,
  ClipboardEdit,
  UserCircle
} from 'lucide-react'
import { UserRole } from '@/types'

export const Sidebar = () => {
  const { user } = useAuth()

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', roles: [UserRole.EMPLOYEE, UserRole.SUPERVISOR, UserRole.HR_ADMIN] },
    { to: '/employees', icon: Users, label: 'Employees', roles: [UserRole.HR_ADMIN] },
    { to: '/attendance', icon: Clock, label: 'Attendance', roles: [UserRole.EMPLOYEE, UserRole.SUPERVISOR, UserRole.HR_ADMIN] },
    { to: '/manual', icon: ClipboardEdit, label: 'Manual Operations', roles: [UserRole.HR_ADMIN] },
    { to: '/corrections', icon: Edit3, label: 'Corrections', roles: [UserRole.EMPLOYEE, UserRole.SUPERVISOR, UserRole.HR_ADMIN] },
    { to: '/shifts', icon: Calendar, label: 'Shifts & Schedules', roles: [UserRole.HR_ADMIN] },
    { to: '/reports', icon: FileText, label: 'Reports', roles: [UserRole.SUPERVISOR, UserRole.HR_ADMIN] },
    { to: '/export', icon: Download, label: 'Export', roles: [UserRole.HR_ADMIN] },
    { to: '/settings', icon: Settings, label: 'Settings', roles: [UserRole.HR_ADMIN] },
    { to: '/audit-logs', icon: FileCheck, label: 'Audit Logs', roles: [UserRole.HR_ADMIN] },
  ]

  // Filter nav items based on user role
  const filteredNavItems = navItems.filter(item => 
    user && item.roles.includes(user.role)
  )

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-gray-200">
        <h1 className="text-xl font-bold text-primary-600">NFC Attendance</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-3">
          {filteredNavItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          v1.0.0
        </p>
      </div>
    </aside>
  )
}



