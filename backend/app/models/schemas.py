from typing import Any, Dict, List, Optional
from pydantic import BaseModel

# Upload response
class UploadZipResponse(BaseModel):
    doc_id: str
    file_count: int
    page_count: int
    pages_index: List[Dict[str, Any]]  # [{chunk_id, source_path, page_number, title}]

# Summarize (page) response
class SummarizeResponse(BaseModel):
    doc_id: Optional[str] = None
    chunk_id: Optional[str] = None
    page_number: Optional[int] = None
    title: Optional[str] = None
    summary: str
    cached: bool = False
    source_pages: int = 1

# Search request/response
class SearchRequest(BaseModel):
    query: str
    top_k: int = 6
    scope: Optional[str] = "document"   # "page" | "document"
    doc_id: Optional[str] = None
    selected_chunk_id: Optional[str] = None
    filter_meta: Optional[Dict[str, Any]] = None

class SearchHit(BaseModel):
    chunk_id: str
    doc_id: str
    page_number: int
    title: str
    snippet: str
    similarity: float
    highlights: Optional[List[Dict[str, int]]] = None

class SearchResponse(BaseModel):
    answer: str
    hits: List[SearchHit]

