from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS, MAX_FILE_SIZE, MAX_REQUEST_SIZE
from app.routers.upload import router as upload_router
from app.routers.summarize import router as summarize_router
from app.routers.search import router as search_router

app = FastAPI(
    title="Document Intelligence API",
    description="RAG system for document upload, search, and summarization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
@app.get("/health")
def health():
    return {
        "ok": True,
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
        "max_request_size_mb": MAX_REQUEST_SIZE // (1024 * 1024)
    }

# Register feature routers
app.include_router(upload_router)
app.include_router(summarize_router)
app.include_router(search_router)

