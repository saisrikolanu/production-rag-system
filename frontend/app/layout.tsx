import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Production RAG System',
  description: 'Retrieval-Augmented Generation with quality evaluation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <h1 className="text-3xl font-bold text-gray-900">
              🔍 Production RAG System
            </h1>
            <p className="text-gray-600 mt-1">
              Document Intelligence with AI-Powered Search
            </p>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-gray-600">
            <p>
              Built with FastAPI, React, OpenAI, Pinecone & RAGAS
            </p>
            <p className="text-sm mt-2">
              © 2026 Sai Sri Kolanu | AI Engineer
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}