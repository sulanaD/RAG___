#!/bin/bash

# RAG API Test Script
# This script tests the RAG API endpoints with various scenarios

BASE_URL="http://localhost:8000"
echo "🧪 RAG API Test Suite"
echo "====================="
echo "Base URL: $BASE_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_code=${4:-200}
    
    echo "Testing: $description"
    echo "  → $method $BASE_URL$endpoint"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$endpoint")
    
    if [ "$response" -eq "$expected_code" ]; then
        echo "  ✅ Success (HTTP $response)"
    else
        echo "  ❌ Failed (HTTP $response, expected $expected_code)"
    fi
    echo ""
}

# Test health endpoint
test_endpoint "GET" "/health" "Health Check"

# Test documents endpoint
test_endpoint "GET" "/documents" "List Documents"

# Test invalid upload (no file)
echo "Testing: Upload without file (should fail)"
echo "  → POST $BASE_URL/upload-zip"
response=$(curl -s -o /dev/null -w "%{http_code}" -X "POST" "$BASE_URL/upload-zip")
if [ "$response" -eq "422" ]; then
    echo "  ✅ Success (HTTP $response - validation error expected)"
else
    echo "  ❌ Failed (HTTP $response, expected 422)"
fi
echo ""

# Test search without parameters (should fail)
echo "Testing: Search without parameters (should fail)"
echo "  → POST $BASE_URL/search"
response=$(curl -s -o /dev/null -w "%{http_code}" -X "POST" "$BASE_URL/search" \
    -H "Content-Type: application/json" \
    -d '{}')
if [ "$response" -eq "422" ]; then
    echo "  ✅ Success (HTTP $response - validation error expected)"
else
    echo "  ❌ Failed (HTTP $response, expected 422)"
fi
echo ""

echo "📝 Manual Testing Instructions:"
echo "================================"
echo ""
echo "1. Import the Postman collection:"
echo "   File: RAG_API_Tests.postman_collection.json"
echo ""
echo "2. Test file upload with a ZIP file:"
echo "   - Create a test ZIP with PDF/DOCX/TXT files"
echo "   - Use the 'Upload ZIP File' request in Postman"
echo "   - Maximum file size is now 500MB"
echo ""
echo "3. Test search functionality:"
echo "   - Use the doc_id from upload response"
echo "   - Try different search scopes: document, page, global"
echo ""
echo "4. Test summarization:"
echo "   - Use document or page scope"
echo "   - Verify AI-generated summaries"
echo ""
echo "5. Test error handling:"
echo "   - Try uploading non-ZIP files"
echo "   - Test with files larger than 500MB"
echo "   - Send malformed requests"
echo ""
echo "🚀 Server Configuration:"
echo "========================"
echo "Max file size: 500MB (524,288,000 bytes)"
echo "Allowed file types in ZIP: PDF, DOCX, TXT"
echo "CORS enabled for development"
echo ""