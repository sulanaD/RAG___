import re
from typing import List
from fastapi import APIRouter, HTTPException
from app.db.supabase_client import supabase, rpc_match_chunks
from app.services.ai import embed, rag_answer
from app.models.schemas import SearchRequest, SearchResponse, SearchHit

router = APIRouter(prefix="", tags=["search"])

@router.post("/search", response_model=SearchResponse)
def semantic_search(req: SearchRequest):
    scope = (req.scope or "document").lower()

    # Page scope: use only the selected chunk as context
    if scope == "page":
        if not req.selected_chunk_id:
            raise HTTPException(status_code=400, detail="selected_chunk_id required when scope='page'")
        full = supabase.table("doc_chunks").select("doc_id, page_number, content, id") \
            .eq("id", req.selected_chunk_id).single().execute().data
        if not full:
            raise HTTPException(status_code=404, detail="Chunk not found")
        text = full["content"]["text"]
        answer = rag_answer(req.query, [text])
        hit = SearchHit(
            chunk_id=full["id"],
            doc_id=full["doc_id"],
            page_number=int(full["page_number"]),
            title=full["content"].get("title") or "Untitled",
            snippet=text[:800],
            similarity=1.0,
            highlights=None
        )
        return SearchResponse(answer=answer, hits=[hit])

    # Document scope: ANN search within doc (or across all if doc_id omitted)
    qvec = embed([req.query])[0]
    rows = rpc_match_chunks(qvec, req.top_k, req.doc_id, req.filter_meta)

    # Defensive: if rows is not a list, log/raise a helpful error
    if not isinstance(rows, list):
        # convert to list if possible
        try:
            rows = list(rows)
        except Exception:
            raise HTTPException(status_code=500, detail=f"Unexpected RPC response shape: {type(rows)}. Expected list of rows.")

    terms = [t for t in re.split(r"[\\s,.;:?]+", req.query) if len(t) >= 3]
    contexts: List[str] = []
    hits: List[SearchHit] = []

    for r in rows:
        # Normalize keys that may come from RPC (some installations return snake_case or nested fields)
        # We'll try several common alternatives when extracting identifiers.
        rid = r.get("id") or r.get("chunk_id") or r.get("doc_chunk_id") or r.get("chunk")
        docid = r.get("doc_id") or r.get("document_id") or r.get("docid")
        page_num = r.get("page_number") or r.get("page") or r.get("page_num")

        # Fetch the full content for this chunk to extract text/title safely
        full = None
        if rid:
            full = supabase.table("doc_chunks").select("content").eq("id", rid).single().execute().data
        else:
            # as a last resort, if RPC returned nested content already, try to use it directly
            full = r.get("content") and {"content": r.get("content")}
        text = ""
        title = None
        if full and full.get("content"):
            content = full["content"]
            text = content.get("text", "") or ""
            title = content.get("title")
        contexts.append(text)

        # rudimentary highlights
        hl, lower = [], text.lower()
        for t in terms:
            pos = lower.find(t.lower())
            if pos != -1:
                hl.append({"start": pos, "end": pos + len(t)})
            if len(hl) >= 5:
                break

        # Safely coerce similarity to float if present
        sim = r.get("similarity") or r.get("score") or r.get("cosine") or 0.0
        try:
            sim = float(sim)
        except Exception:
            sim = 0.0

        hits.append(SearchHit(
            chunk_id=rid or r.get("id"),
            doc_id=docid or r.get("doc_id"),
            page_number=int(page_num or r.get("page_number") or 0),
            title=title or "Untitled",
            snippet=(text[:800] if text else ""),
            similarity=sim,
            highlights=hl or None
        ))
    # Build a citations mapping matching the [p1], [p2] markers used by rag_answer
    citations = []
    for h in hits:
        citations.append({"page_number": h.page_number, "chunk_id": h.chunk_id})

    answer = rag_answer(req.query, contexts, citations=citations)
    return SearchResponse(answer=answer, hits=hits)
