"""
Upload profiles from demo_profiles.json to live backend
"""
import json
import requests

API_BASE = "https://ai-peer-matcher.onrender.com"

print("=" * 70)
print("UPLOADING PROFILES FROM demo_profiles.json")
print("=" * 70)

# Check backend status
print("\n1. Checking backend...")
try:
    r = requests.get(f"{API_BASE}/", timeout=10)
    status = r.json()
    print(f"   ✅ Backend online")
    print(f"   📊 Current profiles: {status['total_profiles']}")
except Exception as e:
    print(f"   ❌ Backend not reachable: {e}")
    print("   ⏳ Tip: Render free tier takes ~30 seconds to wake up")
    exit(1)

# Load profiles from JSON
print("\n2. Loading demo_profiles.json...")
try:
    with open("demo_profiles.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)
    print(f"   ✅ Loaded {len(profiles)} profiles from file")
except Exception as e:
    print(f"   ❌ Error loading file: {e}")
    exit(1)

# Upload each profile
print(f"\n3. Uploading {len(profiles)} profiles...")
print("   (This may take a minute...)\n")

success = 0
skipped = 0
errors = 0

for i, profile in enumerate(profiles, 1):
    try:
        r = requests.post(f"{API_BASE}/profiles", json=profile, timeout=10)
        
        if r.status_code == 201:
            success += 1
            if success % 10 == 0:
                print(f"   ✅ Uploaded {success}/{len(profiles)}...")
        elif r.status_code == 400 and "already exists" in r.text:
            skipped += 1
        else:
            errors += 1
            print(f"   ⚠️  Error with {profile['id']}: {r.status_code}")
            
    except Exception as e:
        errors += 1
        print(f"   ❌ Failed to upload {profile.get('id', 'unknown')}: {e}")

# Final status
print("\n" + "=" * 70)
print("UPLOAD COMPLETE")
print("=" * 70)
print(f"✅ Successfully uploaded: {success}")
print(f"⏭️  Skipped (already exist): {skipped}")
print(f"❌ Errors: {errors}")

# Check final count
r = requests.get(f"{API_BASE}/")
final_count = r.json()['total_profiles']
print(f"\n📊 Total profiles in backend: {final_count}")

if success > 0:
    print("\n🎉 Done! Your backend is now populated with profiles!")
    print(f"   Visit: https://ai-peer-matcher.vercel.app to test!")
else:
    print("\n⚠️  No new profiles added. They might already exist.")
    print(f"   To clear and re-add, use: python manage_database.py")
