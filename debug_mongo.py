import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "peer_matcher" 

TARGET_IDS = [
    "1RV23AI018"
]

def debug():
    print(f"Using MongoDB URL: {MONGO_URL.split('@')[-1] if '@' in MONGO_URL else MONGO_URL}")
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"DB Name: {DB_NAME}")
    print(f"Collections: {db.list_collection_names()}")
    
    count = db.profiles.count_documents({})
    print(f"Total Profiles: {count}")
    
    target_count = db.profiles.count_documents({"id": {"$in": TARGET_IDS}})
    print(f"Target '1RV23AI018' count: {target_count}")
    
    if target_count == 0:
        print("Newest 10 IDs in DB (sorted by _id desc):")
        for p in db.profiles.find().sort("_id", -1).limit(10):
            print(f"  - {p.get('id')} (Name: {p.get('name', 'N/A')})")

if __name__ == "__main__":
    debug()
