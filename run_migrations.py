import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

async def run_migrations():
    print("Running migrations...")
    
    # Load environment variables
    load_dotenv()
    
    # Connect to Supabase
    supabase = create_client(
        os.getenv("URL_SUPABASE"),
        os.getenv("API_SUPABASE")
    )
    
    # Read migration file
    with open("migrations/add_language_field.sql", "r") as f:
        migration_sql = f.read()
    
    # Execute migration
    try:
        # Using raw SQL query
        result = supabase.table("users").execute_sql(migration_sql)
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error running migration: {e}")

if __name__ == "__main__":
    asyncio.run(run_migrations()) 