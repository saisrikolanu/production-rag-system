'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { useRAGStore } from '@/lib/store';
import { FiTrash2 } from 'react-icons/fi';

interface HistoryItem {
  id: string;
  query: string;
  answer: string;
  faithfulness: number;
  answer_relevance: number;
  latency_ms: number;
  created_at: string;
}

export default function QueryHistory() {
  const { queryHistory, clearHistory } = useRAGStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await apiClient.getHistory(50, 0);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch history');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading history...</div>;
  }

  if (queryHistory.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No query history yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-700">📜 Query History</h3>
        <button
          onClick={clearHistory}
          className="px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition flex items-center gap-2"
        >
          <FiTrash2 size={16} />
          Clear
        </button>
      </div>

      <div className="space-y-2">
        {queryHistory.map((item, idx) => (
          <div
            key={idx}
            className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition"
          >
            <button
              onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
              className="w-full text-left p-4 hover:bg-gray-50 transition"
            >
              <div className="flex justify-between items-start gap-4">
                <div className="flex-1">
                  <p className="font-medium text-gray-700 line-clamp-1">
                    {item.query}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    {new Date(item.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-700">
                      {(item.faithfulness * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-gray-500">Faithfulness</p>
                  </div>
                </div>
              </div>
            </button>

            {expandedId === item.id && (
              <div className="bg-gray-50 p-4 border-t border-gray-200 space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Answer</p>
                  <p className="text-sm text-gray-600 line-clamp-3">
                    {item.answer}
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div>
                    <p className="text-xs font-medium text-gray-700">
                      {(item.faithfulness * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-gray-500">Faithfulness</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-700">
                      {(item.answer_relevance * 100).toFixed(0)}%
                    </p>
                    <p className="text-xs text-gray-500">Relevance</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-700">
                      {item.latency_ms.toFixed(0)}ms
                    </p>
                    <p className="text-xs text-gray-500">Latency</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {error && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}