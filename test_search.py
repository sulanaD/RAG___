#!/usr/bin/env python3
"""
Test search functionality on uploaded stories
"""
import requests
import json

def test_search_uploaded_stories():
    """Test searching the uploaded stories content"""
    print("🔍 SEARCH TEST ON UPLOADED STORIES")
    print("=" * 40)
    
    # Test search endpoint
    try:
        search_data = {
            "query": "story",
            "top_k": 3
        }
        
        print("🔍 Searching for 'story' in uploaded documents...")
        response = requests.post(
            "http://localhost:8000/search",
            json=search_data,
            timeout=30
        )
        
        print(f"📊 Search status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful!")
            print(f"   Answer: {data.get('answer', 'N/A')[:100]}...")
            print(f"   Found {len(data.get('hits', []))} results")
            
            for i, hit in enumerate(data.get('hits', [])[:3]):
                print(f"   Result {i+1}: {hit.get('title', 'N/A')} (similarity: {hit.get('similarity', 0):.3f})")
                
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Search error: {e}")

if __name__ == "__main__":
    test_search_uploaded_stories()
    print("\n🏁 Search test completed!")