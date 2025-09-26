#!/bin/bash

# FastAPI Backend Startup Script
# This script starts the Document Intelligence API backend server

# Set working directory
cd "$(dirname "$0")"

# Set environment variables for development/testing
# IMPORTANT: Replace these with real values before production use
export SUPABASE_URL="${SUPABASE_URL:-https://your-project.supabase.co}"
export SUPABASE_SERVICE_KEY="${SUPABASE_SERVICE_KEY:-your-service-role-key-here}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-your-openai-api-key-here}"

# Optional: Override model settings
export OPENAI_MODEL_SUMMARY="${OPENAI_MODEL_SUMMARY:-gpt-4o-mini}"
export OPENAI_MODEL_RAG="${OPENAI_MODEL_RAG:-gpt-4o-mini}"
export OPENAI_EMBED_MODEL="${OPENAI_EMBED_MODEL:-text-embedding-3-small}"

# CORS origins
export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:5173,https://your-frontend.example.com}"

# Python executable path
PYTHON_EXEC="/Users/sulanadulwan/RAG/.venv/bin/python"

echo "Starting Document Intelligence API Backend..."
echo "Server will be available at: http://127.0.0.1:8000"
echo "API Documentation: http://127.0.0.1:8000/docs"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
exec $PYTHON_EXEC -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload