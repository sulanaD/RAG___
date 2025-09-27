#!/usr/bin/env python3
"""
Test frontend-backend integration with timeout fixes
"""
import requests
import time
from pathlib import Path

def test_frontend_backend_integration():
    """Test upload with frontend timeout settings"""
    print("🌐 FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 50)
    
    # Test the exact same conditions the frontend will experience
    stories_path = Path("/Users/sulanadulwan/RAG/backend/stories.zip")
    
    if not stories_path.exists():
        print(f"❌ stories.zip not found at {stories_path}")
        return
        
    file_size = stories_path.stat().st_size
    print(f"📁 File size: {file_size} bytes ({file_size/(1024*1024):.1f} MB)")
    
    # Test with frontend timeout settings (3 minutes = 180 seconds)
    try:
        print("🔄 Testing upload with 3-minute timeout (frontend setting)...")
        start_time = time.time()
        
        with open(stories_path, 'rb') as f:
            files = {"file": ("stories.zip", f, "application/zip")}
            
            # Use the same timeout as frontend (180 seconds)
            response = requests.post(
                "http://localhost:8000/upload-zip",
                files=files,
                timeout=180,
                headers={
                    'User-Agent': 'Frontend-Integration-Test'
                }
            )
        
        duration = time.time() - start_time
        print(f"⏱️ Request completed in {duration:.1f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   Document ID: {data.get('doc_id', 'N/A')}")
            print(f"   Files processed: {data.get('file_count', 'N/A')}")
            print(f"   Pages: {data.get('page_count', 'N/A')}")
            
            # Verify this matches frontend expectations
            required_fields = ['doc_id', 'file_count', 'page_count', 'pages_index']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️ Warning: Missing expected fields: {missing_fields}")
            else:
                print("✅ Response format matches frontend expectations")
                
            if duration < 180:  # Within frontend timeout
                print("✅ Upload completes within frontend timeout limit")
            else:
                print("⚠️ Upload takes longer than frontend timeout")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {response.text[:200]}...")
                
    except requests.exceptions.Timeout:
        print("⏰ Upload timed out at 180 seconds - frontend would show timeout message")
    except Exception as e:
        print(f"❌ Upload error: {e}")

def test_health_endpoint():
    """Test frontend health check"""
    print("\n🏥 HEALTH CHECK TEST")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print("   Backend is ready for frontend connections")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    test_health_endpoint()
    test_frontend_backend_integration()
    print("\n🏁 Frontend-backend integration test completed!")
    print("\n📱 Frontend should now work properly at: http://localhost:5174")
    print("🖥️  Backend is running at: http://localhost:8000")