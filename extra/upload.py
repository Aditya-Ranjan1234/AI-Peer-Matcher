# upload_demo_profiles.py
import asyncio
import aiohttp
import json
from pathlib import Path
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8000"
DEFAULT_PASSWORD = "12345678"  # Default password for all demo accounts

async def create_user(session, user_id, name, password):
    """Create a user account using the /signup endpoint"""
    url = f"{API_BASE_URL}/signup"
    user_data = {
        "id": user_id,
        "password": password
    }
    
    async with session.post(url, json=user_data) as response:
        if response.status == 400:
            error = await response.json()
            if "already registered" in error.get("detail", ""):
                print(f"ℹ️  User {user_id} already exists, skipping...")
                return True  # Skip to next step
            raise Exception(f"Error creating user {user_id}: {error.get('detail', 'Unknown error')}")
        response.raise_for_status()
        return True

async def create_profile(session, profile_data):
    """Create a profile using the /profiles endpoint"""
    url = f"{API_BASE_URL}/profiles"
    
    # Ensure the profile data matches the ProfileInput model
    profile = {
        "id": profile_data["id"],
        "name": profile_data["name"],
        "strengths": profile_data["strengths"],
        "weaknesses": profile_data["weaknesses"],
        "preferences": profile_data.get("preferences", ""),
        "description": profile_data.get("description", "")
    }
    
    async with session.post(url, json=profile) as response:
        if response.status == 400:
            error = await response.json()
            if "already exists" in error.get("detail", ""):
                print(f"ℹ️  Profile {profile['id']} already exists, skipping...")
                return True
        response.raise_for_status()
        return True

async def process_profile(session, profile, password):
    """Process a single profile - create user and profile"""
    user_id = profile["id"]
    try:
        # 1. Create user account
        await create_user(session, user_id, profile["name"], password)
        
        # 2. Create profile with embeddings
        await create_profile(session, profile)
        
        return True, user_id
    except Exception as e:
        return False, f"{user_id}: {str(e)}"

async def upload_profiles():
    """Main function to upload demo profiles"""
    profiles_path = Path(__file__).parent / "demo_profiles.json"
    
    if not profiles_path.exists():
        print(f"❌ Error: {profiles_path} not found")
        return

    # Read the demo profiles
    with open(profiles_path, 'r', encoding='utf-8') as f:
        profiles = json.load(f)

    if not profiles:
        print("❌ No profiles found in the JSON file")
        return

    print(f"📂 Found {len(profiles)} profiles to upload")
    print(f"🔗 Using API endpoint: {API_BASE_URL}")
    print(f"🔑 Using default password: {DEFAULT_PASSWORD}")
    print("=" * 50)

    success_count = 0
    error_count = 0
    errors = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for profile in profiles:
            tasks.append(process_profile(session, profile, DEFAULT_PASSWORD))
        
        # Process profiles in batches of 10
        for i in range(0, len(tasks), 10):
            batch = tasks[i:i+10]
            results = await asyncio.gather(*batch, return_exceptions=True)
            
            for success, result in results:
                if success:
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"✅ Processed {success_count}/{len(profiles)} profiles...")
                else:
                    error_count += 1
                    errors.append(result)
                    print(f"❌ Error: {result}")

    # Print summary
    print("\n" + "=" * 50)
    print(f"✅ Successfully processed {success_count} profiles")
    if error_count > 0:
        print(f"⚠️  Failed to process {error_count} profiles")
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
    print("=" * 50)

if __name__ == "__main__":
    print("=== Uploading Demo Profiles via API ===")
    print("This will create user accounts and profiles through the backend API")
    print("Make sure the backend server is running")
    print("=" * 50)
    
    asyncio.run(upload_profiles())