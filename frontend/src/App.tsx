import React, { useState, useCallback } from 'react';
import { UploadPanel } from './components/UploadPanel';
import { ActionPanel } from './components/ActionPanel';
import { DocumentViewer } from './components/DocumentViewer';
import { SearchResults } from './components/SearchResults';
import { SummaryResults } from './components/SummaryResults';
import { UploadResponse, SearchResponse, SummarizeResponse } from './api';
import clsx from 'clsx';

export interface Document {
  id: string;
  name: string;
  pages: Array<{
    chunk_id: string;
    source_path: string;
    page_number: number;
    title: string;
  }>;
}

function App() {
  const [document, setDocument] = useState<Document | null>(null);
  const [selectedPage, setSelectedPage] = useState<number | null>(null);
  const [activeMode, setActiveMode] = useState<'search' | 'summarize'>('search');
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [summaryResults, setSummaryResults] = useState<SummarizeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUploadSuccess = useCallback((response: UploadResponse) => {
    const doc: Document = {
      id: response.doc_id,
      name: `Document (${response.file_count} files, ${response.page_count} pages)`,
      pages: response.pages_index,
    };
    setDocument(doc);
    setSelectedPage(1);
    setError(null);
    setSearchResults(null);
    setSummaryResults(null);
  }, []);

  const handleSearchResults = useCallback((results: SearchResponse) => {
    setSearchResults(results);
    setSummaryResults(null);
    setActiveMode('search');
  }, []);

  const handleSummaryResults = useCallback((results: SummarizeResponse) => {
    setSummaryResults(results);
    setSearchResults(null);
    setActiveMode('summarize');
  }, []);

  const handlePageSelect = useCallback((pageNumber: number) => {
    setSelectedPage(pageNumber);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">RAG Document Intelligence</h1>
          <p className="text-sm text-gray-600 mt-1">
            Upload documents, search content, and generate summaries with AI
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          {/* Left Panel */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Document Upload & Preview</h2>
            </div>
            
            {!document ? (
              <UploadPanel 
                onUploadSuccess={handleUploadSuccess}
                isLoading={isLoading}
                setIsLoading={setIsLoading}
                setError={setError}
              />
            ) : (
              <DocumentViewer
                document={document}
                selectedPage={selectedPage}
                searchResults={searchResults}
                onPageSelect={handlePageSelect}
                onNewUpload={() => {
                  setDocument(null);
                  setSelectedPage(null);
                  setSearchResults(null);
                  setSummaryResults(null);
                }}
              />
            )}
          </div>

          {/* Right Panel */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Actions & Results</h2>
                {document && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setActiveMode('search')}
                      className={clsx(
                        'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                        activeMode === 'search'
                          ? 'bg-primary-500 text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      )}
                    >
                      Search
                    </button>
                    <button
                      onClick={() => setActiveMode('summarize')}
                      className={clsx(
                        'px-3 py-1 rounded-md text-sm font-medium transition-colors',
                        activeMode === 'summarize'
                          ? 'bg-primary-500 text-white'
                          : 'text-gray-600 hover:bg-gray-100'
                      )}
                    >
                      Summarize
                    </button>
                  </div>
                )}
              </div>
            </div>

            {!document ? (
              <div className="flex-1 flex items-center justify-center p-8">
                <div className="text-center text-gray-500">
                  <p className="text-lg font-medium">Upload a document to get started</p>
                  <p className="text-sm mt-2">Upload a ZIP file containing PDF, DOCX, or TXT files to begin searching and summarizing.</p>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col overflow-hidden">
                <ActionPanel
                  document={document}
                  selectedPage={selectedPage}
                  activeMode={activeMode}
                  onSearchResults={handleSearchResults}
                  onSummaryResults={handleSummaryResults}
                  isLoading={isLoading}
                  setIsLoading={setIsLoading}
                  setError={setError}
                />
                
                <div className="flex-1 overflow-hidden">
                  {activeMode === 'search' && searchResults && (
                    <SearchResults results={searchResults} onPageSelect={handlePageSelect} />
                  )}
                  
                  {activeMode === 'summarize' && summaryResults && (
                    <SummaryResults results={summaryResults} />
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="mt-1 text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;