import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")

async def verify_seeded_data():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client["peer_matcher"]
    profiles = db["profiles"]
    
    print("=== VERIFICATION ===")
    total = await profiles.count_documents({})
    print(f"Total profiles: {total}")
    
    # In verify_seed_data.py, add this before the asyncio.run() call:
    users = db["users"]
    user_count = await users.count_documents({})
    print(f"Total users in auth collection: {user_count}")

    # Add this to find users without profiles
    users_without_profiles = await users.count_documents({
        "id": {"$nin": [p["id"] for p in await profiles.find({}, {"id": 1}).to_list(length=None)]}
    })
    print(f"Users without profiles: {users_without_profiles}")
    
    # Sample profiles
    cursor = profiles.find({}, {"_id": 0, "id": 1, "name": 1, "strengths": 1, "weaknesses": 1}).limit(3)
    async for profile in cursor:
        print(f"\nUSN: {profile.get('id')}")
        print(f"Name: {profile.get('name')}")
        print(f"Strengths: {profile.get('strengths')}")
        print(f"Weaknesses: {profile.get('weaknesses')}")
    
    # Count with strengths/weaknesses
    with_strengths = await profiles.count_documents({"strengths": {"$ne": ""}})
    with_weaknesses = await profiles.count_documents({"weaknesses": {"$ne": ""}})
    print(f"\nWith strengths: {with_strengths}/{total}")
    print(f"With weaknesses: {with_weaknesses}/{total}")

if __name__ == "__main__":
    asyncio.run(verify_seeded_data())