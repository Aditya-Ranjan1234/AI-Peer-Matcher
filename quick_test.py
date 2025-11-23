"""
Quick test to verify matching with existing profiles
"""
import requests
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000"

print("=" * 70)
print("Testing AI-Powered Peer Learning Matcher")
print("=" * 70)

# Get all profiles
print("\n1. Getting all existing profiles...")
response = requests.get(f"{API_BASE}/profiles")
if response.status_code == 200:
    data = response.json()
    print(f"✅ Found {data['total']} profiles")
    for profile in data['profiles']:
        print(f"   - {profile['name']} (ID: {profile['id']})")
else:
    print("❌ Failed to get profiles")
    sys.exit(1)

# Test matches for first student
if data['profiles']:
    student = data['profiles'][0]
    print(f"\n2. Finding matches for {student['name']}...")
    print(f"   Strengths: {student['strengths']}")
    print(f"   Weaknesses: {student['weaknesses']}")
    
    response = requests.get(f"{API_BASE}/match/{student['id']}?top_k=3")
    if response.status_code == 200:
        matches = response.json()
        print(f"\n✅ Top {matches['total_matches']} matches:")
        
        for i, match in enumerate(matches['matches'], 1):
            score_pct = match['score'] * 100
            print(f"\n   Match #{i}: {match['name']}")
            print(f"   Score: {score_pct:.1f}%")
            print(f"   Can help you with: {match['strengths']}")
            print(f"   Needs help with: {match['weaknesses']}")
    else:
        print(f"❌ Failed to get matches: {response.text}")

print("\n" + "=" * 70)
print("✅ Test Complete!")
print("=" * 70)
