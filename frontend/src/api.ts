import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for all requests
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface UploadResponse {
  doc_id: string;
  file_count: number;
  page_count: number;
  pages_index: Array<{
    chunk_id: string;
    source_path: string;
    page_number: number;
    title: string;
  }>;
}

export interface SearchRequest {
  query: string;
  top_k?: number;
  scope?: 'document' | 'page';
  doc_id?: string;
  selected_chunk_id?: string;
  filter_meta?: Record<string, any>;
}

export interface SearchHit {
  chunk_id: string;
  doc_id: string;
  page_number: number;
  title: string;
  snippet: string;
  similarity: number;
  highlights?: Array<{ start: number; end: number }>;
}

export interface SearchResponse {
  answer: string;
  hits: SearchHit[];
}

export interface SummarizeResponse {
  doc_id?: string;
  chunk_id?: string;
  page_number?: number;
  title?: string;
  summary: string;
  cached: boolean;
  source_pages: number;
}

export interface ChunkResponse {
  doc_id?: string;
  chunk_id?: string;
  page_number?: number;
  title?: string;
  text: string;
}

export const apiService = {
  // Upload ZIP file
  async uploadZip(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    // Use extended timeout for upload processing - 10 minutes for large files
    const response = await api.post('/upload-zip', formData, {
      timeout: 600000, // 10 minutes for upload processing
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Search documents
  async search(request: SearchRequest): Promise<SearchResponse> {
    const response = await api.post('/search', request);
    return response.data;
  },

  // Summarize page
  async summarizePage(chunkId: string): Promise<SummarizeResponse> {
    const response = await api.get(`/summarize-page/${chunkId}`);
    return response.data;
  },

  // Fetch original chunk content
  async getChunk(chunkId: string): Promise<ChunkResponse> {
    const response = await api.get(`/chunk/${chunkId}`);
    return response.data;
  },

  // Health check
  async healthCheck(): Promise<{ ok: boolean }> {
    const response = await api.get('/healthz');
    return response.data;
  },
};