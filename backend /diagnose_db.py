#!/usr/bin/env python3
"""
Advanced Supabase diagnostics
"""
import sys
sys.path.append('.')

from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from supabase import create_client
import json

def diagnose_supabase():
    print("🔍 Advanced Supabase Diagnostics...")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_SERVICE_KEY[:20]}...")
    
    try:
        # Create client
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Client created successfully")
        
        # Try different approaches to check what exists
        tests = [
            ("app.documents", "Check if app.documents table exists"),
            ("documents", "Check if documents table exists in public schema"),
            ("public.documents", "Check explicit public.documents"),
        ]
        
        for table_name, description in tests:
            try:
                print(f"\n🧪 {description}...")
                result = supabase.table(table_name).select("*").limit(1).execute()
                print(f"✅ SUCCESS: {table_name} - Found {len(result.data)} records")
                if result.data:
                    print(f"   Sample record: {result.data[0]}")
                return True
            except Exception as e:
                print(f"❌ FAILED: {table_name} - {e}")
        
        # Check what schemas exist
        print(f"\n🔍 Checking available schemas...")
        try:
            # This is a raw SQL query to see schemas
            result = supabase.rpc("exec", {"query": "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('public', 'app');"}).execute()
            print(f"Available schemas: {result}")
        except Exception as e:
            print(f"Could not check schemas: {e}")
            
        # Try to check what tables exist in app schema
        print(f"\n🔍 Checking tables in app schema...")
        try:
            # Check if we can query information_schema
            result = supabase.rpc("exec", {"query": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'app';"}).execute()
            print(f"Tables in app schema: {result}")
        except Exception as e:
            print(f"Could not check app schema tables: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Critical failure: {e}")
        return False

def test_manual_approach():
    """Test with manual SQL execution"""
    print(f"\n🧪 Testing manual SQL approach...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Try a simple query first
        result = supabase.rpc("exec", {"query": "SELECT 1 as test"}).execute()
        print(f"✅ Basic SQL works: {result}")
        
        # Check if app schema exists
        result = supabase.rpc("exec", {"query": "SELECT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'app') as app_exists"}).execute()
        print(f"✅ App schema check: {result}")
        
    except Exception as e:
        print(f"❌ Manual SQL failed: {e}")

if __name__ == "__main__":
    success = diagnose_supabase()
    if not success:
        test_manual_approach()
        
    print(f"\n💡 Recommendations:")
    print(f"1. Check if the schema was applied in Supabase SQL Editor")
    print(f"2. Verify the 'app' schema was created")
    print(f"3. Check if RLS policies are blocking access")
    print(f"4. Try refreshing the Supabase schema cache")