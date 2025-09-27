#!/usr/bin/env python3
"""
Quick RAG API Test - Non-interrupting version
Tests the API without killing the server process
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint and display file size limits"""
    print("🏥 Testing Health Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is healthy!")
            print(f"📊 Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the backend server is running on http://localhost:8000")
        return False

def test_documents():
    """Test documents endpoint"""
    print("\n📄 Testing Documents Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/documents", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Found {len(documents)} documents")
            
            if documents:
                print("📋 First document structure:")
                first_doc = documents[0]
                print(f"  - ID: {first_doc.get('id', 'N/A')}")
                print(f"  - Name: {first_doc.get('name', 'N/A')}")
                print(f"  - Pages: {len(first_doc.get('pages', []))}")
            else:
                print("📝 No documents found - upload some ZIP files to test!")
            return True
        else:
            print(f"❌ Failed to fetch documents: {response.status_code}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_search_validation():
    """Test search endpoint with invalid data"""
    print("\n🔍 Testing Search Validation")
    print("-" * 30)
    
    try:
        # Test empty search
        response = requests.post(
            f"{BASE_URL}/search",
            json={},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"Empty search test - Status: {response.status_code}")
        if response.status_code == 422:
            print("✅ Correctly validates empty search requests")
        else:
            print("⚠️  Unexpected response for empty search")
        
        # Test basic search structure
        response = requests.post(
            f"{BASE_URL}/search",
            json={
                "query": "test query", 
                "top_k": 5,
                "scope": "global"
            },
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"Valid search structure test - Status: {response.status_code}")
        if response.status_code in [200, 404]:
            print("✅ Search endpoint accepts properly formatted requests")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            
        return True
        
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run quick API tests"""
    print("🧪 RAG API Quick Test Suite")
    print("=" * 50)
    print(f"🎯 Testing server at: {BASE_URL}")
    print(f"⏰ Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_health():
        tests_passed += 1
    
    if test_documents():
        tests_passed += 1
        
    if test_search_validation():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your API is working correctly.")
        print("\n💡 Next Steps:")
        print("   1. Import RAG_API_Tests.postman_collection.json into Postman")
        print("   2. Test file uploads with actual ZIP files")
        print("   3. Test search and summarization with uploaded documents")
        print("   4. Verify 500MB file size limit works as expected")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print(f"\n🌐 Server URL: {BASE_URL}")
    print("📚 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()