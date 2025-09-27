import { useState } from 'react';
import { Search, FileText, Loader2 } from 'lucide-react';
import { apiService, SearchRequest, SearchResponse, SummarizeResponse } from '../api';
import { Document } from '../App';

interface ActionPanelProps {
  document: Document;
  selectedPage: number | null;
  activeMode: 'search' | 'summarize';
  onSearchResults: (results: SearchResponse) => void;
  onSummaryResults: (results: SummarizeResponse) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export function ActionPanel({
  document,
  selectedPage,
  activeMode,
  onSearchResults,
  onSummaryResults,
  isLoading,
  setIsLoading,
  setError,
}: ActionPanelProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchScope, setSearchScope] = useState<'document' | 'page'>('document');

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Please enter a search query.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const request: SearchRequest = {
        query: searchQuery.trim(),
        top_k: 6,
        scope: searchScope,
        // Always include doc_id for document-scoped search to avoid cross-document issues
        doc_id: document.id,
      };

      if (searchScope === 'page' && selectedPage) {
        const pageInfo = document.pages.find(p => p.page_number === selectedPage);
        if (pageInfo) {
          request.selected_chunk_id = pageInfo.chunk_id;
        } else {
          setError('Please select a valid page for page-scoped search.');
          setIsLoading(false);
          return;
        }
      }

      console.log('Search request:', request); // Debug logging
      const results = await apiService.search(request);
      console.log('Search results:', results); // Debug logging
      onSearchResults(results);
    } catch (error: any) {
      console.error('Search error:', error);
      setError(error.response?.data?.detail || 'Failed to search. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (!selectedPage) {
      setError('Please select a page to summarize.');
      return;
    }

    const pageInfo = document.pages.find(p => p.page_number === selectedPage);
    if (!pageInfo) {
      setError('Selected page not found.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const results = await apiService.summarizePage(pageInfo.chunk_id);
      onSummaryResults(results);
    } catch (error: any) {
      console.error('Summarize error:', error);
      setError(error.response?.data?.detail || 'Failed to generate summary. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 border-b border-gray-200">
      {activeMode === 'search' ? (
        <div className="space-y-4">
          <div>
            <label htmlFor="search-query" className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <div className="flex space-x-2">
              <input
                id="search-query"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSearch()}
                placeholder="Enter your search query..."
                className="flex-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                disabled={isLoading}
              />
              <button
                onClick={handleSearch}
                disabled={isLoading || !searchQuery.trim()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Scope
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="document"
                  checked={searchScope === 'document'}
                  onChange={(e) => setSearchScope(e.target.value as 'document' | 'page')}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-700">Entire Document</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="page"
                  checked={searchScope === 'page'}
                  onChange={(e) => setSearchScope(e.target.value as 'document' | 'page')}
                  disabled={!selectedPage}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 disabled:opacity-50"
                />
                <span className="ml-2 text-sm text-gray-700">Current Page Only</span>
              </label>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Summarize Page
            </label>
            <p className="text-sm text-gray-600 mb-4">
              {selectedPage
                ? `Generate a summary for page ${selectedPage}`
                : 'Select a page from the document viewer to summarize'}
            </p>
            <button
              onClick={handleSummarize}
              disabled={isLoading || !selectedPage}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating Summary...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4 mr-2" />
                  Generate Summary
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}