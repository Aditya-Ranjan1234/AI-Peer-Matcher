"""
Database Management Script
Populate or clear student profiles in the backend
"""
import requests
import json

API_BASE = "https://ai-peer-matcher.onrender.com"

def status():
    """Check current database status"""
    print("Checking database status...")
    r = requests.get(f"{API_BASE}/")
    data = r.json()
    print(f"\n✅ Backend: {data['status']}")
    print(f"📊 Total Profiles: {data['total_profiles']}\n")
    return data['total_profiles']

def clear_all():
    """Clear all profiles from database"""
   print("\n⚠️  WARNING: This will delete ALL profiles!")
    confirm = input("Type 'YES' to confirm: ")
    
    if confirm != "YES":
        print("❌ Cancelled")
        return
    
    print("\nFetching all profiles...")
    r = requests.get(f"{API_BASE}/profiles")
    profiles = r.json()['profiles']
    
    deleted = 0
    for profile in profiles:
        try:
            r = requests.delete(f"{API_BASE}/profiles/{profile['id']}")
            if r.status_code == 200:
                deleted += 1
                if deleted % 10 == 0:
                    print(f"Deleted {deleted}/{len(profiles)}...")
        except Exception as e:
            print(f"Error deleting {profile['id']}: {e}")
    
    print(f"\n✅ Deleted {deleted} profiles")
    status()

def populate():
    """Run the populate_demo.py script"""
    print("\n📥 Running population script...")
    print("This will add 100 random student profiles\n")
    
    import subprocess
    import os
    
    script_path = os.path.join(os.path.dirname(__file__), 'demo', 'populate_demo.py')
    subprocess.run(['python', script_path])

def main():
    print("=" * 70)
    print("DATABASE MANAGEMENT")
    print("=" * 70)
    
    current_count = status()
    
    print("Options:")
    print("  1. Populate database (add 100 profiles)")
    print("  2. Clear all profiles")
    print("  3. Just show status")
    print("  4. Exit")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == "1":
        populate()
    elif choice == "2":
        clear_all()
    elif choice == "3":
        status()
    elif choice == "4":
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
