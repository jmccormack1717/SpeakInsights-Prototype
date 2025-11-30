/** Tests for queryStore */
import { describe, it, expect, beforeEach } from 'vitest'
import { useQueryStore } from '../queryStore'
import type { QueryResponse } from '../../types'

describe('queryStore', () => {
  beforeEach(() => {
    // Reset store to initial state before each test
    useQueryStore.getState().reset()
  })

  it('initializes with default values', () => {
    const state = useQueryStore.getState()
    
    expect(state.isLoading).toBe(false)
    expect(state.error).toBe(null)
    expect(state.currentResponse).toBe(null)
    expect(state.history).toEqual([])
    expect(state.currentUserId).toBe('default_user')
    expect(state.currentDatasetId).toBe('mvp_dataset')
    expect(state.datasets).toEqual([])
  })

  it('sets loading state', () => {
    useQueryStore.getState().setLoading(true)
    expect(useQueryStore.getState().isLoading).toBe(true)
    
    useQueryStore.getState().setLoading(false)
    expect(useQueryStore.getState().isLoading).toBe(false)
  })

  it('sets error state', () => {
    const errorMessage = 'Test error'
    useQueryStore.getState().setError(errorMessage)
    expect(useQueryStore.getState().error).toBe(errorMessage)
    
    useQueryStore.getState().setError(null)
    expect(useQueryStore.getState().error).toBe(null)
  })

  it('sets user ID', () => {
    const userId = 'user-123'
    useQueryStore.getState().setUserId(userId)
    expect(useQueryStore.getState().currentUserId).toBe(userId)
  })

  it('sets dataset ID and clears history', () => {
    // Add some history first
    useQueryStore.getState().addTurn('Question 1')
    expect(useQueryStore.getState().history.length).toBe(1)
    
    // Change dataset
    const datasetId = 'new-dataset'
    useQueryStore.getState().setDatasetId(datasetId)
    
    expect(useQueryStore.getState().currentDatasetId).toBe(datasetId)
    expect(useQueryStore.getState().history).toEqual([])
    expect(useQueryStore.getState().currentResponse).toBe(null)
    expect(useQueryStore.getState().error).toBe(null)
  })

  it('adds a turn to history', () => {
    const question = 'What is the average age?'
    const turnId = useQueryStore.getState().addTurn(question)
    
    const state = useQueryStore.getState()
    expect(state.history.length).toBe(1)
    expect(state.history[0].question).toBe(question)
    expect(state.history[0].id).toBe(turnId)
    expect(state.history[0].response).toBe(null)
    expect(state.history[0].createdAt).toBeGreaterThan(0)
  })

  it('attaches response to a turn', () => {
    const question = 'What is the average age?'
    const turnId = useQueryStore.getState().addTurn(question)
    
    const mockResponse: QueryResponse = {
      sql: 'SELECT * FROM table',
      results: [],
      visualization: { type: 'table', data: {}, config: {} },
      analysis: { summary: 'Test' },
      data_structure: {},
    }
    
    useQueryStore.getState().attachResponseToTurn(turnId, mockResponse)
    
    const state = useQueryStore.getState()
    expect(state.history[0].response).toEqual(mockResponse)
    expect(state.currentResponse).toEqual(mockResponse)
  })

  it('clears history', () => {
    useQueryStore.getState().addTurn('Question 1')
    useQueryStore.getState().addTurn('Question 2')
    
    expect(useQueryStore.getState().history.length).toBe(2)
    
    useQueryStore.getState().clearHistory()
    
    expect(useQueryStore.getState().history).toEqual([])
    expect(useQueryStore.getState().currentResponse).toBe(null)
    expect(useQueryStore.getState().error).toBe(null)
  })

  it('resets to initial state', () => {
    // Modify state
    useQueryStore.getState().setLoading(true)
    useQueryStore.getState().setError('Error')
    useQueryStore.getState().setUserId('new-user')
    useQueryStore.getState().addTurn('Question')
    
    // Reset
    useQueryStore.getState().reset()
    
    const state = useQueryStore.getState()
    expect(state.isLoading).toBe(false)
    expect(state.error).toBe(null)
    expect(state.currentUserId).toBe('default_user')
    expect(state.currentDatasetId).toBe('mvp_dataset')
    expect(state.history).toEqual([])
  })

  it('sets datasets', () => {
    const datasets = [
      { id: 'ds1', name: 'Dataset 1', row_count: 100 },
      { id: 'ds2', name: 'Dataset 2', row_count: 200 },
    ]
    
    useQueryStore.getState().setDatasets(datasets)
    expect(useQueryStore.getState().datasets).toEqual(datasets)
  })

  it('sets preset question', () => {
    const question = 'Preset question'
    useQueryStore.getState().setPresetQuestion(question)
    expect(useQueryStore.getState().presetQuestion).toBe(question)
    
    useQueryStore.getState().setPresetQuestion(null)
    expect(useQueryStore.getState().presetQuestion).toBe(null)
  })
})

