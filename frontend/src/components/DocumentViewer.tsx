import React from 'react';
import { ChevronLeft, ChevronRight, FileText, Upload } from 'lucide-react';
import { Document } from '../App';
import { SearchResponse } from '../api';

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
        <p>No content preview available for this page.</p>
        <p className="mt-2">Use the search function to find relevant content in your documents.</p>
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
              {currentPage ? currentPage.title : 'Select a page'}
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
          <div className="p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Documents by Folder:</h4>
            {(() => {
              // Group pages by folder structure
              const folderGroups: Record<string, typeof sortedPages> = {};
              
              sortedPages.forEach(page => {
                const pathParts = page.source_path.split('/');
                const folder = pathParts.length > 1 ? pathParts.slice(0, -1).join('/') : 'Root';
                
                if (!folderGroups[folder]) {
                  folderGroups[folder] = [];
                }
                folderGroups[folder].push(page);
              });

              // Sort folder groups
              const sortedFolders = Object.keys(folderGroups).sort();

              return (
                <div className="space-y-4">
                  {sortedFolders.map(folder => (
                    <div key={folder} className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="bg-gray-50 px-3 py-2 border-b border-gray-200">
                        <h5 className="text-sm font-medium text-gray-700 flex items-center">
                          <FileText className="w-4 h-4 mr-2" />
                          {folder === 'Root' ? '📁 Root Directory' : `📁 ${folder}`}
                          <span className="ml-auto text-xs text-gray-500">
                            {folderGroups[folder].length} pages
                          </span>
                        </h5>
                      </div>
                      <div className="divide-y divide-gray-100">
                        {folderGroups[folder]
                          .sort((a, b) => {
                            // First sort by file name, then by page number
                            const fileA = a.source_path.split('/').pop() || '';
                            const fileB = b.source_path.split('/').pop() || '';
                            if (fileA !== fileB) return fileA.localeCompare(fileB);
                            return a.page_number - b.page_number;
                          })
                          .map((page) => {
                            const fileName = page.source_path.split('/').pop() || '';
                            return (
                              <button
                                key={page.chunk_id}
                                onClick={() => onPageSelect(page.page_number)}
                                className="w-full text-left p-3 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset transition-colors"
                              >
                                <div className="flex items-start justify-between">
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center">
                                      <span className="text-sm font-medium text-gray-900 mr-2">
                                        {fileName}
                                      </span>
                                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                        Page {page.page_number}
                                      </span>
                                    </div>
                                    <p className="text-sm text-gray-600 mt-1 truncate">{page.title}</p>
                                  </div>
                                  <FileText className="w-4 h-4 text-gray-400 ml-2 flex-shrink-0" />
                                </div>
                              </button>
                            );
                          })}
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>
        )}
      </div>
    </div>
  );
}