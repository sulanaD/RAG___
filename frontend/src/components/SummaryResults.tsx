import React from 'react';
import { FileText, Clock } from 'lucide-react';
import { SummarizeResponse } from '../api';

interface SummaryResultsProps {
  results: SummarizeResponse;
}

export function SummaryResults({ results }: SummaryResultsProps) {
  return (
    <div className="flex-1 overflow-y-auto">
      <div className="p-4">
        <div className="mb-4">
          <div className="flex items-center mb-3">
            <FileText className="w-5 h-5 text-primary-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Page Summary</h3>
          </div>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium text-green-800">
                {results.title || `Page ${results.page_number}`}
              </h4>
              <div className="flex items-center text-xs text-green-600">
                <Clock className="w-3 h-3 mr-1" />
                {results.cached ? 'Cached' : 'Generated'}
              </div>
            </div>
            
            <p className="text-sm text-green-900 leading-relaxed whitespace-pre-wrap">
              {results.summary}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
            <div className="flex items-center">
              <span className="font-medium mr-2">Document ID:</span>
              <span className="font-mono text-xs truncate">{results.doc_id || 'N/A'}</span>
            </div>
            <div className="flex items-center">
              <span className="font-medium mr-2">Page:</span>
              <span>{results.page_number || 'N/A'}</span>
            </div>
            <div className="flex items-center">
              <span className="font-medium mr-2">Source Pages:</span>
              <span>{results.source_pages}</span>
            </div>
            <div className="flex items-center">
              <span className="font-medium mr-2">Chunk ID:</span>
              <span className="font-mono text-xs truncate">{results.chunk_id || 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}