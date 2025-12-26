# clear_database.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

async def clear_database():
    # Load environment variables
    load_dotenv()
    MONGODB_URL = os.getenv("MONGODB_URL")
    
    if not MONGODB_URL:
        # Try parent directory's .env if not found
        load_dotenv('../.env')
        MONGODB_URL = os.getenv("MONGODB_URL")
        
    if not MONGODB_URL:
        print("❌ Error: MONGODB_URL not found in .env")
        return

    print("🔗 Connecting to database...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db_name = MONGODB_URL.split('/')[-1].split('?')[0] or "peer_matcher"
    db = client[db_name]
    
    # Collections to clear
    collections = {
        "users": "User credentials",
        "profiles": "User profiles",
        "projects": "Projects",
        "sessions": "Active sessions",
        "matches": "Match history",
        "teams": "Team formations"
    }
    
    try:
        # Get list of all collections
        all_collections = await db.list_collection_names()
        
        # Clear each collection
        for coll_name, description in collections.items():
            if coll_name in all_collections:
                result = await db[coll_name].delete_many({})
                print(f"✅ Cleared {result.deleted_count} {description} from '{coll_name}'")
            else:
                print(f"ℹ️  Collection '{coll_name}' not found, skipping...")
        
        print("\n✨ Database cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing database: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    print("=== DATABASE CLEANUP TOOL ===")
    print("WARNING: This will delete ALL data from the database!")
    confirmation = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if confirmation == 'yes':
        asyncio.run(clear_database())
    else:
        print("Operation cancelled.")