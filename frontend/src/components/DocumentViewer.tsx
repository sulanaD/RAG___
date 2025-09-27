// React import not required with the new JSX transform
import { ChevronLeft, ChevronRight, FileText, Upload } from 'lucide-react';
import { Document } from '../App';
import { SearchResponse } from '../api';
import { apiService } from '../api';
import { useEffect, useState } from 'react';
import { FolderBrowser } from './FolderBrowser';

interface DocumentViewerProps {
  document: Document;
  selectedPage: number | null;
  searchResults: SearchResponse | null;
  onPageSelect: (pageNumber: number) => void;
  onNewUpload: () => void;
}

export function DocumentViewer({
  document,
  selectedPage,
  searchResults,
  onPageSelect,
  onNewUpload,
}: DocumentViewerProps) {
  const [originalText, setOriginalText] = useState<string | null>(null);
  const [loadingOriginal, setLoadingOriginal] = useState(false);
  const [pageTitles, setPageTitles] = useState<Record<string, string>>({});
  const [pageTexts, setPageTexts] = useState<Record<string, string>>({});

  useEffect(() => {
    // Fetch the original chunk text whenever selectedPage changes
    let cancelled = false;
    async function fetchOriginal() {
      setOriginalText(null);
      if (!selectedPage) return;
      const pageInfo = document.pages.find(p => p.page_number === selectedPage);
      if (!pageInfo) return;
      // If we already have the text cached from bulk fetch, use it
      if (pageTexts[pageInfo.chunk_id]) {
        setOriginalText(pageTexts[pageInfo.chunk_id]);
        return;
      }
      setLoadingOriginal(true);
      try {
        const chunk = await apiService.getChunk(pageInfo.chunk_id);
        if (!cancelled) setOriginalText(chunk.text || null);
        if (chunk.text) {
          setPageTexts(prev => ({ ...prev, [pageInfo.chunk_id]: String(chunk.text) }));
        }
        if (chunk.title) {
          setPageTitles(prev => ({ ...prev, [pageInfo.chunk_id]: String(chunk.title) }));
        }
      } catch (e) {
        console.error('Failed to fetch chunk text', e);
        if (!cancelled) setOriginalText(null);
      } finally {
        if (!cancelled) setLoadingOriginal(false);
      }
    }
    fetchOriginal();
    return () => { cancelled = true; };
  }, [selectedPage, document.pages]);

  // Prefetch titles/text for all pages when document changes
  useEffect(() => {
    let cancelled = false;
    async function fetchAll() {
      const promises = document.pages.map(async (p) => {
        try {
          const chunk = await apiService.getChunk(p.chunk_id);
          return { id: p.chunk_id, title: chunk.title, text: chunk.text };
        } catch (e) {
          return { id: p.chunk_id, title: undefined, text: undefined };
        }
      });
      const results = await Promise.all(promises);
      if (cancelled) return;
      const titles: Record<string, string> = {};
      const texts: Record<string, string> = {};
      results.forEach(r => {
        if (r.title) titles[r.id] = String(r.title);
        if (r.text) texts[r.id] = String(r.text);
      });
      setPageTitles(prev => ({ ...prev, ...titles }));
      setPageTexts(prev => ({ ...prev, ...texts }));
    }
    fetchAll();
    return () => { cancelled = true; };
  }, [document]);
  const currentPage = document.pages.find(p => p.page_number === selectedPage);
  const sortedPages = document.pages.sort((a, b) => a.page_number - b.page_number);
  const currentIndex = sortedPages.findIndex(p => p.page_number === selectedPage);

  const navigatePage = (direction: 'prev' | 'next') => {
    if (direction === 'prev' && currentIndex > 0) {
      onPageSelect(sortedPages[currentIndex - 1].page_number);
    } else if (direction === 'next' && currentIndex < sortedPages.length - 1) {
      onPageSelect(sortedPages[currentIndex + 1].page_number);
    }
  };

  const getHighlightedContent = (text: string, highlights?: Array<{ start: number; end: number }>) => {
    if (!highlights || highlights.length === 0) {
      return <span>{text}</span>;
    }

    const parts = [];
    let lastIndex = 0;

    // Sort highlights by start position
    const sortedHighlights = highlights.sort((a, b) => a.start - b.start);

    sortedHighlights.forEach((highlight, index) => {
      // Add text before highlight
      if (highlight.start > lastIndex) {
        parts.push(text.slice(lastIndex, highlight.start));
      }

      // Add highlighted text
      parts.push(
        <mark key={index} className="bg-yellow-200 px-1 rounded">
          {text.slice(highlight.start, highlight.end)}
        </mark>
      );

      lastIndex = highlight.end;
    });

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return <span>{parts}</span>;
  };

  const getPageContent = () => {
    if (!currentPage) return null;

    // Find search hit for current page if search results exist
    const searchHit = searchResults?.hits.find(hit => hit.page_number === selectedPage);
    
    if (searchHit) {
      return (
        <div className="space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <p className="text-sm text-yellow-800 font-medium mb-2">Search Match Found</p>
            <p className="text-sm text-yellow-700">
              {getHighlightedContent(searchHit.snippet, searchHit.highlights)}
            </p>
            <p className="text-xs text-yellow-600 mt-2">
              Similarity: {(searchHit.similarity * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      );
    }

    return (
      <div className="text-sm text-gray-600">
        {loadingOriginal ? (
          <p>Loading page content...</p>
        ) : originalText ? (
          <div className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">{originalText}</div>
        ) : (
          <>
            <p>No content preview available for this page.</p>
            <p className="mt-2">Use the search function to find relevant content in your documents.</p>
          </>
        )}
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Document Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h3 className="text-lg font-medium text-gray-900 truncate">{document.name}</h3>
            <p className="text-sm text-gray-500">
              {document.pages.length} pages • {selectedPage ? `Page ${selectedPage}` : 'No page selected'}
            </p>
          </div>
          <button
            onClick={onNewUpload}
            className="ml-4 inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <Upload className="w-4 h-4 mr-1" />
            New Upload
          </button>
        </div>
      </div>

      {/* Page Navigation */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigatePage('prev')}
            disabled={currentIndex <= 0}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Previous
          </button>

          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-gray-400" />
            <span className="text-sm font-medium text-gray-700">
              {currentPage ? (pageTitles[currentPage.chunk_id] || currentPage.title || 'Select a page') : 'Select a page'}
            </span>
          </div>

          <button
            onClick={() => navigatePage('next')}
            disabled={currentIndex >= sortedPages.length - 1}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
            <ChevronRight className="w-4 h-4 ml-1" />
          </button>
        </div>
      </div>

      {/* Page List */}
      <div className="flex-1 overflow-y-auto">
        {selectedPage ? (
          <div className="p-4">
            {getPageContent()}
          </div>
        ) : (
          <FolderBrowser 
            pages={sortedPages}
            selectedPage={selectedPage}
            onPageSelect={onPageSelect}
            pageTitles={pageTitles}
          />
        )}
      </div>
    </div>
  );
}