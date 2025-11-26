/** Zustand store for query state management */
import { create } from 'zustand';
import type { QueryResponse, Dataset } from '../types';

export interface ConversationTurn {
  id: string;
  question: string;
  response: QueryResponse | null;
  createdAt: number;
}

interface QueryState {
  // Current query state
  isLoading: boolean;
  error: string | null;
  currentResponse: QueryResponse | null;
  history: ConversationTurn[];

  // Dataset management
  currentUserId: string;
  currentDatasetId: string | null;
  datasets: Dataset[];
  presetQuestion: string | null;

  // Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setResponse: (response: QueryResponse | null) => void;
  setUserId: (userId: string) => void;
  setDatasetId: (datasetId: string | null) => void;
  setDatasets: (datasets: Dataset[]) => void;
  setPresetQuestion: (question: string | null) => void;
  addTurn: (question: string) => string;
  attachResponseToTurn: (id: string, response: QueryResponse) => void;
  clearHistory: () => void;
  reset: () => void;
}

const initialState: Omit<QueryState, 'setLoading' | 'setError' | 'setResponse' | 'setUserId' | 'setDatasetId' | 'setDatasets' | 'setPresetQuestion' | 'addTurn' | 'attachResponseToTurn' | 'clearHistory' | 'reset'> =
  {
    isLoading: false,
    error: null,
    currentResponse: null,
    history: [],
    currentUserId: 'default_user',
    currentDatasetId: null,
    datasets: [],
    presetQuestion: null,
  };

export const useQueryStore = create<QueryState>((set) => ({
  ...initialState,

  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setResponse: (response) =>
    set((state) => ({
      currentResponse: response,
      history:
        response && state.history.length
          ? state.history.map((turn, idx) =>
              idx === state.history.length - 1 && !turn.response
                ? { ...turn, response }
                : turn,
            )
          : state.history,
    })),
  setUserId: (userId) => set({ currentUserId: userId }),
  setDatasetId: (datasetId) =>
    set((state) => ({
      currentDatasetId: datasetId,
      // Changing dataset starts a fresh conversation
      history: [],
      currentResponse: null,
      error: null,
      isLoading: false,
    })),
  setDatasets: (datasets) => set({ datasets }),
  setPresetQuestion: (presetQuestion) => set({ presetQuestion }),
  addTurn: (question) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    set((state) => ({
      history: [
        ...state.history,
        {
          id,
          question,
          response: null,
          createdAt: Date.now(),
        },
      ],
      // Clear any previous top-level error for new turn
      error: null,
    }));
    return id;
  },
  attachResponseToTurn: (id, response) =>
    set((state) => ({
      currentResponse: response,
      history: state.history.map((turn) => (turn.id === id ? { ...turn, response } : turn)),
    })),
  clearHistory: () =>
    set({
      history: [],
      currentResponse: null,
      error: null,
    }),
  reset: () => set(initialState),
}));

