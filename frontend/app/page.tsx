'use client';

import { useState, useEffect } from 'react';
import DocumentUploader from '@/components/DocumentUploader';
import URLIngester from '@/components/URLIngester';
import QueryInterface from '@/components/QueryInterface';
import ResultsDisplay from '@/components/ResultsDisplay';
import MetricsDashboard from '@/components/MetricsDashboard';
import QueryHistory from '@/components/QueryHistory';
import { apiClient } from '@/lib/api';

type Tab = 'ingest' | 'query' | 'metrics' | 'history';

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>('query');
  const [isHealthy, setIsHealthy] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      await apiClient.getHealth();
      setIsHealthy(true);
      setLoading(false);
    } catch (err) {
      setIsHealthy(false);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-2xl font-bold mb-4">🚀 Initializing...</p>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    );
  }

  if (!isHealthy) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center bg-red-50 border border-red-200 rounded-lg p-8 max-w-md">
          <p className="text-2xl mb-4">⚠️ Backend Unavailable</p>
          <p className="text-gray-600 mb-4">
            Unable to connect to the backend API. Please ensure it's running on
            http://localhost:8000
          </p>
          <button
            onClick={checkHealth}
            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition"
          >
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Tabs */}
      <div className="mb-8">
        <div className="flex flex-wrap gap-2 border-b border-gray-200">
          <TabButton
            active={activeTab === 'ingest'}
            onClick={() => setActiveTab('ingest')}
          >
            📤 Ingest Data
          </TabButton>
          <TabButton
            active={activeTab === 'query'}
            onClick={() => setActiveTab('query')}
          >
            🔍 Query
          </TabButton>
          <TabButton
            active={activeTab === 'metrics'}
            onClick={() => setActiveTab('metrics')}
          >
            📊 Metrics
          </TabButton>
          <TabButton
            active={activeTab === 'history'}
            onClick={() => setActiveTab('history')}
          >
            📜 History
          </TabButton>
        </div>
      </div>

      {/* Tab Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {activeTab === 'ingest' && (
            <div className="space-y-8">
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <DocumentUploader />
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <URLIngester />
              </div>
            </div>
          )}

          {activeTab === 'query' && (
            <div className="space-y-8">
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <QueryInterface />
              </div>
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <ResultsDisplay />
              </div>
            </div>
          )}

          {activeTab === 'metrics' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <MetricsDashboard />
            </div>
          )}

          {activeTab === 'history' && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <QueryHistory />
            </div>
          )}
        </div>

        {/* Sidebar - Always Show Metrics */}
        <div className="lg:col-span-1">
          <div className="sticky top-20">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <QuickStats />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-3 font-medium border-b-2 transition ${
        active
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-gray-600 hover:text-gray-900'
      }`}
    >
      {children}
    </button>
  );
}

function QuickStats() {
  const [stats, setStats] = useState({
    total_queries: 0,
    avg_latency: 0,
    avg_faithfulness: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await apiClient.getMetrics();
      setStats({
        total_queries: response.data.total_queries,
        avg_latency: response.data.avg_latency,
        avg_faithfulness: response.data.avg_faithfulness,
      });
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center text-gray-500">Loading...</div>;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-700">📈 Quick Stats</h3>

      <div className="space-y-3">
        <StatItem
          icon="🔍"
          label="Total Queries"
          value={stats.total_queries}
        />
        <StatItem
          icon="⚡"
          label="Avg Latency"
          value={`${stats.avg_latency.toFixed(0)}ms`}
        />
        <StatItem
          icon="✅"
          label="Avg Faithfulness"
          value={`${(stats.avg_faithfulness * 100).toFixed(0)}%`}
        />
      </div>

      <div className="text-xs text-gray-500 text-center mt-4">
        Auto-refreshes every 15s
      </div>
    </div>
  );
}

function StatItem({
  icon,
  label,
  value,
}: {
  icon: string;
  label: string;
  value: string | number;
}) {
  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-2">
        <span className="text-2xl">{icon}</span>
        <p className="text-sm font-medium text-gray-700">{label}</p>
      </div>
      <p className="text-lg font-bold text-gray-900">{value}</p>
    </div>
  );
}