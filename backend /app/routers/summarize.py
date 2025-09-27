from fastapi import APIRouter, HTTPException
from app.db.supabase_client import supabase
from app.services.ai import page_summary
from app.models.schemas import SummarizeResponse

router = APIRouter(prefix="", tags=["summarize"])

@router.get("/summarize-page/{chunk_id}", response_model=SummarizeResponse)
def summarize_page(chunk_id: str):
    try:
        res = supabase.table("doc_chunks") \
            .select("doc_id, page_number, content") \
            .eq("id", chunk_id).single().execute()
        row = res.data
    except Exception:
        row = None
    if not row:
        raise HTTPException(status_code=404, detail="Chunk not found")
    title = row["content"].get("title") or f"Page {row['page_number']}"
    text  = row["content"].get("text")  or ""
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text in chunk")
    summary = page_summary(title, text, target_words=140)
    return SummarizeResponse(
        doc_id=row["doc_id"],
        chunk_id=chunk_id,
        page_number=int(row["page_number"]),
        title=title,
        summary=summary,
        cached=False,
        source_pages=1
    )

