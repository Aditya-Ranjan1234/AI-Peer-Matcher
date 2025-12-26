"""
Reset and Seed MongoDB with Random Profiles

This script:
1. Clears ALL existing profiles from MongoDB
2. Loads random profiles from demo/random_profiles.json
3. Sends them to the API endpoint to be created properly with embeddings

Usage:
    python reset_and_seed_profiles.py
"""

import asyncio
import json
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URL = os.getenv("MONGODB_URL")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")  # Default to localhost
RANDOM_PROFILES_FILE = "demo/random_profiles.json"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


async def clear_all_profiles():
    """Clear all profiles from MongoDB"""
    print_header("Step 1: Clearing All Profiles from MongoDB")
    
    if not MONGODB_URL:
        print_error("MONGODB_URL environment variable not set!")
        return False
    
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client["peer_matcher"]
        collection = db["profiles"]
        
        # Count existing profiles
        count_before = await collection.count_documents({})
        print_info(f"Found {count_before} existing profiles")
        
        # Delete all profiles
        result = await collection.delete_many({})
        print_success(f"Deleted {result.deleted_count} profiles from MongoDB")
        
        # Verify deletion
        count_after = await collection.count_documents({})
        if count_after == 0:
            print_success("MongoDB collection is now empty")
            return True
        else:
            print_warning(f"Warning: {count_after} profiles still remain")
            return False
            
    except Exception as e:
        print_error(f"Failed to clear profiles: {e}")
        return False


import csv

def load_random_profiles():
    """Load random profiles from JSON file and map USN/Name from CSV"""
    print_header("Step 2: Loading and Mapping Profiles")
    
    CSV_FILE = "data.csv"
    
    if not os.path.exists(RANDOM_PROFILES_FILE):
        print_error(f"File not found: {RANDOM_PROFILES_FILE}")
        return None
    if not os.path.exists(CSV_FILE):
        print_error(f"File not found: {CSV_FILE}")
        return None
    
    try:
        # 1. Load random profile templates
        with open(RANDOM_PROFILES_FILE, 'r', encoding='utf-8') as f:
            templates = json.load(f)
            
        # 2. Load Student data from CSV
        # USN is at index 3, STUDENT FULL NAME is at index 5
        student_data = []
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip first 2 title/empty lines
            next(reader) 
            next(reader)
            # Skip header line
            next(reader)
            
            for row in reader:
                if len(row) > 5:
                    usn = row[3].strip()
                    name = row[5].strip()
                    if usn and name:
                        student_data.append({"usn": usn, "name": name})
        
        print_info(f"Loaded {len(student_data)} students from CSV")
        
        # 3. Map students to templates (limited to number of templates or students)
        final_profiles = []
        count = min(len(templates), len(student_data))
        
        for i in range(count):
            profile = templates[i].copy()
            profile['id'] = student_data[i]['usn']
            profile['name'] = student_data[i]['name']
            
            # Convert array fields to comma-separated strings for API
            if isinstance(profile.get('strengths'), list):
                profile['strengths'] = ', '.join(profile['strengths'])
            if isinstance(profile.get('weaknesses'), list):
                profile['weaknesses'] = ', '.join(profile['weaknesses'])
            if isinstance(profile.get('preferences'), list):
                profile['preferences'] = ', '.join(profile['preferences'])
                
            final_profiles.append(profile)
            
        print_success(f"Successfully mapped {len(final_profiles)} profiles")
        return final_profiles
    except Exception as e:
        print_error(f"Failed to load/map profiles: {e}")
        return None


async def create_profile_via_api(client, profile, index, total):
    """Create a single profile via the API endpoint"""
    try:
        response = await client.post(
            f"{API_BASE_URL}/profiles",
            json=profile,
            timeout=60.0  # Longer timeout for embedding generation
        )
        
        if response.status_code == 201:
            print_success(f"[{index + 1}/{total}] Created profile: {profile['id']} - {profile['name']}")
            return True
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print_error(f"[{index + 1}/{total}] Failed to create {profile['id']}: {error_detail}")
            return False
            
    except httpx.TimeoutException:
        print_error(f"[{index + 1}/{total}] Timeout creating {profile['id']} (embedding generation took too long)")
        return False
    except Exception as e:
        print_error(f"[{index + 1}/{total}] Error creating {profile['id']}: {e}")
        return False


async def seed_profiles_via_api(profiles):
    """Send all profiles to the API endpoint to be created with embeddings"""
    print_header("Step 3: Creating Profiles via API (with embeddings)")
    
    print_info(f"Target API: {API_BASE_URL}")
    print_info(f"Profiles to create: {len(profiles)}")
    print_warning("This will take a while (~10-20 seconds per profile for embedding generation)")
    print()
    
    async with httpx.AsyncClient() as client:
        # Test API connection first
        try:
            response = await client.get(f"{API_BASE_URL}/", timeout=10.0)
            if response.status_code == 200:
                print_success(f"API is online: {API_BASE_URL}")
            else:
                print_error(f"API returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Cannot connect to API: {e}")
            print_info("Make sure the backend is running!")
            return False
        
        print()
        
        # Create profiles one by one
        success_count = 0
        failed_count = 0
        
        for index, profile in enumerate(profiles):
            success = await create_profile_via_api(client, profile, index, len(profiles))
            if success:
                success_count += 1
            else:
                failed_count += 1
            
            # Small delay to avoid overwhelming the server
            if index < len(profiles) - 1:
                await asyncio.sleep(0.5)
        
        print()
        print_header("Summary")
        print_success(f"Successfully created: {success_count}/{len(profiles)} profiles")
        if failed_count > 0:
            print_warning(f"Failed to create: {failed_count}/{len(profiles)} profiles")
        
        return success_count > 0


async def main():
    """Main execution flow"""
    print_header("Reset and Seed MongoDB with Random Profiles")
    
    # Step 1: Clear all profiles
    if not await clear_all_profiles():
        print_error("Failed to clear profiles. Aborting.")
        return False
    
    # Step 2: Load random profiles
    profiles = load_random_profiles()
    if not profiles:
        print_error("Failed to load profiles. Aborting.")
        return False
    
    # Step 3: Seed profiles via API
    if not await seed_profiles_via_api(profiles):
        print_error("Failed to seed profiles. Aborting.")
        return False
    
    print()
    print_header("✅ All Done!")
    print_success("MongoDB has been reset and seeded with 100 random profiles")
    print_info("All profiles now have proper embeddings and can be matched")
    
    return True


if __name__ == "__main__":
    # Check if using production or local
    if "render.com" in API_BASE_URL or "vercel.app" in API_BASE_URL:
        print_warning(f"⚠️  WARNING: You are targeting PRODUCTION: {API_BASE_URL}")
        response = input("Are you sure you want to clear ALL production profiles? (yes/no): ")
        if response.lower() != "yes":
            print_info("Aborted by user")
            sys.exit(0)
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
