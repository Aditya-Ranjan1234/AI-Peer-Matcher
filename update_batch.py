import requests
from pymongo import MongoClient
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = "http://127.0.0.1:8000/signup"
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "peer_matcher" 

# Data
USERS_DATA = [
    {"id": "1RV23AI018", "name": "Anjali Suresh Kalarikkal", "strengths": "Mathematics, Biology, Computer Science, Programming, English Literature, Creative Writing, History", "weaknesses": "Chemistry, Economics, Psychology, Business, Music", "password": "1RVAn"},
    {"id": "1RV23AI054", "name": "Mayur Kumar K N", "strengths": "Mathematics, Computer Science, English Literature, Creative Writing, History", "weaknesses": "Physics, Economics, Psychology, Business, Music", "password": "1RVMa"},
    {"id": "1RV23AI034", "name": "Garv Agarwalla", "strengths": "Mathematics, Computer Science, Programming, Statistics", "weaknesses": "Chemistry, Economics, Psychology", "password": "1RVGa"},
    {"id": "1RV23CY028", "name": "Meda Mounika", "strengths": "Mathematics, Computer Science", "weaknesses": "Programming, Creative Writing, Art, Music", "password": "1RVMe"},
    {"id": "1RV23CY019", "name": "Esha Sharma", "strengths": "Mathematics, Computer Science, Programming, Creative Writing, History, Art, Music", "weaknesses": "Physics, Chemistry, Biology, Economics, Business, Statistics", "password": "1RVEs"},
    {"id": "1RV23CS087", "name": "Eshitha Chowdary Nattem", "strengths": "Mathematics, Chemistry, Computer Science", "weaknesses": "English Literature, Creative Writing, History, Economics, Psychology, Business, Statistics, Art, Music", "password": "1RVEs"},
    {"id": "1RV23CD019", "name": "Shravani G L", "strengths": "Creative Writing, Art, Music", "weaknesses": "Mathematics, Computer Science, Programming, Statistics", "password": "1RVSh"},
    {"id": "1RV23CY006", "name": "Akshaya Sannapureddy", "strengths": "Chemistry, Computer Science, Programming", "weaknesses": "Mathematics, Statistics", "password": "1RVAk"},
    {"id": "1RV23CY063", "name": "Yashmitha Desai", "strengths": "Mathematics, Biology, English Literature, History", "weaknesses": "Physics, Programming, Psychology, Business, Statistics", "password": "1RVYa"},
    {"id": "1RV23AI050", "name": "Maheshkumar Malge", "strengths": "Mathematics, Physics, Computer Science, Programming, Economics, Psychology, Business, Statistics", "weaknesses": "Chemistry, Biology, English Literature, Creative Writing, History, Economics, Psychology, Art", "password": "1RVMa"},
    {"id": "1RV23CD061", "name": "Yashashwini S", "strengths": "Mathematics, Biology, Computer Science, History", "weaknesses": "Computer Science, Programming, Statistics", "password": "1RVYa"},
    {"id": "1RV23CD055", "name": "Sinchana RV", "strengths": "Mathematics, Physics, Chemistry, Biology, English Literature", "weaknesses": "Computer Science, Programming", "password": "1RVSi"}
]

def update_profiles():
    print("Connecting to MongoDB...")
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    target_ids = [u["id"] for u in USERS_DATA]
    print(f"Targeting {len(target_ids)} users for update.")

    # 1. Cleanup
    print("Deleting existing records...")
    res_users = db.users.delete_many({"id": {"$in": target_ids}})
    res_profiles = db.profiles.delete_many({"id": {"$in": target_ids}})
    print(f"Deleted {res_users.deleted_count} users and {res_profiles.deleted_count} profiles.")

    # 2. Re-Signup
    print("Creating new profiles via API...")
    success_count = 0
    for user in USERS_DATA:
        payload = {
            "id": user["id"],
            "password": user["password"],
            "name": user["name"].strip(),
            "strengths": user["strengths"],
            "weaknesses": user["weaknesses"],
            "description": f"Student {user['name']}"
        }
        
        try:
            resp = requests.post(API_URL, json=payload)
            if resp.status_code in [200, 201]:
                print(f"  [OK] {user['id']}")
                success_count += 1
            else:
                print(f"  [FAIL] {user['id']}: {resp.text}")
        except Exception as e:
            print(f"  [ERR] {user['id']}: {e}")
        
        time.sleep(2)

    print(f"\nUpdate Complete. Successfully updated {success_count}/{len(USERS_DATA)} profiles.")

if __name__ == "__main__":
    update_profiles()
