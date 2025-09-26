from pathlib import Path
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.db.supabase_client import insert_document, insert_chunks, update_page_count, supabase, CHUNKS_TABLE
from app.services.utils_zip import extract_zip_recursive
from app.services.parsing import iter_pages_for_file
from app.services.ai import embed, gen_title
from app.models.schemas import UploadZipResponse

router = APIRouter(prefix="", tags=["upload"])
ALLOWED = {".pdf", ".docx", ".txt"}

@router.post("/upload-zip", response_model=UploadZipResponse)
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip")

    with tempfile.TemporaryDirectory() as td:
        tempd = Path(td)
        data = await file.read()
        extracted = extract_zip_recursive(data, tempd / "unzipped")
        allowed = [p for p in extracted if p.suffix.lower() in ALLOWED]
        if not allowed:
            raise HTTPException(status_code=400, detail="No supported files found in zip")

        doc_id = insert_document(name=file.filename, file_count=len(allowed), meta={})

        staged_rows = []
        page_count = 0
        texts_for_embedding, slots = [], []

        for path in allowed:
            for page_num, page_text in iter_pages_for_file(path):
                title = gen_title(page_text)
                staged_rows.append({
                    "doc_id": doc_id,
                    "source_path": str(path.relative_to(tempd)),
                    "page_number": int(page_num),
                    "content": {"title": title, "text": page_text, "page_meta": {}},
                    "embedding": None
                })
                texts_for_embedding.append(page_text)
                slots.append(len(staged_rows)-1)
                page_count += 1

        if page_count == 0:
            raise HTTPException(status_code=400, detail="No extractable text found")

        vectors = embed(texts_for_embedding)
        for v, idx in zip(vectors, slots):
            staged_rows[idx]["embedding"] = v

        insert_chunks(staged_rows)
        update_page_count(doc_id, page_count)

        # Retrieve the processed chunks from Supabase
        q = supabase.table(CHUNKS_TABLE) \
            .select("id, source_path, page_number, content->>title") \
            .eq("doc_id", doc_id).order("page_number", desc=False).execute()
        
        pages_index = [{
            "chunk_id": r["id"],
            "source_path": r["source_path"],
            "page_number": int(r["page_number"]),
            "title": r.get("content->>title") or "Untitled"
        } for r in (q.data or [])]

        return UploadZipResponse(
            doc_id=doc_id,
            file_count=len(allowed),
            page_count=page_count,
            pages_index=pages_index
        )

