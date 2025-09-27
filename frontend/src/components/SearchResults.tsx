// React import not required with the new JSX transform
import { Search, ChevronRight } from 'lucide-react';
import { SearchResponse } from '../api';

interface SearchResultsProps {
  results: SearchResponse;
  onPageSelect: (pageNumber: number) => void;
}

export function SearchResults({ results, onPageSelect }: SearchResultsProps) {
  const getHighlightedText = (text: string, highlights?: Array<{ start: number; end: number }>) => {
    if (!highlights || highlights.length === 0) {
      return text;
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

    return parts;
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="p-4">
        {/* AI Answer */}
        <div className="mb-6">
          <div className="flex items-center mb-3">
            <Search className="w-5 h-5 text-primary-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">AI Answer</h3>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-900 whitespace-pre-wrap">{results.answer}</p>
          </div>
        </div>

        {/* Search Hits */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-3">
            Search Results ({results.hits.length} matches)
          </h4>
          <div className="space-y-3">
            {results.hits.map((hit, _index) => (
              <div
                key={hit.chunk_id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h5 className="text-sm font-medium text-gray-900">{hit.title}</h5>
                    <p className="text-xs text-gray-500 mt-1">
                      Page {hit.page_number} • Similarity: {(hit.similarity * 100).toFixed(1)}%
                    </p>
                  </div>
                  <button
                    onClick={() => onPageSelect(hit.page_number)}
                    className="ml-2 inline-flex items-center text-xs text-primary-600 hover:text-primary-700 font-medium"
                  >
                    View Page
                    <ChevronRight className="w-3 h-3 ml-1" />
                  </button>
                </div>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {getHighlightedText(hit.snippet, hit.highlights)}
                </p>
              </div>
            ))}
          </div>
        </div>

        {results.hits.length === 0 && (
          <div className="text-center py-8">
            <Search className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Found</h3>
            <p className="text-sm text-gray-600">
              Try adjusting your search query or search scope.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}