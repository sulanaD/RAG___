#!/usr/bin/env python3
"""
Quick test for nested folder structures with mixed file types
"""
import requests
import zipfile
import io
import tempfile
import os
from pathlib import Path

def create_nested_test_zip():
    """Create a ZIP with nested folders containing mixed file types"""
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add some valid document files
        zf.writestr("documents/report.txt", "This is a text report.\n" * 100)
        zf.writestr("documents/analysis.pdf", b"fake PDF content for testing")
        
        # Add nested folder with images (should be filtered out)
        zf.writestr("documents/images/photo1.jpg", b"fake JPEG content")
        zf.writestr("documents/images/photo2.png", b"fake PNG content")
        zf.writestr("documents/images/icon.gif", b"fake GIF content")
        
        # Add more nested levels with mixed content
        zf.writestr("documents/subfolder/data.txt", "Valid text data\n" * 50)
        zf.writestr("documents/subfolder/media/video.mp4", b"fake video content")
        zf.writestr("documents/subfolder/media/audio.wav", b"fake audio content")
        
        # Add metadata files that should be skipped
        zf.writestr("__MACOSX/._hidden", b"macOS metadata")
        zf.writestr("documents/.DS_Store", b"directory store file")
        zf.writestr("documents/._metadata", b"metadata file")
        
    buffer.seek(0)
    return buffer.getvalue()

def test_nested_upload():
    """Test uploading ZIP with nested folders and mixed file types"""
    print("🗂️  NESTED FOLDER TEST")
    print("=" * 50)
    
    try:
        # Test server connection
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return
        print("✅ Server is running")
        
        # Create test ZIP
        zip_content = create_nested_test_zip()
        print(f"📦 Created test ZIP ({len(zip_content)} bytes)")
        
        # Upload the ZIP
        files = {"file": ("nested_test.zip", zip_content, "application/zip")}
        
        print("🚀 Uploading nested folder ZIP...")
        response = requests.post(
            "http://localhost:8000/upload-zip",
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   Document ID: {data.get('doc_id')}")
            print(f"   File count: {data.get('file_count', 0)}")
            print(f"   Page count: {data.get('page_count', 0)}")
            
            if data.get('page_count', 0) > 0:
                print("✅ Successfully processed documents from nested structure")
            else:
                print("⚠️ No pages processed - check if filtering is too aggressive")
                
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Test error: {e}")

def test_large_file_quick():
    """Quick test for large file handling (smaller test file)"""
    print("\n📏 LARGE FILE TEST (Quick)")
    print("=" * 50)
    
    try:
        # Create a moderately large ZIP (5MB) to test quickly
        buffer = io.BytesIO()
        large_content = "This is test content for large file testing.\n" * 50000  # ~2.5MB text
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("large_document1.txt", large_content)
            zf.writestr("large_document2.txt", large_content)
        
        buffer.seek(0)
        zip_content = buffer.getvalue()
        size_mb = len(zip_content) / (1024 * 1024)
        print(f"📦 Created test ZIP ({size_mb:.1f} MB)")
        
        # Upload the ZIP
        files = {"file": ("large_test.zip", zip_content, "application/zip")}
        
        print("🚀 Uploading large file...")
        response = requests.post(
            "http://localhost:8000/upload-zip",
            files=files,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Large file upload successful!")
            print(f"   Page count: {data.get('page_count', 0)}")
        else:
            print(f"❌ Large file upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Large file test error: {e}")

if __name__ == "__main__":
    test_nested_upload()
    test_large_file_quick()
    print("\n🏁 Tests completed!")