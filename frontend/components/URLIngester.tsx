'use client';

import { useState } from 'react';
import { FiGlobe } from 'react-icons/fi';
import { apiClient } from '@/lib/api';

export default function URLIngester() {
  const [url, setUrl] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (!url) {
        throw new Error('Please enter a URL');
      }

      const response = await apiClient.ingestUrl(url, name);
      setSuccess(`✓ Successfully ingested URL (${response.data.chunks_created} chunks)`);
      setUrl('');
      setName('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to ingest URL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">🌐 Ingest from URL</h2>

      <form onSubmit={handleIngest} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            URL
          </label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Name (Optional)
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., OpenAI Documentation"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          {loading ? '⏳ Ingesting...' : '🌐 Ingest URL'}
        </button>
      </form>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          ❌ {error}
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {success}
        </div>
      )}
    </div>
  );
}