#!/usr/bin/env python3
"""
Simple test for stories.zip upload with detailed debugging
"""
import requests
import time
from pathlib import Path

def test_stories_simple():
    """Simple test with timeout and progress tracking"""
    print("📚 SIMPLE STORIES.ZIP TEST")
    print("=" * 40)
    
    stories_path = Path.home() / "Downloads" / "stories.zip"
    
    if not stories_path.exists():
        print(f"❌ stories.zip not found at {stories_path}")
        return
        
    file_size = stories_path.stat().st_size
    print(f"📁 File size: {file_size} bytes ({file_size/(1024*1024):.1f} MB)")
    
    # Quick health check
    try:
        print("🔍 Testing server health...")
        response = requests.get("http://localhost:8000/health", timeout=3)
        print(f"✅ Server health: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return
    
    # Test upload with short timeout first
    try:
        print("🚀 Starting upload (30 second timeout)...")
        start_time = time.time()
        
        with open(stories_path, 'rb') as f:
            files = {"file": ("stories.zip", f, "application/zip")}
            
            response = requests.post(
                "http://localhost:8000/upload-zip",
                files=files,
                timeout=30,
                stream=True
            )
        
        duration = time.time() - start_time
        print(f"⏱️ Request completed in {duration:.1f} seconds")
        print(f"📊 Status code: {response.status_code}")
        print(f"📊 Response size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success! Document ID: {data.get('doc_id')}")
                print(f"   Files processed: {data.get('file_count', 0)}")
                print(f"   Pages: {data.get('page_count', 0)}")
            except Exception as json_err:
                print(f"❌ JSON parse error: {json_err}")
                print(f"Raw response (first 200 chars): {response.text[:200]}...")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {response.text[:200]}...")
                
    except requests.exceptions.Timeout:
        print("⏰ Upload timed out after 30 seconds")
        print("   This suggests the server is hanging during processing")
    except Exception as e:
        print(f"❌ Upload error: {e}")

if __name__ == "__main__":
    test_stories_simple()