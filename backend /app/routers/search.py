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

    terms = [t for t in re.split(r"[\\s,.;:?]+", req.query) if len(t) >= 3]
    contexts: List[str] = []
    hits: List[SearchHit] = []

    for r in rows:
        full = supabase.table("doc_chunks").select("content").eq("id", r["id"]).single().execute().data
        text = full["content"]["text"]
        contexts.append(text)

        # rudimentary highlights
        hl, lower = [], text.lower()
        for t in terms:
            pos = lower.find(t.lower())
            if pos != -1:
                hl.append({"start": pos, "end": pos + len(t)})
            if len(hl) >= 5: break

        hits.append(SearchHit(
            chunk_id=r["id"],
            doc_id=r["doc_id"],
            page_number=r["page_number"],
            title=r["title"] or "Untitled",
            snippet=r["snippet"],
            similarity=r["similarity"],
            highlights=hl or None
        ))

    answer = rag_answer(req.query, contexts)
    return SearchResponse(answer=answer, hits=hits)
