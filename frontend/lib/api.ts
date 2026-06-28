import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Client methods
export const apiClient = {
  // Health check
  async getHealth() {
    return api.get('/health');
  },

  // Metrics
  async getMetrics() {
    return api.get('/metrics');
  },

  // Documents
  async uploadDocuments(files: File[]) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    return api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  async ingestUrl(url: string, name?: string) {
    const params = new URLSearchParams();
    params.append('url', url);
    if (name) params.append('name', name);
    
    return api.post(`/documents/ingest-url?${params.toString()}`);
  },

  // Query
  async query(query: string, topK: number = 5, useReranker: boolean = true) {
    return api.post('/query', {
      query,
      top_k: topK,
      use_reranker: useReranker,
    });
  },

  // History
  async getHistory(limit: number = 50, skip: number = 0) {
    return api.get('/history', {
      params: { limit, skip },
    });
  },
};

export default api;