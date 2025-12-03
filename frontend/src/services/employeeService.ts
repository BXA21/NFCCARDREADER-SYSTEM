/**
 * Employee service for API calls
 */

import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import { Employee, PaginatedResponse, Card } from '@/types'

export const employeeService = {
  /**
   * Get paginated list of employees
   */
  async getEmployees(params: {
    page?: number
    page_size?: number
    department?: string
    status?: string
    search?: string
  }): Promise<PaginatedResponse<Employee>> {
    const response = await axiosInstance.get(API_ENDPOINTS.EMPLOYEES, { params })
    return response.data
  },

  /**
   * Get single employee by ID
   */
  async getEmployee(id: string): Promise<Employee> {
    const response = await axiosInstance.get(API_ENDPOINTS.EMPLOYEE_DETAIL(id))
    return response.data
  },

  /**
   * Create new employee
   */
  async createEmployee(data: {
    employee_no: string
    full_name: string
    email: string
    department: string
    supervisor_id?: string
    hire_date: string
    status?: string
  }): Promise<Employee> {
    const response = await axiosInstance.post(API_ENDPOINTS.EMPLOYEES, data)
    return response.data
  },

  /**
   * Update employee
   */
  async updateEmployee(
    id: string,
    data: Partial<{
      full_name: string
      email: string
      department: string
      supervisor_id: string
      status: string
    }>
  ): Promise<Employee> {
    const response = await axiosInstance.put(API_ENDPOINTS.EMPLOYEE_DETAIL(id), data)
    return response.data
  },

  /**
   * Delete (terminate) employee
   */
  async deleteEmployee(id: string): Promise<void> {
    await axiosInstance.delete(API_ENDPOINTS.EMPLOYEE_DETAIL(id))
  },

  /**
   * Issue card to employee
   */
  async issueCard(employeeId: string, cardUid: string): Promise<Card> {
    const response = await axiosInstance.post(API_ENDPOINTS.ISSUE_CARD(employeeId), {
      card_uid: cardUid,
    })
    return response.data
  },

  /**
   * Get employee cards
   */
  async getEmployeeCards(employeeId: string): Promise<Card[]> {
    const response = await axiosInstance.get(API_ENDPOINTS.EMPLOYEE_CARDS(employeeId))
    return response.data
  },

  /**
   * Revoke card
   */
  async revokeCard(cardId: string): Promise<Card> {
    const response = await axiosInstance.put(API_ENDPOINTS.REVOKE_CARD(cardId))
    return response.data
  },

  /**
   * Mark card as lost
   */
  async markCardLost(cardId: string): Promise<Card> {
    const response = await axiosInstance.put(API_ENDPOINTS.MARK_CARD_LOST(cardId))
    return response.data
  },
}



