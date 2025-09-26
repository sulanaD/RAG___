#!/usr/bin/env python3
"""
Simple direct table check
"""
import sys
sys.path.append('.')

from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_SERVICE_KEY

def check_tables():
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    # List of possible table references to try
    table_variations = [
        "app.documents",
        "documents", 
        "public.documents",
    ]
    
    for table_name in table_variations:
        try:
            print(f"🧪 Trying table: {table_name}")
            result = supabase.table(table_name).select("*").limit(1).execute()
            print(f"✅ SUCCESS: {table_name} exists! Records: {len(result.data)}")
            
            # If successful, try to insert a test record
            test_record = {
                "name": "connection-test.txt",
                "file_count": 1,
                "page_count": 1,
                "meta": {"test": True}
            }
            
            insert_result = supabase.table(table_name).insert(test_record).execute()
            if insert_result.data:
                print(f"✅ INSERT test successful!")
                # Clean up
                record_id = insert_result.data[0]["id"]
                supabase.table(table_name).delete().eq("id", record_id).execute()
                print(f"✅ Test record cleaned up")
                return table_name
                
        except Exception as e:
            print(f"❌ {table_name}: {e}")
    
    # If no tables worked, let's see what's actually in the database
    print(f"\n🔍 Let's check what schemas exist...")
    try:
        # Try to query information_schema through the API
        import requests
        
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        }
        
        # Check for any tables
        url = f"{SUPABASE_URL}/rest/v1/information_schema.schemata"
        params = {"select": "schema_name"}
        
        response = requests.get(url, headers=headers, params=params)
        print(f"Schemas response: {response.status_code}")
        
        if response.status_code == 200:
            schemas = response.json()
            print(f"Available schemas: {[s['schema_name'] for s in schemas]}")
            
        # Check for tables in different schemas  
        for schema in ['public', 'app']:
            url = f"{SUPABASE_URL}/rest/v1/information_schema.tables"
            params = {"select": "table_name", "table_schema": f"eq.{schema}"}
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                tables = response.json()
                print(f"Tables in {schema}: {[t['table_name'] for t in tables]}")
            
    except Exception as e:
        print(f"Schema inspection failed: {e}")
    
    return None

if __name__ == "__main__":
    working_table = check_tables()
    if working_table:
        print(f"\n🎉 Database is working! Use table: {working_table}")
    else:
        print(f"\n❌ No working tables found. Schema may not be applied correctly.")
        print(f"\n🔧 Next steps:")
        print(f"1. Go to Supabase Dashboard → SQL Editor")
        print(f"2. Re-run the schema.sql file")
        print(f"3. Check for any error messages")
        print(f"4. Go to Settings → API → Restart API")