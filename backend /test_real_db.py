#!/usr/bin/env python3
"""
Direct database connection test using psycopg2
"""
import os
import sys
sys.path.append('.')

# Test with different connection methods
def test_direct_connection():
    try:
        from supabase import create_client
        from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY
        
        print("🔍 Testing Supabase Connection...")
        print(f"URL: {SUPABASE_URL}")
        print(f"Service Key: {SUPABASE_SERVICE_KEY[:30]}...")
        
        # Create client with explicit settings
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        print("✅ Client created")
        
        # Test 1: Check if we can access any table
        print("\n🧪 Test 1: Basic connectivity...")
        try:
            # Try to query a system table that should always exist
            result = supabase.rpc("version").execute()
            print(f"✅ Basic connection works: {result}")
        except Exception as e:
            print(f"❌ Basic connection failed: {e}")
            return False
            
        # Test 2: Check app schema specifically
        print("\n🧪 Test 2: Check app schema...")
        try:
            result = supabase.table("app.documents").select("count", count="exact").execute()
            print(f"✅ app.documents table accessible! Count: {result.count}")
            return True
        except Exception as e:
            print(f"❌ app.documents failed: {e}")
            
        # Test 3: Try with different schema reference
        print("\n🧪 Test 3: Alternative schema access...")
        try:
            # Sometimes you need to specify the schema differently
            from supabase import create_client
            supabase_alt = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            result = supabase_alt.table("documents").select("count", count="exact").execute()
            print(f"✅ Alternative schema access works! Count: {result.count}")
            return True
        except Exception as e:
            print(f"❌ Alternative schema access failed: {e}")
            
        return False
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return False

def test_manual_db_query():
    """Test with raw database URL if available"""
    try:
        from app.config import SUPABASE_URL
        
        # Extract database connection details
        if "supabase.co" in SUPABASE_URL:
            # This is a Supabase hosted database
            print(f"\n🔍 Supabase Project Details:")
            project_id = SUPABASE_URL.split("//")[1].split(".")[0]
            print(f"Project ID: {project_id}")
            
            # Check if the URL is accessible
            import requests
            health_url = f"{SUPABASE_URL}/rest/v1/"
            print(f"Health check URL: {health_url}")
            
            from app.config import SUPABASE_SERVICE_KEY
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            }
            
            response = requests.get(health_url, headers=headers, timeout=10)
            print(f"Health check response: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Supabase API is accessible")
                
                # Try to query the schema information
                schema_url = f"{SUPABASE_URL}/rest/v1/information_schema.tables"
                params = {"select": "table_name,table_schema", "table_schema": "eq.app"}
                
                response = requests.get(schema_url, headers=headers, params=params, timeout=10)
                print(f"Schema query response: {response.status_code}")
                if response.status_code == 200:
                    tables = response.json()
                    print(f"Tables in app schema: {tables}")
                    return len(tables) > 0
                
            return False
            
    except Exception as e:
        print(f"❌ Manual query failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Comprehensive Supabase Testing\n")
    
    success1 = test_direct_connection()
    success2 = test_manual_db_query()
    
    if success1 or success2:
        print(f"\n🎉 Database connection successful!")
        print(f"You can now restart the backend with real database.")
    else:
        print(f"\n🔧 Database connection issues detected.")
        print(f"Possible solutions:")
        print(f"1. Restart Supabase API in dashboard")
        print(f"2. Check if schema was applied correctly")
        print(f"3. Verify RLS policies aren't blocking access")
        print(f"4. Check if project is paused/suspended")