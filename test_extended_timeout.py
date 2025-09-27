#!/usr/bin/env python3
"""
Test the new extended frontend timeout settings
"""
import requests
import time
from pathlib import Path

def test_extended_timeout():
    """Test upload with extended 10-minute timeout"""
    print("⏰ EXTENDED TIMEOUT TEST")
    print("=" * 40)
    
    stories_path = Path("/Users/sulanadulwan/RAG/backend/stories.zip")
    
    if not stories_path.exists():
        print(f"❌ stories.zip not found at {stories_path}")
        return
        
    file_size = stories_path.stat().st_size
    print(f"📁 File size: {file_size} bytes ({file_size/(1024*1024):.1f} MB)")
    
    # Test with the new extended timeout (10 minutes = 600 seconds)
    try:
        print("🔄 Testing upload with 10-minute timeout (new frontend setting)...")
        start_time = time.time()
        
        with open(stories_path, 'rb') as f:
            files = {"file": ("stories.zip", f, "application/zip")}
            
            # Use the same timeout as the new frontend setting (600 seconds)
            response = requests.post(
                "http://localhost:8000/upload-zip",
                files=files,
                timeout=600,  # 10 minutes - same as frontend
                headers={
                    'User-Agent': 'Frontend-Extended-Timeout-Test'
                }
            )
        
        duration = time.time() - start_time
        print(f"⏱️ Request completed in {duration:.1f} seconds")
        
        # Calculate timeout safety margin
        timeout_margin = 600 - duration
        print(f"🔒 Timeout safety margin: {timeout_margin:.1f} seconds ({timeout_margin/60:.1f} minutes)")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful with extended timeout!")
            print(f"   Document ID: {data.get('doc_id', 'N/A')}")
            print(f"   Files processed: {data.get('file_count', 'N/A')}")
            print(f"   Pages: {data.get('page_count', 'N/A')}")
            
            # Performance analysis
            if duration < 60:  # Under 1 minute
                print("🚀 Fast processing - frontend will respond quickly")
            elif duration < 180:  # Under 3 minutes
                print("⚡ Moderate processing time - frontend will handle well")
            elif duration < 600:  # Under 10 minutes
                print("⏳ Long processing time - new extended timeout handles this")
            else:
                print("⚠️ Very long processing - may need further timeout extension")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⏰ Upload timed out even at 10 minutes - may need backend optimization")
    except Exception as e:
        print(f"❌ Upload error: {e}")

if __name__ == "__main__":
    print("📊 Frontend timeout settings:")
    print("   • Global timeout: 5 minutes (300 seconds)")
    print("   • Upload timeout: 10 minutes (600 seconds)")
    print("   • Previous timeout: 3 minutes (180 seconds)")
    print()
    
    test_extended_timeout()
    
    print("\n📱 Frontend: http://localhost:5173")
    print("🖥️  Backend: http://localhost:8000")
    print("\n✅ Extended timeout should resolve frontend error issues!")