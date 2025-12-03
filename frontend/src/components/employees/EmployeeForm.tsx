/**
 * Employee create/edit form component
 */

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Employee, EmployeeStatus } from '@/types'
import { X } from 'lucide-react'

const employeeSchema = z.object({
  employee_no: z.string().regex(/^EMP-\d{3,}$/, 'Must be in format EMP-001'),
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  department: z.string().min(2, 'Department is required'),
  hire_date: z.string(),
  status: z.nativeEnum(EmployeeStatus),
})

type EmployeeFormData = z.infer<typeof employeeSchema>

interface EmployeeFormProps {
  employee?: Employee
  onSubmit: (data: EmployeeFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export const EmployeeForm: React.FC<EmployeeFormProps> = ({
  employee,
  onSubmit,
  onCancel,
  isLoading,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<EmployeeFormData>({
    resolver: zodResolver(employeeSchema),
    defaultValues: employee
      ? {
          employee_no: employee.employee_no,
          full_name: employee.full_name,
          email: employee.email,
          department: employee.department,
          hire_date: employee.hire_date.split('T')[0],
          status: employee.status,
        }
      : {
          status: EmployeeStatus.ACTIVE,
        },
  })

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {employee ? 'Edit Employee' : 'Add New Employee'}
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
          {/* Employee Number */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Employee Number *
            </label>
            <input
              {...register('employee_no')}
              type="text"
              className="input"
              placeholder="EMP-001"
              disabled={!!employee}
            />
            {errors.employee_no && (
              <p className="mt-1 text-sm text-red-600">{errors.employee_no.message}</p>
            )}
          </div>

          {/* Full Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              {...register('full_name')}
              type="text"
              className="input"
              placeholder="John Doe"
            />
            {errors.full_name && (
              <p className="mt-1 text-sm text-red-600">{errors.full_name.message}</p>
            )}
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email *
            </label>
            <input
              {...register('email')}
              type="email"
              className="input"
              placeholder="john.doe@company.com"
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          {/* Department */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Department *
            </label>
            <input
              {...register('department')}
              type="text"
              className="input"
              placeholder="IT"
            />
            {errors.department && (
              <p className="mt-1 text-sm text-red-600">{errors.department.message}</p>
            )}
          </div>

          {/* Hire Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Hire Date *
            </label>
            <input
              {...register('hire_date')}
              type="date"
              className="input"
            />
            {errors.hire_date && (
              <p className="mt-1 text-sm text-red-600">{errors.hire_date.message}</p>
            )}
          </div>

          {/* Status */}
          {employee && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status *
              </label>
              <select {...register('status')} className="input">
                <option value={EmployeeStatus.ACTIVE}>Active</option>
                <option value={EmployeeStatus.INACTIVE}>Inactive</option>
                <option value={EmployeeStatus.TERMINATED}>Terminated</option>
              </select>
              {errors.status && (
                <p className="mt-1 text-sm text-red-600">{errors.status.message}</p>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="btn btn-secondary"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Saving...
                </span>
              ) : (
                employee ? 'Update Employee' : 'Create Employee'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}



