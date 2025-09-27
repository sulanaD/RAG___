#!/usr/bin/env python3
"""
Final comprehensive test of the upload system
"""
import requests
import zipfile
import io
from pathlib import Path

def test_comprehensive_upload():
    """Test various upload scenarios"""
    print("🧪 COMPREHENSIVE UPLOAD TEST")
    print("=" * 40)
    
    # Test 1: Empty ZIP
    print("\n📦 Test 1: Empty ZIP")
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            pass  # Empty ZIP
        buffer.seek(0)
        
        files = {"file": ("empty.zip", buffer.getvalue(), "application/zip")}
        response = requests.post("http://localhost:8000/upload-zip", files=files, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Expected error: {response.json().get('detail', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: ZIP with only images (should filter out)
    print("\n🖼️  Test 2: ZIP with only images")
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            zf.writestr("image1.jpg", b"fake jpg content")
            zf.writestr("image2.png", b"fake png content")
            zf.writestr("subfolder/image3.gif", b"fake gif content")
        buffer.seek(0)
        
        files = {"file": ("images_only.zip", buffer.getvalue(), "application/zip")}
        response = requests.post("http://localhost:8000/upload-zip", files=files, timeout=15)
        
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Expected error: {response.json().get('detail', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Valid ZIP with documents
    print("\n📄 Test 3: Valid ZIP with documents")
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zf:
            zf.writestr("doc1.txt", "This is document 1 with some content.")
            zf.writestr("folder/doc2.txt", "This is document 2 in a folder.")
            zf.writestr("ignore_me.jpg", b"fake image")  # Should be filtered
        buffer.seek(0)
        
        files = {"file": ("valid_docs.zip", buffer.getvalue(), "application/zip")}
        response = requests.post("http://localhost:8000/upload-zip", files=files, timeout=20)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('file_count')} files, {data.get('page_count')} pages")
        else:
            print(f"   ❌ Error: {response.json().get('detail', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_comprehensive_upload()
    print("\n🏁 Comprehensive test completed!")