#!/usr/bin/env python3
"""
Test uploading the stories.zip file from backend directory
"""
import requests
import time
from pathlib import Path

def test_backend_stories_upload():
    """Test uploading stories.zip from backend directory"""
    print("📚 BACKEND STORIES.ZIP UPLOAD TEST")
    print("=" * 50)
    
    stories_path = Path("/Users/sulanadulwan/RAG/backend/stories.zip")
    
    if not stories_path.exists():
        print(f"❌ stories.zip not found at {stories_path}")
        return
        
    file_size = stories_path.stat().st_size
    print(f"📁 File size: {file_size} bytes ({file_size/(1024*1024):.1f} MB)")
    
    # Quick health check
    try:
        print("🔍 Testing server health...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Server health: {response.status_code}")
        
        # Print server config
        config = response.json()
        print(f"📊 Max file size: {config.get('max_file_size_mb', 'unknown')} MB")
        
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return
    
    # Test upload with extended timeout
    try:
        print("🚀 Starting upload (60 second timeout)...")
        start_time = time.time()
        
        with open(stories_path, 'rb') as f:
            files = {"file": ("stories.zip", f, "application/zip")}
            
            response = requests.post(
                "http://localhost:8000/upload-zip",
                files=files,
                timeout=60
            )
        
        duration = time.time() - start_time
        print(f"⏱️ Request completed in {duration:.1f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Upload successful!")
                print(f"   Document ID: {data.get('doc_id', 'N/A')}")
                print(f"   Files processed: {data.get('file_count', 'N/A')}")
                print(f"   Pages: {data.get('page_count', 'N/A')}")
                
                if data.get('page_count', 0) > 0:
                    print(f"🎉 SUCCESS! {data.get('page_count')} pages processed successfully")
                else:
                    print("⚠️ Warning: No pages processed")
                    
            except Exception as json_err:
                print(f"❌ JSON parse error: {json_err}")
                print(f"Raw response (first 500 chars): {response.text[:500]}...")
                
        elif response.status_code == 413:
            print("❌ File too large error")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {response.text[:300]}...")
                
        elif response.status_code == 500:
            print("❌ Internal server error")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {response.text[:300]}...")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {response.text[:300]}...")
                
    except requests.exceptions.Timeout:
        print("⏰ Upload timed out after 60 seconds")
        print("   Check server logs for processing status")
    except Exception as e:
        print(f"❌ Upload error: {e}")

if __name__ == "__main__":
    test_backend_stories_upload()
    print("\n🏁 Test completed!")