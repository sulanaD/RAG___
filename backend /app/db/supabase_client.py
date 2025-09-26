from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY
import requests
import uuid
from typing import Optional, List

# Initialize table references for public schema
DOCUMENTS_TABLE = "documents"
CHUNKS_TABLE = "doc_chunks"

# Validate we have credentials; fail fast if not present or clearly invalid
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("Supabase credentials missing. Set SUPABASE_URL and SUPABASE_SERVICE_KEY in your environment (.env).")

if SUPABASE_URL.startswith("https://test."):
    raise RuntimeError("Supabase test URL detected. Please set a real SUPABASE_URL in .env.")

if SUPABASE_SERVICE_KEY.startswith("dummy_"):
    raise RuntimeError("Supabase service key looks like a dummy value. Set the real SUPABASE_SERVICE_KEY in .env.")

# First, validate REST access using both the publishable (anon) and secret (service) keys.
rest_check_url = f"{SUPABASE_URL}/rest/v1/{DOCUMENTS_TABLE}?select=id&limit=1"
print(f"🧪 Testing REST access to {rest_check_url} using provided keys...")
# First try using the publishable (anon) key as 'apikey' header (no Authorization). This often suffices for GET selects.
try:
    resp = requests.get(rest_check_url, headers={"apikey": SUPABASE_ANON_KEY}, timeout=10)
except Exception as e:
    raise RuntimeError(f"Failed to reach Supabase REST endpoint {rest_check_url}: {e}")

if resp.status_code == 200 or resp.status_code == 204:
    print("✅ REST check passed using publishable key (apikey header)")
else:
    # If publishable key didn't work, try using both apikey and Authorization (service key)
    try:
        resp2 = requests.get(rest_check_url, headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}, timeout=10)
    except Exception as e:
        raise RuntimeError(f"Failed to reach Supabase REST endpoint with combined headers: {e}")
    if resp2.status_code in (200, 204):
        print("✅ REST check passed using publishable + service key (apikey + Authorization)")
    else:
        # Surface server error with guidance
        raise RuntimeError(
            f"Supabase REST check returned status {resp2.status_code}: {resp2.text}\n"
            "Hint: Ensure SUPABASE_ANON_KEY (publishable) and SUPABASE_SERVICE_KEY (secret) are correct, and that REST access is enabled for the key."
        )

# If REST check succeeded, initialize the Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print(f"✅ Connected to Supabase (REST OK). Created supabase client for {SUPABASE_URL}")
except Exception as e:
    raise RuntimeError(f"Supabase client creation failed: {e}")


def insert_document(name: str, file_count: int, meta: dict) -> str:
    r = supabase.table(DOCUMENTS_TABLE).insert({"name": name, "file_count": file_count, "meta": meta}).execute()
    # supabase client returns an object with .data attribute in many versions; be defensive
    data = getattr(r, "data", None)
    if data is None:
        # try dict-like access
        try:
            data = r.get("data")
        except Exception:
            data = None
    if not data:
        raise RuntimeError(f"Failed to insert document, unexpected response: {r}")
    return data[0]["id"]


def update_page_count(doc_id: str, page_count: int) -> None:
    r = supabase.table(DOCUMENTS_TABLE).update({"page_count": page_count}).eq("id", doc_id).execute()
    data = getattr(r, "data", None)
    if data is None:
        try:
            data = r.get("data")
        except Exception:
            data = None
    # If update returns no data and status code indicates error, raise
    status = getattr(r, "status_code", None) or getattr(r, "status", None)
    if data is None and status and int(status) >= 400:
        raise RuntimeError(f"Failed to update page_count for {doc_id}: status={status}, resp={r}")


def insert_chunks(rows: List[dict]) -> None:
    # rows: {doc_id, source_path, page_number, content, embedding}
    r = supabase.table(CHUNKS_TABLE).insert(rows).execute()
    data = getattr(r, "data", None)
    if data is None:
        try:
            data = r.get("data")
        except Exception:
            data = None
    status = getattr(r, "status_code", None) or getattr(r, "status", None)
    if data is None and status and int(status) >= 400:
        raise RuntimeError(f"Failed to insert chunks: status={status}, resp={r}")


def rpc_match_chunks(query_embedding: List[float], top_k: int, filter_doc: Optional[str], filter_meta: Optional[dict]):
    payload = {
        "query_embedding": query_embedding,
        "match_count": top_k,
        "filter_doc": filter_doc,
        "filter_meta": filter_meta,
    }
    r = supabase.rpc("match_doc_chunks", payload).execute()
    data = getattr(r, "data", None)
    if data is None:
        try:
            data = r.get("data")
        except Exception:
            data = None
    status = getattr(r, "status_code", None) or getattr(r, "status", None)
    if data is None and status and int(status) >= 400:
        raise RuntimeError(f"Supabase RPC match_doc_chunks failed: status={status}, resp={r}")
    # Normalize the returned rows to a canonical form to simplify callers.
    # Expected canonical keys: id, doc_id, page_number, similarity, content (optional)
    rows = data or []
    normalized = []
    try:
        for item in rows:
            # item might be a dict-like, or a row with nested keys
            if not isinstance(item, dict):
                # try to coerce
                try:
                    item = dict(item)
                except Exception:
                    # fallback: append as-is
                    normalized.append({"id": None, "doc_id": None, "page_number": None, "similarity": 0.0, "content": None})
                    continue

            # try multiple key names for id/doc/page/similarity
            rid = item.get("id") or item.get("chunk_id") or item.get("doc_chunk_id") or item.get("chunk")
            docid = item.get("doc_id") or item.get("document_id") or item.get("docid")
            page = item.get("page_number") or item.get("page") or item.get("page_num") or item.get("p")
            sim = item.get("similarity") or item.get("score") or item.get("cosine") or item.get("distance")

            # If the RPC included nested 'match' or 'payload' fields, try to extract
            if rid is None and "match" in item and isinstance(item["match"], dict):
                m = item["match"]
                rid = m.get("id") or m.get("chunk_id")
                docid = docid or m.get("doc_id")
                page = page or m.get("page_number")
                sim = sim or m.get("similarity") or m.get("score")

            # content may already be included from RPC
            content = item.get("content") or item.get("payload") or item.get("data")

            # coerce types
            try:
                page_num = int(page) if page is not None else None
            except Exception:
                page_num = None

            try:
                similarity = float(sim) if sim is not None else 0.0
            except Exception:
                # sometimes distance is returned and lower=better; we will treat non-negative numbers as-is
                try:
                    similarity = float(sim)
                except Exception:
                    similarity = 0.0

            normalized.append({
                "id": rid,
                "doc_id": docid,
                "page_number": page_num,
                "similarity": similarity,
                "content": content,
                # preserve original item for debugging or fallback
                "_raw": item,
            })
    except Exception:
        # If normalization fails for some reason, return the raw data to avoid breaking callers
        return data

    return normalized

