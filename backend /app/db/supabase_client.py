from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
import uuid
import json
from typing import Optional, List, Dict, Any

# Check if we have valid Supabase credentials
HAS_REAL_DB = (
    SUPABASE_URL and 
    SUPABASE_SERVICE_KEY and 
    not SUPABASE_URL.startswith("https://test.") and
    not SUPABASE_SERVICE_KEY.startswith("dummy_")
)

# Initialize table references for public schema
DOCUMENTS_TABLE = "documents"
CHUNKS_TABLE = "doc_chunks"

if HAS_REAL_DB:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Test connection with simple public schema tables
        print(f"🧪 Testing connection to {DOCUMENTS_TABLE}...")
        result = supabase.table(DOCUMENTS_TABLE).select("id").limit(1).execute()
        print(f"✅ Connected to Supabase database using public schema")
        
    except Exception as e:
        print(f"⚠️  Supabase connection failed, using mock database: {e}")
        HAS_REAL_DB = False
        supabase = None
else:
    supabase = None
    print("⚠️  Using mock database - no valid Supabase credentials detected")

# Mock in-memory storage for testing
mock_documents: Dict[str, Dict] = {}
mock_chunks: List[Dict] = []

def insert_document(name: str, file_count: int, meta: dict) -> str:
    if HAS_REAL_DB and supabase:
        r = supabase.table(DOCUMENTS_TABLE).insert({"name": name, "file_count": file_count, "meta": meta}).execute()
        return r.data[0]["id"]
    else:
        # Mock document insertion
        doc_id = str(uuid.uuid4())
        mock_documents[doc_id] = {
            "id": doc_id,
            "name": name,
            "file_count": file_count,
            "page_count": 0,
            "meta": meta
        }
        return doc_id

def update_page_count(doc_id: str, page_count: int) -> None:
    if HAS_REAL_DB and supabase:
        supabase.table(DOCUMENTS_TABLE).update({"page_count": page_count}).eq("id", doc_id).execute()
    else:
        # Mock update
        if doc_id in mock_documents:
            mock_documents[doc_id]["page_count"] = page_count

def insert_chunks(rows: List[dict]) -> None:
    # rows: {doc_id, source_path, page_number, content, embedding}
    if HAS_REAL_DB and supabase:
        supabase.table(CHUNKS_TABLE).insert(rows).execute()
    else:
        # Mock chunks insertion
        for row in rows:
            chunk = {
                "id": str(uuid.uuid4()),
                **row
            }
            mock_chunks.append(chunk)

def rpc_match_chunks(query_embedding: List[float], top_k: int, filter_doc: Optional[str], filter_meta: Optional[dict]):
    if HAS_REAL_DB and supabase:
        payload = {
            "query_embedding": query_embedding,
            "match_count": top_k,
            "filter_doc": filter_doc,
            "filter_meta": filter_meta,
        }
        return supabase.rpc("match_doc_chunks", payload).execute().data
    else:
        # Mock search - return chunks for the filtered document
        filtered_chunks = [
            chunk for chunk in mock_chunks 
            if not filter_doc or chunk.get("doc_id") == filter_doc
        ]
        # Return first top_k chunks with mock similarity scores
        results = []
        for i, chunk in enumerate(filtered_chunks[:top_k]):
            results.append({
                "id": chunk["id"],
                "source_path": chunk["source_path"],
                "page_number": chunk["page_number"],
                "content": chunk["content"],
                "similarity": 0.8 - (i * 0.1)  # Mock decreasing similarity
            })
        return results

