import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def _split_csv(value: str | None) -> List[str]:
    return [x.strip() for x in (value or "").split(",") if x.strip()]

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_SUMMARY = os.getenv("OPENAI_MODEL_SUMMARY", "gpt-4o-mini")
OPENAI_MODEL_RAG = os.getenv("OPENAI_MODEL_RAG", "gpt-4o-mini")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

CORS_ORIGINS = _split_csv(os.getenv("CORS_ORIGINS", "*"))

# File upload settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "524288000"))  # 500MB in bytes
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "524288000"))  # 500MB in bytes

