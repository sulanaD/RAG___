from pathlib import Path
import tempfile
import logging
import traceback
import sys
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.db.supabase_client import insert_document, insert_chunks, update_page_count, supabase, CHUNKS_TABLE
from app.services.utils_zip import extract_zip_recursive
from app.services.parsing import iter_pages_for_file
from app.services.ai import embed, gen_title
from app.models.schemas import UploadZipResponse
from app.config import MAX_FILE_SIZE

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="", tags=["upload"])
ALLOWED = {".pdf", ".docx", ".txt"}

@router.post("/upload-zip", response_model=UploadZipResponse)
async def upload_zip(file: UploadFile = File(...)):
    logger.info(f"🚀 Starting upload process for file: {file.filename}")
    
    try:
        # Basic file validation
        if not file.filename.lower().endswith(".zip"):
            logger.warning(f"❌ Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Please upload a .zip")
        
        logger.info(f"📁 File name: {file.filename}")
        logger.info(f"📏 Reported file size: {file.size} bytes ({(file.size or 0) / (1024*1024):.2f} MB)")
        logger.info(f"📊 Max allowed size: {MAX_FILE_SIZE} bytes ({MAX_FILE_SIZE / (1024*1024):.2f} MB)")
        
        # Check file size before reading
        if file.size and file.size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE // (1024 * 1024)
            logger.warning(f"❌ File too large: {file.size} bytes > {MAX_FILE_SIZE} bytes")
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size allowed is {max_mb}MB"
            )
        
        logger.info("📖 Starting file read...")
        
        # Read file data with error handling
        try:
            data = await file.read()
            actual_size = len(data)
            logger.info(f"✅ File read successfully: {actual_size} bytes ({actual_size / (1024*1024):.2f} MB)")
            
            # Additional size check after reading
            if actual_size > MAX_FILE_SIZE:
                max_mb = MAX_FILE_SIZE // (1024 * 1024)
                logger.warning(f"❌ Actual file size exceeds limit: {actual_size} > {MAX_FILE_SIZE}")
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Actual size: {actual_size//(1024*1024)}MB, Maximum allowed: {max_mb}MB"
                )
                
        except Exception as read_error:
            logger.error(f"❌ Error reading file: {str(read_error)}")
            logger.error(f"📋 Error type: {type(read_error).__name__}")
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(read_error)}")

        with tempfile.TemporaryDirectory() as td:
            tempd = Path(td)
            logger.info(f"📁 Temporary directory created: {tempd}")
            
            try:
                logger.info("🔄 Starting ZIP extraction...")
                extracted = extract_zip_recursive(data, tempd / "unzipped")
                logger.info(f"✅ ZIP extracted successfully: {len(extracted)} files found")
                
            except Exception as extract_error:
                logger.error(f"❌ Error extracting ZIP: {str(extract_error)}")
                logger.error(f"📋 Error type: {type(extract_error).__name__}")
                logger.error(f"📋 Traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error extracting ZIP file: {str(extract_error)}")

            # Filter out macOS metadata files and folders
            logger.info("🔍 Filtering extracted files...")
            filtered = []
            for p in extracted:
                path_str = str(p)
                # Skip __MACOSX folders and ._* metadata files
                if '__MACOSX' in path_str or p.name.startswith('._'):
                    logger.debug(f"⏭️ Skipping metadata file: {p}")
                    continue
                if p.suffix.lower() in ALLOWED:
                    filtered.append(p)
                    logger.debug(f"✅ Including file: {p}")
                else:
                    logger.debug(f"⏭️ Skipping unsupported file: {p}")
            
            allowed = filtered
            logger.info(f"📋 Files after filtering: {len(allowed)} supported files")
            
            if not allowed:
                logger.warning("❌ No supported files found after filtering")
                raise HTTPException(status_code=400, detail="No supported files found in zip")

            logger.info(f"💾 Inserting document record for {len(allowed)} files...")
            doc_id = insert_document(name=file.filename, file_count=len(allowed), meta={})
            logger.info(f"✅ Document created with ID: {doc_id}")

            staged_rows = []
            page_count = 0
            texts_for_embedding, slots = [], []

            logger.info("📄 Processing document pages...")
            for path in allowed:
                # Extract folder structure for better titles
                relative_path = path.relative_to(tempd)
                folder_parts = relative_path.parent.parts[1:]  # Skip 'unzipped'
                folder_name = folder_parts[-1] if folder_parts else None
                
                logger.debug(f"📖 Processing file: {path}")
                
                try:
                    # Generate a single title for the entire file based on filename and folder context
                    base_filename = path.stem  # filename without extension
                    if folder_name and folder_name != 'unzipped':
                        file_title = f"{folder_name}: {base_filename}"
                    else:
                        file_title = base_filename
                    
                    for page_num, page_text in iter_pages_for_file(path):
                        # Use filename-based title with page number for efficiency
                        if page_num > 1:
                            title = f"{file_title} (Page {page_num})"
                        else:
                            title = file_title
                        
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
                        
                except Exception as parse_error:
                    logger.error(f"❌ Error parsing file {path}: {str(parse_error)}")
                    logger.error(f"📋 Parse error traceback: {traceback.format_exc()}")
                    # Continue with other files instead of failing completely
                    continue

            if page_count == 0:
                logger.warning("❌ No extractable text found in any files")
                raise HTTPException(status_code=400, detail="No extractable text found")

            logger.info(f"🧠 Generating embeddings for {len(texts_for_embedding)} text chunks using optimized batching...")
            logger.info(f"💰 API Optimization: Smart batching prevents token limit errors while minimizing API calls")
            try:
                vectors = embed(texts_for_embedding)
                logger.info(f"✅ Embeddings generated successfully")
                
                for v, idx in zip(vectors, slots):
                    staged_rows[idx]["embedding"] = v
                    
            except Exception as embed_error:
                logger.error(f"❌ Error generating embeddings: {str(embed_error)}")
                logger.error(f"📋 Embedding error traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(embed_error)}")

            logger.info(f"💾 Inserting {len(staged_rows)} chunks into database...")
            try:
                insert_chunks(staged_rows)
                update_page_count(doc_id, page_count)
                logger.info("✅ Database operations completed successfully")
                
            except Exception as db_error:
                logger.error(f"❌ Database error: {str(db_error)}")
                logger.error(f"📋 Database error traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")

            # Retrieve the processed chunks from Supabase
            logger.info("📋 Retrieving processed chunks for response...")
            try:
                q = supabase.table(CHUNKS_TABLE) \
                    .select("id, source_path, page_number, content") \
                    .eq("doc_id", doc_id).order("page_number", desc=False).execute()
                
                pages_index = [{
                    "chunk_id": r["id"],
                    "source_path": r["source_path"],
                    "page_number": int(r["page_number"]),
                    "title": (r.get("content") or {}).get("title") or "Untitled"
                } for r in (q.data or [])]

                logger.info(f"🎉 Upload completed successfully! Document ID: {doc_id}, Pages: {page_count}")

                return UploadZipResponse(
                    doc_id=doc_id,
                    file_count=len(allowed),
                    page_count=page_count,
                    pages_index=pages_index
                )
                
            except Exception as query_error:
                logger.error(f"❌ Error retrieving processed data: {str(query_error)}")
                logger.error(f"📋 Query error traceback: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Error retrieving processed data: {str(query_error)}")

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during upload: {str(e)}")
        logger.error(f"📋 Error type: {type(e).__name__}")
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        logger.error(f"🔧 Python version: {sys.version}")
        
        # Provide helpful error message based on error type
        if "MemoryError" in str(type(e)):
            raise HTTPException(
                status_code=507,
                detail="Server ran out of memory processing the file. Try uploading a smaller file or contact support."
            )
        elif "TimeoutError" in str(type(e)) or "timeout" in str(e).lower():
            raise HTTPException(
                status_code=504,
                detail="Upload timed out. The file may be too large or the server is busy. Please try again."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error during upload: {str(e)}"
            )

