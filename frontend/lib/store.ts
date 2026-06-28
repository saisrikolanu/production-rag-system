import { create } from 'zustand';

export interface QueryResult {
  query: string;
  answer: string;
  sources: Array<{
    filename: string;
    text: string;
    relevance_score: number;
  }>;
  metrics: {
    faithfulness: number;
    answer_relevance: number;
    context_relevance: number;
    latency_ms: number;
  };
  timestamp: string;
}

export interface Metrics {
  total_queries: number;
  total_errors: number;
  error_rate: number;
  avg_latency: number;
  avg_faithfulness: number;
  avg_relevance: number;
  timestamp: string;
}

interface RAGStore {
  // Loading states
  isLoading: boolean;
  isUploading: boolean;
  
  // Data
  currentResult: QueryResult | null;
  metrics: Metrics | null;
  queryHistory: QueryResult[];
  
  // Methods
  setLoading: (loading: boolean) => void;
  setUploading: (uploading: boolean) => void;
  setCurrentResult: (result: QueryResult | null) => void;
  setMetrics: (metrics: Metrics | null) => void;
  setQueryHistory: (history: QueryResult[]) => void;
  addToHistory: (result: QueryResult) => void;
  clearHistory: () => void;
}

export const useRAGStore = create<RAGStore>((set) => ({
  isLoading: false,
  isUploading: false,
  currentResult: null,
  metrics: null,
  queryHistory: [],
  
  setLoading: (loading) => set({ isLoading: loading }),
  setUploading: (uploading) => set({ isUploading: uploading }),
  setCurrentResult: (result) => set({ currentResult: result }),
  setMetrics: (metrics) => set({ metrics }),
  setQueryHistory: (history) => set({ queryHistory: history }),
  addToHistory: (result) => set((state) => ({
    queryHistory: [result, ...state.queryHistory].slice(0, 50),
  })),
  clearHistory: () => set({ queryHistory: [] }),
}));