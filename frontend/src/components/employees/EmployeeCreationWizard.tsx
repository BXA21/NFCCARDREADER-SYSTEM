/**
 * Multi-step Employee Creation Wizard with NFC Card Integration
 * Steps:
 * 1. Employee Details
 * 2. Scan NFC Card
 * 3. Confirm Card Assignment
 * 4. Write to NFC Card
 * 5. Test Card (Live Demo)
 */

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import axiosInstance from '@/lib/axios'
import { API_ENDPOINTS } from '@/config/api'
import { CheckCircle, AlertCircle, CreditCard, Loader2, UserPlus, TestTube } from 'lucide-react'

interface EmployeeFormData {
  employee_no: string
  full_name: string
  email: string
  department: string
  hire_date: string
  supervisor_id?: string
  status: 'ACTIVE' | 'INACTIVE'
}

interface DetectedCard {
  card_uid: string
  detected_at: string
  is_assigned: boolean
  assigned_to?: string
}

interface CardWriteStatus {
  success: boolean
  message: string
  blocks_written?: number
}

interface TestEvent {
  event_type: 'IN' | 'OUT'
  timestamp: string
  employee_name: string
  department: string
}

type WizardStep = 1 | 2 | 3 | 4 | 5

export const EmployeeCreationWizard = ({ onComplete, onCancel }: { onComplete: () => void, onCancel: () => void }) => {
  const [currentStep, setCurrentStep] = useState<WizardStep>(1)
  const [employeeData, setEmployeeData] = useState<EmployeeFormData>({
    employee_no: '',
    full_name: '',
    email: '',
    department: '',
    hire_date: new Date().toISOString().split('T')[0],
    status: 'ACTIVE'
  })
  const [detectedCard, setDetectedCard] = useState<DetectedCard | null>(null)
  const [createdEmployeeId, setCreatedEmployeeId] = useState<string | null>(null)
  const [isScanning, setIsScanning] = useState(false)
  const [isWriting, setIsWriting] = useState(false)
  const [writeStatus, setWriteStatus] = useState<CardWriteStatus | null>(null)
  const [testEvents, setTestEvents] = useState<TestEvent[]>([])
  const [manualCardUid, setManualCardUid] = useState<string>('')
  const [showManualInput, setShowManualInput] = useState(false)

  // Step 1: Create Employee Mutation
  const createEmployeeMutation = useMutation({
    mutationFn: async (data: EmployeeFormData) => {
      console.log('[WIZARD] Submitting employee data:', JSON.stringify(data, null, 2))
      const response = await axiosInstance.post(API_ENDPOINTS.EMPLOYEES, data)
      console.log('[WIZARD] Employee created successfully:', JSON.stringify(response.data, null, 2))
      return response.data
    },
    onSuccess: (data) => {
      setCreatedEmployeeId(data.id)
      setCurrentStep(2)
      setIsScanning(true)
    },
    onError: (error: any) => {
      console.error('[WIZARD] Employee creation failed:', error)
      console.error('[WIZARD] Error response:', JSON.stringify(error.response?.data, null, 2))
      const errorDetail = error.response?.data?.detail || error.message
      const errorMsg = typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail, null, 2)
      alert(`Failed to create employee:\n\n${errorMsg}`)
    }
  })

  // Step 2: Poll for detected cards
  const { data: scannedCard, refetch: refetchCard } = useQuery({
    queryKey: ['scan-card'],
    queryFn: async () => {
      const response = await axiosInstance.get('/cards/scan-mode/latest')
      return response.data
    },
    enabled: isScanning && currentStep === 2,
    refetchInterval: 500, // Poll every 500ms for fast response
  })

  useEffect(() => {
    if (scannedCard && currentStep === 2) {
      setDetectedCard(scannedCard)
      setIsScanning(false)
    }
  }, [scannedCard, currentStep])

  // Step 3: Assign card to employee
  const assignCardMutation = useMutation({
    mutationFn: async () => {
      if (!createdEmployeeId || !detectedCard) throw new Error('Missing data')
      const response = await axiosInstance.post(
        `/employees/${createdEmployeeId}/cards`,
        { card_uid: detectedCard.card_uid }
      )
      return response.data
    },
    onSuccess: () => {
      setCurrentStep(4)
      setIsWriting(true)
      writeToCard()
    }
  })

  // Step 4: Write employee data to NFC card
  const writeToCard = async () => {
    try {
      if (!detectedCard || !employeeData) return

      const response = await axiosInstance.post('/cards/write', {
        card_uid: detectedCard.card_uid,
        employee_data: {
          employee_no: employeeData.employee_no,
          full_name: employeeData.full_name,
          department: employeeData.department,
          employee_id: createdEmployeeId
        }
      })

      setWriteStatus(response.data)
      setIsWriting(false)
      
      // Auto-advance to test step after 2 seconds
      setTimeout(() => setCurrentStep(5), 2000)
    } catch (error: any) {
      setWriteStatus({
        success: false,
        message: error.response?.data?.detail || 'Failed to write to card'
      })
      setIsWriting(false)
    }
  }

  // Step 5: Poll for test attendance events  
  const { data: latestEvent } = useQuery({
    queryKey: ['test-attendance', createdEmployeeId],
    queryFn: async () => {
      const response = await axiosInstance.get(
        `/attendance/test/${createdEmployeeId}/latest`
      )
      return response.data
    },
    enabled: currentStep === 5 && !!createdEmployeeId,
    refetchInterval: 500, // Poll every 500ms for instant feedback
  })

  useEffect(() => {
    if (latestEvent && currentStep === 5) {
      // Add new event if not already in list
      setTestEvents(prev => {
        const exists = prev.some(e => e.timestamp === latestEvent.timestamp)
        if (!exists) {
          return [...prev, latestEvent]
        }
        return prev
      })
    }
  }, [latestEvent, currentStep])

  const handleStep1Submit = (e: React.FormEvent) => {
    e.preventDefault()
    createEmployeeMutation.mutate(employeeData)
  }

  const handleStep3Confirm = () => {
    assignCardMutation.mutate()
  }

  const handleFinish = () => {
    onComplete()
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header with Progress */}
        <div className="sticky top-0 bg-white border-b p-6 z-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Create New Employee with NFC Card
          </h2>
          
          {/* Progress Steps */}
          <div className="flex items-center justify-between">
            {[1, 2, 3, 4, 5].map((step) => (
              <div key={step} className="flex items-center">
                <div className={`
                  flex items-center justify-center w-10 h-10 rounded-full border-2 font-semibold
                  ${currentStep >= step 
                    ? 'bg-primary-600 border-primary-600 text-white' 
                    : 'bg-gray-100 border-gray-300 text-gray-500'
                  }
                  ${currentStep === step ? 'ring-4 ring-primary-100' : ''}
                `}>
                  {currentStep > step ? <CheckCircle className="w-6 h-6" /> : step}
                </div>
                {step < 5 && (
                  <div className={`w-16 h-1 mx-2 ${currentStep > step ? 'bg-primary-600' : 'bg-gray-300'}`} />
                )}
              </div>
            ))}
          </div>
          
          {/* Step Labels */}
          <div className="flex justify-between mt-2 text-xs text-gray-600">
            <span className={currentStep === 1 ? 'font-semibold text-primary-600' : ''}>Details</span>
            <span className={currentStep === 2 ? 'font-semibold text-primary-600' : ''}>Scan Card</span>
            <span className={currentStep === 3 ? 'font-semibold text-primary-600' : ''}>Confirm</span>
            <span className={currentStep === 4 ? 'font-semibold text-primary-600' : ''}>Write Card</span>
            <span className={currentStep === 5 ? 'font-semibold text-primary-600' : ''}>Test</span>
          </div>
        </div>

        {/* Step Content */}
        <div className="p-6">
          {/* STEP 1: Employee Details Form */}
          {currentStep === 1 && (
            <form onSubmit={handleStep1Submit} className="space-y-4">
              <div className="flex items-center mb-4">
                <UserPlus className="w-6 h-6 text-primary-600 mr-2" />
                <h3 className="text-lg font-semibold">Step 1: Enter Employee Details</h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Employee Number *
                  </label>
                  <input
                    type="text"
                    required
                    value={employeeData.employee_no}
                    onChange={(e) => setEmployeeData(prev => ({ ...prev, employee_no: e.target.value }))}
                    placeholder="EMP-001"
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={employeeData.full_name}
                    onChange={(e) => setEmployeeData(prev => ({ ...prev, full_name: e.target.value }))}
                    placeholder="Mohammed Ahmed"
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={employeeData.email}
                    onChange={(e) => setEmployeeData(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="mohammed@company.com"
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Department *
                  </label>
                  <input
                    type="text"
                    required
                    value={employeeData.department}
                    onChange={(e) => setEmployeeData(prev => ({ ...prev, department: e.target.value }))}
                    placeholder="Engineering"
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hire Date *
                  </label>
                  <input
                    type="date"
                    required
                    value={employeeData.hire_date}
                    onChange={(e) => setEmployeeData(prev => ({ ...prev, hire_date: e.target.value }))}
                    className="input"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status *
                  </label>
                  <select
                    value={employeeData.status}
                    onChange={(e) => setEmployeeData(prev => ({ ...prev, status: e.target.value as any }))}
                    className="input"
                  >
                    <option value="ACTIVE">Active</option>
                    <option value="INACTIVE">Inactive</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={onCancel}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createEmployeeMutation.isPending}
                  className="btn-primary"
                >
                  {createEmployeeMutation.isPending ? 'Creating...' : 'Next: Scan NFC Card'}
                </button>
              </div>
            </form>
          )}

          {/* STEP 2: Scan NFC Card */}
          {currentStep === 2 && (
            <div className="text-center py-8">
              <div className="flex items-center justify-center mb-4">
                <CreditCard className="w-12 h-12 text-primary-600 mr-2" />
                <h3 className="text-lg font-semibold">Step 2: Scan NFC Card</h3>
              </div>

              {!showManualInput ? (
                <>
                  {isScanning ? (
                    <div className="space-y-6">
                      <div className="relative">
                        <div className="w-48 h-48 mx-auto border-4 border-primary-300 rounded-full flex items-center justify-center animate-pulse">
                          <CreditCard className="w-24 h-24 text-primary-600" />
                        </div>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-56 h-56 border-4 border-primary-200 rounded-full animate-ping" />
                        </div>
                      </div>
                      
                      <div>
                        <p className="text-xl font-semibold text-gray-900 mb-2">
                          Waiting for NFC Card...
                        </p>
                        <p className="text-gray-600">
                          Please tap the NFC card on the ACR122U reader
                        </p>
                        <p className="text-sm text-gray-500 mt-2">
                          Card will be detected automatically
                        </p>
                      </div>

                      <div className="flex items-center justify-center gap-2 text-primary-600">
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Scanning...</span>
                      </div>

                      {/* Manual Input Option */}
                      <div className="pt-4 border-t border-gray-200 mt-6">
                        <p className="text-sm text-gray-600 mb-3">
                          Card not detecting automatically?
                        </p>
                        <button
                          onClick={() => {
                            setIsScanning(false)
                            setShowManualInput(true)
                          }}
                          className="btn-secondary text-sm"
                        >
                          Enter Card UID Manually
                        </button>
                      </div>
                    </div>
                  ) : detectedCard ? (
                    <div className="space-y-4">
                      <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                      <p className="text-xl font-semibold text-green-600">
                        Card Detected!
                      </p>
                      <div className="bg-gray-50 rounded-lg p-4 max-w-md mx-auto">
                        <p className="text-sm text-gray-600 mb-1">Card UID:</p>
                        <p className="text-lg font-mono font-bold text-gray-900">
                          {detectedCard.card_uid}
                        </p>
                      </div>
                      <button
                        onClick={() => setCurrentStep(3)}
                        className="btn-primary"
                      >
                        Continue to Assignment
                      </button>
                    </div>
                  ) : null}
                </>
              ) : (
                /* Manual Input Form */
                <div className="space-y-6 max-w-md mx-auto">
                  <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
                    <p className="text-sm text-gray-900 font-semibold mb-2">
                      📝 Manual Card Entry
                    </p>
                    <p className="text-xs text-gray-600">
                      Tap your card on the reader and check the reader agent terminal for the card UID,
                      then enter it below.
                    </p>
                  </div>

                  <div className="text-left">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Card UID (Hexadecimal) *
                    </label>
                    <input
                      type="text"
                      value={manualCardUid}
                      onChange={(e) => setManualCardUid(e.target.value.toUpperCase())}
                      placeholder="04ABC123456789"
                      className="input w-full font-mono"
                      maxLength={20}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Example: 043BBE1B6F6180 or 04A2B3C4D5E6F7
                    </p>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        setShowManualInput(false)
                        setIsScanning(true)
                        setManualCardUid('')
                      }}
                      className="btn-secondary flex-1"
                    >
                      Back to Auto-Scan
                    </button>
                    <button
                      onClick={() => {
                        if (manualCardUid.trim().length >= 10) {
                          setDetectedCard({
                            card_uid: manualCardUid.trim(),
                            detected_at: new Date().toISOString(),
                            is_assigned: false
                          })
                          setShowManualInput(false)
                        } else {
                          alert('Please enter a valid card UID (at least 10 characters)')
                        }
                      }}
                      disabled={manualCardUid.trim().length < 10}
                      className="btn-primary flex-1"
                    >
                      Use This Card
                    </button>
                  </div>
                </div>
              )}

              <button
                onClick={onCancel}
                className="btn-secondary mt-6"
              >
                Cancel
              </button>
            </div>
          )}

          {/* STEP 3: Confirm Card Assignment */}
          {currentStep === 3 && detectedCard && (
            <div className="text-center py-8">
              <div className="flex items-center justify-center mb-4">
                <AlertCircle className="w-12 h-12 text-yellow-600 mr-2" />
                <h3 className="text-lg font-semibold">Step 3: Confirm Card Assignment</h3>
              </div>

              <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 max-w-lg mx-auto mb-6">
                <p className="text-lg text-gray-900 mb-4">
                  Assign this card to <span className="font-bold">{employeeData.full_name}</span>?
                </p>
                
                <div className="space-y-3 text-left">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Employee No:</span>
                    <span className="font-semibold">{employeeData.employee_no}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Department:</span>
                    <span className="font-semibold">{employeeData.department}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Card UID:</span>
                    <span className="font-mono font-semibold">{detectedCard.card_uid}</span>
                  </div>
                </div>
              </div>

              <div className="flex justify-center gap-3">
                <button
                  onClick={() => {
                    setCurrentStep(2)
                    setDetectedCard(null)
                    setIsScanning(true)
                  }}
                  className="btn-secondary"
                >
                  Scan Different Card
                </button>
                <button
                  onClick={handleStep3Confirm}
                  disabled={assignCardMutation.isPending}
                  className="btn-primary"
                >
                  {assignCardMutation.isPending ? 'Assigning...' : 'Confirm & Write to Card'}
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: Write to NFC Card */}
          {currentStep === 4 && (
            <div className="text-center py-8">
              <div className="flex items-center justify-center mb-4">
                <CreditCard className="w-12 h-12 text-primary-600 mr-2" />
                <h3 className="text-lg font-semibold">Step 4: Writing Employee Data to NFC Card</h3>
              </div>

              {isWriting ? (
                <div className="space-y-6">
                  <div className="w-48 h-48 mx-auto border-4 border-primary-300 rounded-full flex items-center justify-center">
                    <Loader2 className="w-24 h-24 text-primary-600 animate-spin" />
                  </div>
                  
                  <div>
                    <p className="text-xl font-semibold text-gray-900 mb-2">
                      Please keep the card on the reader...
                    </p>
                    <p className="text-gray-600">
                      Writing employee data to NFC card
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      This will take a few seconds
                    </p>
                  </div>

                  <div className="flex items-center justify-center gap-2 text-primary-600">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Writing data blocks...</span>
                  </div>
                </div>
              ) : writeStatus ? (
                <div className="space-y-4">
                  {writeStatus.success ? (
                    <>
                      <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
                      <p className="text-xl font-semibold text-green-600">
                        Card Programmed Successfully!
                      </p>
                      <div className="bg-green-50 rounded-lg p-4 max-w-md mx-auto">
                        <p className="text-sm text-gray-600 mb-1">{writeStatus.message}</p>
                        {writeStatus.blocks_written && (
                          <p className="text-xs text-gray-500">
                            Blocks written: {writeStatus.blocks_written}
                          </p>
                        )}
                      </div>
                      <p className="text-gray-600">
                        Proceeding to test...
                      </p>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-16 h-16 text-red-500 mx-auto" />
                      <p className="text-xl font-semibold text-red-600">
                        Write Failed
                      </p>
                      <div className="bg-red-50 rounded-lg p-4 max-w-md mx-auto">
                        <p className="text-sm text-gray-900">{writeStatus.message}</p>
                      </div>
                      <button
                        onClick={() => {
                          setIsWriting(true)
                          writeToCard()
                        }}
                        className="btn-primary"
                      >
                        Retry Writing
                      </button>
                    </>
                  )}
                </div>
              ) : null}
            </div>
          )}

          {/* STEP 5: Test Card */}
          {currentStep === 5 && (
            <div className="py-8">
              <div className="flex items-center justify-center mb-6">
                <TestTube className="w-12 h-12 text-primary-600 mr-2" />
                <h3 className="text-lg font-semibold">Step 5: Test Your New Card</h3>
              </div>

              <div className="max-w-2xl mx-auto">
                <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
                  <p className="text-center text-lg text-gray-900 mb-4">
                    <span className="font-bold">Test the card now!</span>
                    <br />
                    Tap the card on the reader to simulate clock in/out
                  </p>
                  
                  <div className="flex items-center justify-center gap-2 text-primary-600">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Listening for card taps...</span>
                  </div>
                </div>

                {/* Live Test Events */}
                <div className="space-y-3">
                  <h4 className="font-semibold text-gray-900">Live Test Results:</h4>
                  
                  {testEvents.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <CreditCard className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Waiting for first tap...</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {testEvents.map((event, index) => (
                        <div
                          key={index}
                          className={`p-4 rounded-lg border-2 ${
                            event.event_type === 'IN'
                              ? 'bg-green-50 border-green-300'
                              : 'bg-orange-50 border-orange-300'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-semibold text-gray-900">
                                {event.event_type === 'IN' ? '🟢 Clock IN' : '🔴 Clock OUT'}
                              </p>
                              <p className="text-sm text-gray-600">
                                {event.employee_name} • {event.department}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-medium text-gray-900">
                                {new Date(event.timestamp).toLocaleTimeString()}
                              </p>
                              <p className="text-xs text-gray-500">
                                {new Date(event.timestamp).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          
                          {event.event_type === 'IN' ? (
                            <p className="text-sm text-green-700 mt-2">
                              ✅ {event.employee_name} has arrived at {new Date(event.timestamp).toLocaleTimeString()}
                            </p>
                          ) : (
                            <p className="text-sm text-orange-700 mt-2">
                              ✅ {event.employee_name} has left at {new Date(event.timestamp).toLocaleTimeString()}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {testEvents.length > 0 && (
                  <div className="mt-6 bg-green-50 border-2 border-green-300 rounded-lg p-4">
                    <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
                    <p className="text-center text-green-800 font-semibold">
                      Card is working perfectly! 🎉
                    </p>
                    <p className="text-center text-sm text-green-700 mt-1">
                      The employee can now use this card for attendance
                    </p>
                  </div>
                )}

                <div className="flex justify-center gap-3 mt-8">
                  {testEvents.length > 0 ? (
                    <button
                      onClick={handleFinish}
                      className="btn-primary"
                    >
                      Complete Setup
                    </button>
                  ) : (
                    <button
                      onClick={handleFinish}
                      className="btn-secondary"
                    >
                      Skip Test & Finish
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

