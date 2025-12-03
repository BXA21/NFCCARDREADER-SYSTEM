/**
 * Card management modal component
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { employeeService } from '@/services/employeeService'
import { Employee, Card } from '@/types'
import { X, CreditCard, Trash2 } from 'lucide-react'
import { getStatusColor, cn, formatDateTime, getErrorMessage } from '@/lib/utils'

interface CardManagementModalProps {
  employee: Employee
  onClose: () => void
}

export const CardManagementModal: React.FC<CardManagementModalProps> = ({
  employee,
  onClose,
}) => {
  const queryClient = useQueryClient()
  const [cardUid, setCardUid] = useState('')
  const [error, setError] = useState('')

  // Fetch employee cards
  const { data: cards, isLoading } = useQuery({
    queryKey: ['employee-cards', employee.id],
    queryFn: () => employeeService.getEmployeeCards(employee.id),
  })

  // Issue card mutation
  const issueCardMutation = useMutation({
    mutationFn: (uid: string) => employeeService.issueCard(employee.id, uid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-cards', employee.id] })
      queryClient.invalidateQueries({ queryKey: ['employees'] })
      setCardUid('')
      setError('')
    },
    onError: (error) => {
      setError(getErrorMessage(error))
    },
  })

  // Revoke card mutation
  const revokeCardMutation = useMutation({
    mutationFn: (cardId: string) => employeeService.revokeCard(cardId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employee-cards', employee.id] })
      queryClient.invalidateQueries({ queryKey: ['employees'] })
    },
  })

  const handleIssueCard = () => {
    if (!cardUid.trim()) {
      setError('Please enter a card UID')
      return
    }
    issueCardMutation.mutate(cardUid.trim().toUpperCase())
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Manage NFC Cards</h2>
            <p className="text-sm text-gray-600 mt-1">
              {employee.full_name} ({employee.employee_no})
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Issue New Card */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Issue New Card</h3>
            
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <div className="flex space-x-3">
              <input
                type="text"
                value={cardUid}
                onChange={(e) => setCardUid(e.target.value)}
                placeholder="Enter card UID (e.g., 04A2B3C4D5E6F7)"
                className="input flex-1"
                disabled={issueCardMutation.isPending}
              />
              <button
                onClick={handleIssueCard}
                disabled={issueCardMutation.isPending}
                className="btn btn-primary"
              >
                {issueCardMutation.isPending ? 'Issuing...' : 'Issue Card'}
              </button>
            </div>
            <p className="mt-2 text-sm text-gray-500">
              Enter the card UID from the NFC reader. The system will automatically format it.
            </p>
          </div>

          {/* Existing Cards */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Card History</h3>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              </div>
            ) : cards && cards.length > 0 ? (
              <div className="space-y-3">
                {cards.map((card: Card) => (
                  <div
                    key={card.id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                  >
                    <div className="flex items-center">
                      <CreditCard className="w-5 h-5 text-gray-400 mr-3" />
                      <div>
                        <p className="font-medium text-gray-900">{card.card_uid}</p>
                        <p className="text-sm text-gray-600">
                          Issued: {formatDateTime(card.issued_at)}
                        </p>
                        {card.revoked_at && (
                          <p className="text-sm text-gray-600">
                            Revoked: {formatDateTime(card.revoked_at)}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={cn('badge', getStatusColor(card.status))}>
                        {card.status}
                      </span>
                      {card.status === 'ACTIVE' && (
                        <button
                          onClick={() => {
                            if (confirm('Are you sure you want to revoke this card?')) {
                              revokeCardMutation.mutate(card.id)
                            }
                          }}
                          disabled={revokeCardMutation.isPending}
                          className="text-red-600 hover:text-red-900"
                          title="Revoke Card"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <CreditCard className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                <p>No cards issued yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t border-gray-200">
          <button onClick={onClose} className="btn btn-secondary">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}



