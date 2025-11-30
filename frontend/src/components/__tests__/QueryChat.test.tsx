/** Tests for QueryChat component */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryChat } from '../QueryChat'
import { useQueryStore } from '../../stores/queryStore'
import { queryApi } from '../../services/api'

// Mock the API
vi.mock('../../services/api', () => ({
  queryApi: {
    executeQuery: vi.fn(),
  },
}))

// Mock the store
vi.mock('../../stores/queryStore', () => ({
  useQueryStore: vi.fn(),
}))

describe('QueryChat', () => {
  const mockSetLoading = vi.fn()
  const mockSetError = vi.fn()
  const mockAddTurn = vi.fn(() => 'turn-123')
  const mockAttachResponseToTurn = vi.fn()
  const mockSetPresetQuestion = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useQueryStore as any).mockReturnValue({
      isLoading: false,
      setLoading: mockSetLoading,
      setError: mockSetError,
      addTurn: mockAddTurn,
      attachResponseToTurn: mockAttachResponseToTurn,
      currentUserId: 'test-user',
      currentDatasetId: 'test-dataset',
      presetQuestion: null,
      setPresetQuestion: mockSetPresetQuestion,
    })
  })

  it('renders the query input and submit button', () => {
    render(<QueryChat />)
    
    expect(screen.getByLabelText(/ask about your data/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/ask a question about your data/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze/i })).toBeInTheDocument()
  })

  it('disables submit button when no dataset is selected', () => {
    ;(useQueryStore as any).mockReturnValue({
      isLoading: false,
      setLoading: mockSetLoading,
      setError: mockSetError,
      addTurn: mockAddTurn,
      attachResponseToTurn: mockAttachResponseToTurn,
      currentUserId: 'test-user',
      currentDatasetId: null,
      presetQuestion: null,
      setPresetQuestion: mockSetPresetQuestion,
    })

    render(<QueryChat />)
    
    const button = screen.getByRole('button', { name: /analyze/i })
    expect(button).toBeDisabled()
  })

  it('disables submit button when input is empty', () => {
    render(<QueryChat />)
    
    const button = screen.getByRole('button', { name: /analyze/i })
    expect(button).toBeDisabled()
  })

  it('enables submit button when input has text and dataset is selected', async () => {
    const user = userEvent.setup()
    render(<QueryChat />)
    
    const input = screen.getByPlaceholderText(/ask a question about your data/i)
    const button = screen.getByRole('button', { name: /analyze/i })
    
    await user.type(input, 'What is the average age?')
    
    expect(button).not.toBeDisabled()
  })

  it('shows loading state when processing', () => {
    ;(useQueryStore as any).mockReturnValue({
      isLoading: true,
      setLoading: mockSetLoading,
      setError: mockSetError,
      addTurn: mockAddTurn,
      attachResponseToTurn: mockAttachResponseToTurn,
      currentUserId: 'test-user',
      currentDatasetId: 'test-dataset',
      presetQuestion: null,
      setPresetQuestion: mockSetPresetQuestion,
    })

    render(<QueryChat />)
    
    expect(screen.getByText(/processing/i)).toBeInTheDocument()
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('submits query when form is submitted', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      sql: 'SELECT * FROM table',
      results: [],
      visualization: { type: 'table' },
      analysis: { summary: 'Test analysis' },
      data_structure: {},
    }
    
    ;(queryApi.executeQuery as any).mockResolvedValue(mockResponse)

    render(<QueryChat />)
    
    const input = screen.getByPlaceholderText(/ask a question about your data/i)
    const button = screen.getByRole('button', { name: /analyze/i })
    
    await user.type(input, 'What is the average age?')
    await user.click(button)
    
    await waitFor(() => {
      expect(mockAddTurn).toHaveBeenCalledWith('What is the average age?')
      expect(mockSetLoading).toHaveBeenCalledWith(true)
      expect(queryApi.executeQuery).toHaveBeenCalledWith({
        user_id: 'test-user',
        dataset_id: 'test-dataset',
        query: 'What is the average age?',
      })
    })
  })

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup()
    const error = new Error('API Error')
    
    ;(queryApi.executeQuery as any).mockRejectedValue(error)

    render(<QueryChat />)
    
    const input = screen.getByPlaceholderText(/ask a question about your data/i)
    const button = screen.getByRole('button', { name: /analyze/i })
    
    await user.type(input, 'Test query')
    await user.click(button)
    
    await waitFor(() => {
      expect(mockSetError).toHaveBeenCalled()
      expect(mockSetLoading).toHaveBeenCalledWith(false)
    })
  })
})

