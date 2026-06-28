'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { useRAGStore, Metrics } from '@/lib/store';

export default function MetricsDashboard() {
  const { metrics, setMetrics } = useRAGStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await apiClient.getMetrics();
      setMetrics(response.data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch metrics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading metrics...</div>;
  }

  if (error || !metrics) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        ⚠️ Unable to load metrics
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">📊 System Metrics</h2>
        <button
          onClick={fetchMetrics}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          🔄 Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricBox
          title="Total Queries"
          value={metrics.total_queries}
          icon="🔍"
        />
        <MetricBox
          title="Error Rate"
          value={`${(metrics.error_rate * 100).toFixed(2)}%`}
          icon="⚠️"
        />
        <MetricBox
          title="Avg Latency"
          value={`${metrics.avg_latency.toFixed(0)}ms`}
          icon="⚡"
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-4">
          Quality Scores (24h Average)
        </h3>
        <div className="space-y-4">
          <ScoreBar
            label="Faithfulness"
            score={metrics.avg_faithfulness}
            description="Answer sticks to documents"
          />
          <ScoreBar
            label="Answer Relevance"
            score={metrics.avg_relevance}
            description="Answer addresses query"
          />
        </div>
      </div>

      <div className="text-sm text-gray-500 text-center">
        Last updated: {new Date(metrics.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
}

function MetricBox({
  title,
  value,
  icon,
}: {
  title: string;
  value: string | number;
  icon: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
      <p className="text-3xl mb-2">{icon}</p>
      <p className="text-gray-600 text-sm font-medium">{title}</p>
      <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
    </div>
  );
}

function ScoreBar({
  label,
  score,
  description,
}: {
  label: string;
  score: number;
  description: string;
}) {
  const percentage = Math.round(score * 100);
  const color =
    score >= 0.8 ? 'bg-green-500' : score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div>
      <div className="flex justify-between mb-2">
        <p className="font-medium text-gray-700">{label}</p>
        <p className="font-semibold text-gray-900">{percentage}%</p>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full`} style={{ width: `${percentage}%` }} />
      </div>
      <p className="text-xs text-gray-500 mt-1">{description}</p>
    </div>
  );
}