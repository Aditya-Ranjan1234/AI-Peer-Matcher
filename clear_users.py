import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def clear_users():
    url = os.getenv('MONGODB_URL')
    if not url:
        # Try finding .env in the parent directory if not found (for common project structures)
        load_dotenv('../.env')
        url = os.getenv('MONGODB_URL')
        
    if not url:
        print("❌ Error: MONGODB_URL not found in .env")
        return
        
    client = AsyncIOMotorClient(url)
    # Get database name from URL or default to 'peer_matcher'
    db_name = url.split('/')[-1].split('?')[0] or "peer_matcher"
    db = client[db_name]
    coll = db["users"]
    
    print(f"📡 Connecting to Database: {db_name}")
    
    # Count how many users exist
    count = await coll.count_documents({})
    print(f"🔍 Found {count} registered users in '{db_name}.users'")
    
    if count > 0:
        result = await coll.delete_many({})
        print(f"✅ Successfully deleted {result.deleted_count} user credentials.")
        print("🚀 Users can now sign up again from scratch for their USNs.")
    else:
        print("💡 No user credentials found to delete.")
        
    client.close() # Note: motor's client.close() is NOT an awaitable

if __name__ == "__main__":
    asyncio.run(clear_users())
