/**
 * Employees management page
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { employeeService } from '@/services/employeeService'
import { Employee, EmployeeStatus } from '@/types'
import { EmployeeList } from '@/components/employees/EmployeeList'
import { EmployeeForm } from '@/components/employees/EmployeeForm'
import { EmployeeCreationWizard } from '@/components/employees/EmployeeCreationWizard'
import { CardManagementModal } from '@/components/employees/CardManagementModal'
import { Plus, Search, Filter } from 'lucide-react'
import { getErrorMessage } from '@/lib/utils'

export const EmployeesPage = () => {
  const queryClient = useQueryClient()
  
  // State
  const [search, setSearch] = useState('')
  const [department, setDepartment] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [showWizard, setShowWizard] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null)
  const [showCardModal, setShowCardModal] = useState(false)
  const [cardEmployee, setCardEmployee] = useState<Employee | null>(null)

  // Fetch employees
  const { data, isLoading, error } = useQuery({
    queryKey: ['employees', page, search, department, status],
    queryFn: () =>
      employeeService.getEmployees({
        page,
        page_size: 20,
        search: search || undefined,
        department: department || undefined,
        status: status || undefined,
      }),
  })

  // Create employee mutation
  const createMutation = useMutation({
    mutationFn: employeeService.createEmployee,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      setShowForm(false)
      setSelectedEmployee(null)
    },
  })

  // Update employee mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      employeeService.updateEmployee(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      setShowForm(false)
      setSelectedEmployee(null)
    },
  })

  // Delete employee mutation
  const deleteMutation = useMutation({
    mutationFn: employeeService.deleteEmployee,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
  })

  // Handlers
  const handleCreate = () => {
    setSelectedEmployee(null)
    setShowWizard(true)
  }

  const handleWizardComplete = () => {
    queryClient.invalidateQueries({ queryKey: ['employees'] })
    setShowWizard(false)
  }

  const handleEdit = (employee: Employee) => {
    setSelectedEmployee(employee)
    setShowForm(true)
  }

  const handleDelete = async (employee: Employee) => {
    if (confirm(`Are you sure you want to terminate ${employee.full_name}?`)) {
      try {
        await deleteMutation.mutateAsync(employee.id)
      } catch (err) {
        alert(getErrorMessage(err))
      }
    }
  }

  const handleManageCard = (employee: Employee) => {
    setCardEmployee(employee)
    setShowCardModal(true)
  }

  const handleFormSubmit = async (formData: any) => {
    try {
      if (selectedEmployee) {
        await updateMutation.mutateAsync({
          id: selectedEmployee.id,
          data: formData,
        })
      } else {
        await createMutation.mutateAsync(formData)
      }
    } catch (err) {
      throw err
    }
  }

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
          <p className="text-gray-600 mt-1">Manage employee records and NFC cards</p>
        </div>
        <button onClick={handleCreate} className="btn btn-primary">
          <Plus className="w-5 h-5 mr-2" />
          Add Employee
        </button>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by name, email, or employee no..."
                className="input pl-10"
              />
            </div>
          </div>
          <div>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="input"
            >
              <option value="">All Departments</option>
              <option value="IT">IT</option>
              <option value="HR">HR</option>
              <option value="Finance">Finance</option>
              <option value="Operations">Operations</option>
            </select>
          </div>
          <div>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="input"
            >
              <option value="">All Status</option>
              <option value={EmployeeStatus.ACTIVE}>Active</option>
              <option value={EmployeeStatus.INACTIVE}>Inactive</option>
              <option value={EmployeeStatus.TERMINATED}>Terminated</option>
            </select>
          </div>
        </div>
      </div>

      {/* Employee List */}
      <div className="card">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : error ? (
          <div className="text-center py-12 text-red-600">
            Error loading employees: {getErrorMessage(error)}
          </div>
        ) : data && data.items.length > 0 ? (
          <>
            <EmployeeList
              employees={data.items}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onManageCard={handleManageCard}
            />

            {/* Pagination */}
            {data.total_pages > 1 && (
              <div className="mt-6 flex items-center justify-between border-t border-gray-200 pt-4">
                <p className="text-sm text-gray-600">
                  Showing {data.items.length} of {data.total} employees
                </p>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                    className="btn btn-secondary disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <span className="px-4 py-2 text-sm text-gray-700">
                    Page {page} of {data.total_pages}
                  </span>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page === data.total_pages}
                    className="btn btn-secondary disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Filter className="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <p>No employees found</p>
          </div>
        )}
      </div>

      {/* Employee Creation Wizard (for new employees) */}
      {showWizard && (
        <EmployeeCreationWizard
          onComplete={handleWizardComplete}
          onCancel={() => setShowWizard(false)}
        />
      )}

      {/* Employee Form Modal (for editing existing employees) */}
      {showForm && (
        <EmployeeForm
          employee={selectedEmployee || undefined}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setShowForm(false)
            setSelectedEmployee(null)
          }}
          isLoading={createMutation.isPending || updateMutation.isPending}
        />
      )}

      {/* Card Management Modal */}
      {showCardModal && cardEmployee && (
        <CardManagementModal
          employee={cardEmployee}
          onClose={() => {
            setShowCardModal(false)
            setCardEmployee(null)
          }}
        />
      )}
    </div>
  )
}

