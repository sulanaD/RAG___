#!/usr/bin/env python3
"""
Test script to verify Supabase connection and schema
"""
import sys
sys.path.append('.')

from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from supabase import create_client
import json

def test_supabase_connection():
    print("🧪 Testing Supabase Connection...")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_SERVICE_KEY[:20]}...")
    
    try:
        # Create client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Client created successfully")
        
        # Test basic connection
        result = supabase.table("app.documents").select("*").limit(5).execute()
        print(f"✅ Connection successful! Found {len(result.data)} documents")
        
        # Test if we can insert a test document
        test_doc = {
            "name": "connection-test.txt",
            "file_count": 1,
            "page_count": 0,
            "meta": {"test": True}
        }
        
        insert_result = supabase.table("app.documents").insert(test_doc).execute()
        if insert_result.data:
            doc_id = insert_result.data[0]["id"]
            print(f"✅ Insert test successful! Doc ID: {doc_id}")
            
            # Clean up test document
            supabase.table("app.documents").delete().eq("id", doc_id).execute()
            print("✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    if success:
        print("🎉 Supabase is ready for the RAG system!")
    else:
        print("🔧 Please check your Supabase configuration and schema")
        print("\n📝 Steps to fix:")
        print("1. Go to your Supabase project SQL Editor")
        print("2. Run the schema.sql file")
        print("3. Verify the tables are created")