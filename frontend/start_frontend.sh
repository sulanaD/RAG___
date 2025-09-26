#!/bin/bash

# Frontend Startup Script
# This script installs dependencies and starts the React development server

# Set working directory
cd "$(dirname "$0")"

echo "🎯 RAG Document Intelligence Frontend"
echo "=================================="

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
    echo ""
fi

echo "🚀 Starting development server..."
echo "Frontend will be available at: http://localhost:5173"
echo "Make sure the backend is running at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
exec npm run dev