#!/usr/bin/env python3
"""
Test uploading the stories.zip file from Downloads
"""
import requests
import os
from pathlib import Path

def test_stories_upload():
    """Test uploading the stories.zip file"""
    print("📚 STORIES.ZIP UPLOAD TEST")
    print("=" * 50)
    
    # Check if stories.zip exists in Downloads
    downloads_path = Path.home() / "Downloads" / "stories.zip"
    
    if not downloads_path.exists():
        print(f"❌ stories.zip not found at {downloads_path}")
        return
    
    file_size = downloads_path.stat().st_size
    size_mb = file_size / (1024 * 1024)
    print(f"📁 Found stories.zip ({size_mb:.1f} MB)")
    
    try:
        # Test server connection
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return
        print("✅ Server is running")
        
        # Read the file
        with open(downloads_path, 'rb') as f:
            file_content = f.read()
        
        print(f"📦 Read file content ({len(file_content)} bytes)")
        
        # Prepare upload
        files = {"file": ("stories.zip", file_content, "application/zip")}
        
        print("🚀 Uploading stories.zip...")
        print("   (This may take a while for large files...)")
        
        # Upload with extended timeout
        response = requests.post(
            "http://localhost:8000/upload-zip",
            files=files,
            timeout=300  # 5 minutes
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Upload successful!")
                print(f"   Document ID: {data.get('doc_id', 'N/A')}")
                print(f"   File count: {data.get('file_count', 'N/A')}")
                print(f"   Page count: {data.get('page_count', 'N/A')}")
                
                if data.get('page_count', 0) > 0:
                    print("✅ Documents processed successfully")
                else:
                    print("⚠️ No pages processed - check file contents")
                    
            except Exception as json_error:
                print(f"❌ Failed to parse JSON response: {json_error}")
                print(f"Raw response: {response.text[:500]}...")
                
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Raw error: {response.text[:500]}...")
            
    except requests.exceptions.Timeout:
        print("❌ Upload timed out - file may be too large or server overloaded")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_debug_endpoint():
    """Test the debug configuration endpoint"""
    print("\n🔧 DEBUG CONFIGURATION TEST")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/debug/config", timeout=10)
        if response.status_code == 200:
            config_data = response.json()
            print("✅ Server configuration:")
            for key, value in config_data.items():
                if 'size' in key.lower():
                    if isinstance(value, (int, float)) and value > 1024:
                        mb_value = value / (1024 * 1024)
                        print(f"   {key}: {value} bytes ({mb_value:.1f} MB)")
                    else:
                        print(f"   {key}: {value}")
                else:
                    print(f"   {key}: {value}")
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")

if __name__ == "__main__":
    test_stories_upload()
    test_debug_endpoint()
    print("\n🏁 Test completed!")