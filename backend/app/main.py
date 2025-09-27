from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
import logging
from app.config import CORS_ORIGINS, MAX_FILE_SIZE, MAX_REQUEST_SIZE
from app.routers.upload import router as upload_router
from app.routers.summarize import router as summarize_router
from app.routers.search import router as search_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Intelligence API",
    description="RAG system for document upload, search, and summarization with 500MB file support",
    version="1.0.0"
)

# Middleware to handle large request bodies
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Middleware to handle request size limiting and provide better error messages"""
    
    # Check Content-Length header
    content_length = request.headers.get('content-length')
    if content_length:
        content_length = int(content_length)
        logger.info(f"📏 Request size: {content_length} bytes ({content_length / (1024*1024):.2f} MB)")
        
        if content_length > MAX_REQUEST_SIZE:
            max_mb = MAX_REQUEST_SIZE // (1024 * 1024)
            logger.warning(f"❌ Request too large: {content_length} > {MAX_REQUEST_SIZE}")
            return JSONResponse(
                status_code=413,
                content={
                    "detail": f"Request too large. Size: {content_length//(1024*1024)}MB, Maximum allowed: {max_mb}MB"
                }
            )
    
    response = await call_next(request)
    return response

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": f"Request validation failed: {str(exc)}"}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"❌ HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
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
        "max_request_size_mb": MAX_REQUEST_SIZE // (1024 * 1024),
        "max_file_size_bytes": MAX_FILE_SIZE,
        "max_request_size_bytes": MAX_REQUEST_SIZE
    }

@app.get("/debug/config")
def debug_config():
    """Debug endpoint to check server configuration"""
    return {
        "file_limits": {
            "max_file_size_bytes": MAX_FILE_SIZE,
            "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
            "max_request_size_bytes": MAX_REQUEST_SIZE,
            "max_request_size_mb": MAX_REQUEST_SIZE // (1024 * 1024),
        },
        "cors_origins": CORS_ORIGINS,
        "supported_file_types": [".pdf", ".docx", ".txt"],
        "upload_endpoint": "/upload-zip"
    }

# Register feature routers
app.include_router(upload_router)
app.include_router(summarize_router)
app.include_router(search_router)

