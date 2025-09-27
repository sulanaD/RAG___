#!/usr/bin/env python3
"""
Simple mock backend for testing frontend functionality
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import json
import zipfile
import io
from typing import List, Optional

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data structures
class PageIndex(BaseModel):
    chunk_id: str
    source_path: str
    page_number: int
    title: str

class UploadResponse(BaseModel):
    doc_id: str
    file_count: int
    page_count: int
    pages_index: List[PageIndex]

class ChunkResponse(BaseModel):
    doc_id: str
    chunk_id: str
    page_number: int
    title: str
    text: str

class SearchHit(BaseModel):
    chunk_id: str
    doc_id: str
    page_number: int
    title: str
    snippet: str
    similarity: float
    highlights: Optional[List[dict]] = None

class SearchResponse(BaseModel):
    answer: str
    hits: List[SearchHit]

class SummarizeResponse(BaseModel):
    page_number: int
    title: str
    summary: str

# Mock storage
mock_documents = {}
mock_chunks = {}

@app.get("/healthz")
def health_check():
    return {"ok": True}

@app.post("/upload-zip", response_model=UploadResponse)
async def upload_zip(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file")
    
    # Read the ZIP file
    content = await file.read()
    doc_id = str(uuid.uuid4())
    
    try:
        # Extract ZIP and process files
        with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            # Filter out directories and system files
            files = [f for f in file_list if not f.endswith('/') and not f.startswith('__MACOSX') and not f.split('/')[-1].startswith('._')]
            supported_files = [f for f in files if any(f.lower().endswith(ext) for ext in ['.pdf', '.docx', '.txt'])]
            
            pages_index = []
            page_number = 1
            
            # Group files by folder for better organization
            for file_path in supported_files:
                # Extract folder structure
                path_parts = file_path.split('/')
                folder_parts = path_parts[:-1] if len(path_parts) > 1 else []
                filename = path_parts[-1]
                
                # Generate mock content based on filename
                chunk_id = str(uuid.uuid4())
                
                # Create realistic titles based on file content
                if 'holmes' in filename.lower() or 'sherlock' in filename.lower():
                    title = f"The Adventures of Sherlock Holmes - {filename}"
                    mock_text = f"Sherlock Holmes sat in his armchair at 221B Baker Street, contemplating the mysterious case that had just been brought to his attention. Dr. Watson observed from across the room as Holmes examined the evidence with his characteristic attention to detail. The detective's keen observations and logical deductions would once again prove invaluable in solving this intricate mystery."
                elif 'watson' in filename.lower():
                    title = f"Dr. Watson's Medical Notes - {filename}"
                    mock_text = f"Dr. John Watson carefully documented his observations of the case. As Holmes's trusted companion and chronicler, Watson provided both medical expertise and a grounding perspective to their investigations. His detailed notes would later serve as the foundation for the stories that made their partnership famous throughout London."
                elif 'mystery' in filename.lower() or 'detective' in filename.lower():
                    title = f"Mystery Case Files - {filename}"
                    mock_text = f"The case presented a fascinating puzzle that challenged conventional investigative methods. Evidence pointed in multiple directions, requiring careful analysis and methodical deduction. Each clue revealed new layers of complexity, making this one of the most intriguing mysteries to date."
                elif 'story' in filename.lower():
                    title = f"Classic Story Collection - {filename}"
                    mock_text = f"This collection represents some of the finest examples of classic literature and storytelling. Each tale weaves together compelling characters, intricate plots, and timeless themes that continue to resonate with readers across generations."
                else:
                    # Generate title based on folder context
                    if folder_parts:
                        folder_name = folder_parts[-1]
                        title = f"{folder_name}: {filename}"
                    else:
                        title = f"Document: {filename}"
                    mock_text = f"This document contains important information and detailed analysis relevant to {filename}. The content has been carefully organized and structured to provide comprehensive coverage of the topic at hand."
                
                # Store mock chunk data
                mock_chunks[chunk_id] = {
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "page_number": page_number,
                    "title": title,
                    "text": mock_text
                }
                
                pages_index.append(PageIndex(
                    chunk_id=chunk_id,
                    source_path=file_path,
                    page_number=page_number,
                    title=title
                ))
                
                page_number += 1
            
            # Store document info
            mock_documents[doc_id] = {
                "doc_id": doc_id,
                "name": file.filename,
                "file_count": len(supported_files),
                "page_count": len(pages_index),
                "pages_index": pages_index
            }
            
            return UploadResponse(
                doc_id=doc_id,
                file_count=len(supported_files),
                page_count=len(pages_index),
                pages_index=pages_index
            )
    
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing ZIP file: {str(e)}")

@app.get("/chunk/{chunk_id}", response_model=ChunkResponse)
def get_chunk(chunk_id: str):
    if chunk_id not in mock_chunks:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    chunk_data = mock_chunks[chunk_id]
    return ChunkResponse(**chunk_data)

@app.post("/search", response_model=SearchResponse)
def search(request: dict):
    query = request.get("query", "")
    top_k = request.get("top_k", 5)
    scope = request.get("scope", "document")
    
    # Mock search results
    hits = []
    for chunk_id, chunk_data in list(mock_chunks.items())[:top_k]:
        if query.lower() in chunk_data["title"].lower() or query.lower() in chunk_data["text"].lower():
            hits.append(SearchHit(
                chunk_id=chunk_data["chunk_id"],
                doc_id=chunk_data["doc_id"],
                page_number=chunk_data["page_number"],
                title=chunk_data["title"],
                snippet=chunk_data["text"][:200] + "...",
                similarity=0.85,
                highlights=[{"start": 10, "end": 10 + len(query)}] if query in chunk_data["text"] else None
            ))
    
    answer = f"Based on the search results for '{query}', I found {len(hits)} relevant documents." if hits else "I don't have specific information about that query."
    
    return SearchResponse(answer=answer, hits=hits)

@app.post("/summarize-page/{chunk_id}", response_model=SummarizeResponse)
def summarize_page(chunk_id: str):
    if chunk_id not in mock_chunks:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    chunk_data = mock_chunks[chunk_id]
    summary = f"This page discusses {chunk_data['title'].lower()}. The main points include detailed analysis and comprehensive coverage of the topic. Key insights and important information are presented in a clear and structured manner."
    
    return SummarizeResponse(
        page_number=chunk_data["page_number"],
        title=chunk_data["title"],
        summary=summary
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)