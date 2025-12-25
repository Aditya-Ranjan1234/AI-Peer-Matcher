import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def inspect_db():
    url = os.getenv('MONGODB_URL')
    if not url:
        print("❌ MONGODB_URL not found")
        return
        
    client = AsyncIOMotorClient(url)
    dbs = await client.list_database_names()
    print(f"📂 Databases found: {dbs}")
    
    for db_name in dbs:
        if db_name in ['admin', 'local', 'config']: continue
        db = client[db_name]
        colls = await db.list_collection_names()
        print(f"📦 Database: {db_name} | Collections: {colls}")
        for c in colls:
            count = await db[c].count_documents({})
            print(f"   - {c}: {count} records")
            
    client.close()

if __name__ == "__main__":
    asyncio.run(inspect_db())
