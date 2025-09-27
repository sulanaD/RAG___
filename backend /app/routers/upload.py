from pathlib import Path
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.db.supabase_client import insert_document, insert_chunks, update_page_count, supabase, CHUNKS_TABLE
from app.services.utils_zip import extract_zip_recursive
from app.services.parsing import iter_pages_for_file
from app.services.ai import embed, gen_title
from app.models.schemas import UploadZipResponse
from app.config import MAX_FILE_SIZE

router = APIRouter(prefix="", tags=["upload"])
ALLOWED = {".pdf", ".docx", ".txt"}

@router.post("/upload-zip", response_model=UploadZipResponse)
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip")
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size allowed is {max_mb}MB"
        )

    with tempfile.TemporaryDirectory() as td:
        tempd = Path(td)
        data = await file.read()
        extracted = extract_zip_recursive(data, tempd / "unzipped")
        # Filter out macOS metadata files and folders
        filtered = []
        for p in extracted:
            path_str = str(p)
            # Skip __MACOSX folders and ._* metadata files
            if '__MACOSX' in path_str or p.name.startswith('._'):
                continue
            if p.suffix.lower() in ALLOWED:
                filtered.append(p)
        allowed = filtered
        if not allowed:
            raise HTTPException(status_code=400, detail="No supported files found in zip")

        doc_id = insert_document(name=file.filename, file_count=len(allowed), meta={})

        staged_rows = []
        page_count = 0
        texts_for_embedding, slots = [], []

        for path in allowed:
            # Extract folder structure for better titles
            relative_path = path.relative_to(tempd)
            folder_parts = relative_path.parent.parts[1:]  # Skip 'unzipped'
            folder_name = folder_parts[-1] if folder_parts else None
            
            for page_num, page_text in iter_pages_for_file(path):
                # Generate title with folder context
                if folder_name and folder_name != 'unzipped':
                    title = gen_title(page_text, folder_context=folder_name)
                else:
                    title = gen_title(page_text)
                
                # Include folder info in page metadata
                page_meta = {
                    "folder_path": "/".join(folder_parts) if folder_parts else "",
                    "filename": path.name,
                    "file_type": path.suffix.lower()
                }
                
                staged_rows.append({
                    "doc_id": doc_id,
                    "source_path": str(relative_path),
                    "page_number": int(page_num),
                    "content": {"title": title, "text": page_text, "page_meta": page_meta},
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
            .select("id, source_path, page_number, content") \
            .eq("doc_id", doc_id).order("page_number", desc=False).execute()
        
        pages_index = [{
            "chunk_id": r["id"],
            "source_path": r["source_path"],
            "page_number": int(r["page_number"]),
            "title": (r.get("content") or {}).get("title") or "Untitled"
        } for r in (q.data or [])]

        return UploadZipResponse(
            doc_id=doc_id,
            file_count=len(allowed),
            page_count=page_count,
            pages_index=pages_index
        )

