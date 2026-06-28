'use client';

import { useState } from 'react';
import { FiSearch } from 'react-icons/fi';
import { apiClient } from '@/lib/api';
import { useRAGStore, QueryResult } from '@/lib/store';

export default function QueryInterface() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const { setLoading, isLoading, setCurrentResult, addToHistory } = useRAGStore();
  const [error, setError] = useState('');

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!query.trim()) {
        throw new Error('Please enter a query');
      }

      const response = await apiClient.query(query, topK);
      const result: QueryResult = response.data;
      
      setCurrentResult(result);
      addToHistory(result);
      setQuery('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">🔍 Query Documents</h2>

      <form onSubmit={handleQuery} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Question
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about your documents..."
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Top Results: {topK}
          </label>
          <input
            type="range"
            min="1"
            max="20"
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value))}
            className="w-full"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition flex items-center justify-center gap-2"
        >
          <FiSearch />
          {isLoading ? '⏳ Searching...' : '🔍 Search'}
        </button>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          ❌ {error}
        </div>
      )}
    </div>
  );
}