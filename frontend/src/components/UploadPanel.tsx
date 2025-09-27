import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { apiService, UploadResponse } from '../api';

interface UploadPanelProps {
  onUploadSuccess: (response: UploadResponse) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export function UploadPanel({ onUploadSuccess, isLoading, setIsLoading, setError }: UploadPanelProps) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.zip')) {
      setError('Please upload a ZIP file containing your documents.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.uploadZip(file);
      onUploadSuccess(response);
    } catch (error: any) {
      console.error('Upload error:', error);
      
      // Handle different types of errors
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        setError('Upload is taking longer than expected (10+ minutes). For very large files, this may indicate the file contains many documents. Please try with a smaller ZIP file or contact support if the issue persists.');
      } else if (error.response?.status === 413) {
        setError('File is too large. Maximum size is 500MB.');
      } else if (error.response?.status === 400) {
        setError(error.response?.data?.detail || 'Invalid file format. Please upload a ZIP file containing PDF, DOCX, or TXT files.');
      } else if (error.response?.status === 500) {
        setError('Server processing error: ' + (error.response?.data?.detail || 'Internal server error. Please try again.'));
      } else {
        setError(error.response?.data?.detail || 'Failed to upload file. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8">
      <div
        className={`relative w-full max-w-md p-8 border-2 border-dashed rounded-lg transition-colors ${
          dragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          onChange={handleChange}
          className="hidden"
        />
        
        <div className="text-center">
          {isLoading ? (
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mb-4"></div>
              <p className="text-sm text-gray-600 mb-2">Processing your documents...</p>
              <p className="text-xs text-gray-500">This may take several minutes for large files with many documents.</p>
              <p className="text-xs text-gray-500">Please be patient while we extract, filter, and index your content.</p>
            </div>
          ) : (
            <>
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Upload Document Archive
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Drag and drop a ZIP file here, or click to select
              </p>
              <button
                onClick={onButtonClick}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <FileText className="w-4 h-4 mr-2" />
                Select ZIP File
              </button>
            </>
          )}
        </div>
      </div>

      <div className="mt-6 max-w-md">
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-blue-400 mt-0.5" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Supported Formats</h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>Upload a ZIP file containing:</p>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  <li>PDF documents</li>
                  <li>Microsoft Word (.docx) files</li>
                  <li>Text (.txt) files</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}