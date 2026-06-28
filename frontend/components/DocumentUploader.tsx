'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUpload } from 'react-icons/fi';
import { apiClient } from '@/lib/api';
import { useRAGStore } from '@/lib/store';

export default function DocumentUploader() {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const { setUploading } = useRAGStore();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setError('');
    setSuccess('');
    setUploading(true);

    try {
      const response = await apiClient.uploadDocuments(acceptedFiles);
      setSuccess(`✓ Successfully uploaded ${response.data.document_ids.length} documents`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [setUploading]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
  });

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">📄 Upload Documents</h2>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <FiUpload className="mx-auto mb-4 text-4xl text-gray-400" />
        {isDragActive ? (
          <p className="text-blue-600 font-semibold">Drop files here...</p>
        ) : (
          <>
            <p className="text-gray-600 font-semibold">Drag files here or click to select</p>
            <p className="text-gray-500 text-sm mt-2">Supported: PDF, TXT, DOCX</p>
          </>
        )}
      </div>

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