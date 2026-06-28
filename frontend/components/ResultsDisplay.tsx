'use client';

import { useRAGStore } from '@/lib/store';
import { FiChevronDown } from 'react-icons/fi';
import { useState } from 'react';

export default function ResultsDisplay() {
  const { currentResult } = useRAGStore();
  const [expandedSource, setExpandedSource] = useState<number | null>(null);

  if (!currentResult) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No results yet. Ask a question to get started!</p>
      </div>
    );
  }

  const { query, answer, sources, metrics } = currentResult;

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-700 mb-2">Question</h3>
        <p className="text-gray-600">{query}</p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-700 mb-3">Answer</h3>
        <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{answer}</p>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-700 mb-3">📊 Quality Metrics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            label="Faithfulness"
            value={metrics.faithfulness}
            description="Sticks to documents"
          />
          <MetricCard
            label="Relevance"
            value={metrics.answer_relevance}
            description="Answers question"
          />
          <MetricCard
            label="Context"
            value={metrics.context_relevance}
            description="Documents relevant"
          />
          <MetricCard
            label="Latency"
            value={metrics.latency_ms / 1000}
            description="Response time (s)"
          />
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-700 mb-3">📚 Sources</h3>
        <div className="space-y-2">
          {sources.map((source, idx) => (
            <div key={idx} className="border border-gray-300 rounded-lg overflow-hidden">
              <button
                onClick={() =>
                  setExpandedSource(expandedSource === idx ? null : idx)
                }
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition"
              >
                <div className="text-left">
                  <p className="font-semibold text-gray-700">{source.filename}</p>
                  <p className="text-sm text-gray-500">
                    Relevance: {(source.relevance_score * 100).toFixed(0)}%
                  </p>
                </div>
                <FiChevronDown
                  className={`transition-transform ${
                    expandedSource === idx ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {expandedSource === idx && (
                <div className="bg-gray-50 p-4 border-t border-gray-300">
                  <p className="text-gray-700 text-sm leading-relaxed">
                    {source.text}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  description,
}: {
  label: string;
  value: number;
  description: string;
}) {
  const percentage = Math.round(value * 100);
  const color =
    value >= 0.8 ? 'bg-green-100' : value >= 0.6 ? 'bg-yellow-100' : 'bg-red-100';

  return (
    <div className={`${color} rounded-lg p-4 text-center`}>
      <p className="text-sm font-medium text-gray-700">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-2">
        {percentage}%
      </p>
      <p className="text-xs text-gray-600 mt-1">{description}</p>
    </div>
  );
}