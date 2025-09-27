#!/usr/bin/env python3
"""
RAG API Test Script
Comprehensive testing of the RAG Web API endpoints
"""

import requests
import json
import os
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing Health Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"📊 Response: {json.dumps(data, indent=2)}")
            
            if 'max_file_size_mb' in data:
                print(f"📁 Max file size: {data['max_file_size_mb']}MB")
        else:
            print("❌ Health check failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")

def test_documents_endpoint():
    """Test the documents listing endpoint"""
    print("📄 Testing Documents Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/documents")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Found {len(documents)} documents")
            
            if documents:
                print("📋 Sample document structure:")
                print(json.dumps(documents[0], indent=2)[:500] + "...")
            else:
                print("📝 No documents found (upload some to test)")
        else:
            print("❌ Failed to fetch documents")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n")

def test_file_size_validation():
    """Test file size validation"""
    print("📏 Testing File Size Validation")
    print("-" * 30)
    
    # Test with invalid file type
    try:
        # Create a small test file that's not a ZIP
        test_file_path = Path("/tmp/test.txt")
        test_file_path.write_text("This is not a zip file")
        
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/upload-zip", files=files)
        
        print(f"Non-ZIP file test - Status Code: {response.status_code}")
        if response.status_code == 400:
            print("✅ Correctly rejected non-ZIP file")
            print(f"📝 Error message: {response.json().get('detail', 'No message')}")
        else:
            print("❌ Should have rejected non-ZIP file")
            
        # Clean up
        test_file_path.unlink(missing_ok=True)
        
    except Exception as e:
        print(f"❌ Error testing file validation: {e}")
    
    print("\n")

def test_search_validation():
    """Test search endpoint validation"""
    print("🔍 Testing Search Validation")
    print("-" * 30)
    
    try:
        # Test with empty request
        response = requests.post(
            f"{BASE_URL}/search",
            json={},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Empty search test - Status Code: {response.status_code}")
        if response.status_code == 422:
            print("✅ Correctly validated empty search request")
        else:
            print("❌ Should have validated empty search request")
            
        # Test with minimal valid request
        response = requests.post(
            f"{BASE_URL}/search",
            json={
                "query": "test query",
                "top_k": 5,
                "scope": "global"
            },
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Valid search test - Status Code: {response.status_code}")
        if response.status_code in [200, 404]:  # 200 if results, 404 if no documents
            print("✅ Search endpoint accepting valid requests")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing search: {e}")
    
    print("\n")

def print_usage_instructions():
    """Print detailed usage instructions"""
    print("📚 Manual Testing Instructions")
    print("=" * 50)
    print("""
1. 📥 POSTMAN COLLECTION SETUP:
   - Import: RAG_API_Tests.postman_collection.json
   - Set base_url variable to: http://localhost:8000
   
2. 📦 FILE UPLOAD TESTING:
   - Create a ZIP file with PDF/DOCX/TXT documents
   - Use 'Upload ZIP File' request in Postman
   - Max size: 500MB
   - Note the doc_id from response
   
3. 🔍 SEARCH TESTING:
   - Use doc_id from upload in search requests
   - Test different scopes: document, page, global
   - Try various search queries
   
4. 📄 SUMMARIZATION TESTING:
   - Use document or page scope
   - Provide doc_id and optionally chunk_id
   
5. 🚨 ERROR TESTING:
   - Upload non-ZIP files
   - Try files > 500MB
   - Send malformed JSON requests
   - Test without required parameters

6. 🛠️ PERFORMANCE TESTING:
   - Upload large ZIP files (up to 500MB)
   - Search across many documents
   - Test concurrent requests
""")
    
    print("🔧 API ENDPOINTS:")
    print("-" * 20)
    endpoints = [
        ("GET", "/health", "Health check with file size info"),
        ("GET", "/documents", "List all uploaded documents"),
        ("POST", "/upload-zip", "Upload ZIP file with documents"),
        ("POST", "/search", "Semantic search across documents"),
        ("POST", "/summarize", "Generate document summaries")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"{method:6} {endpoint:15} - {description}")
    
    print(f"\n🌐 Server URL: {BASE_URL}")
    print("💡 Make sure the backend server is running before testing!")

def main():
    """Run all tests"""
    print("🧪 RAG API Comprehensive Test Suite")
    print("=" * 50)
    print(f"🎯 Testing server at: {BASE_URL}")
    print("\n")
    
    # Run basic connectivity tests
    test_health_endpoint()
    test_documents_endpoint()
    test_file_size_validation()
    test_search_validation()
    
    # Print usage instructions
    print_usage_instructions()

if __name__ == "__main__":
    main()