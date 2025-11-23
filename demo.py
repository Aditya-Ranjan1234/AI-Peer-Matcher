import requests
import sys
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000"

# Create a new profile
print("Creating new profile...")
profile = {
    "id": "stu100",
    "name": "Frank Miller",
    "strengths": "Creative Writing, English Literature, Poetry, Drama, Reading",
    "weaknesses": "Calculus, Linear Algebra, Statistics, Mathematics, Physics",
    "preferences": "Mornings, quiet study",
    "description": "Love reading and writing, need serious help with math!"
}

r = requests.post(f"{API_BASE}/profiles", json=profile)
if r.status_code == 201:
    print("✅ Profile created!")
else:
    print(f"⚠️  {r.json()['detail']}")

# Get matches
print(f"\nFinding matches for {profile['name']}...")
print(f"Strengths: {profile['strengths']}")
print(f"Weaknesses: {profile['weaknesses']}")

m = requests.get(f"{API_BASE}/match/{profile['id']}?top_k=3")
data = m.json()

print(f"\n🎯 Top {data['total_matches']} Matches:\n")
for i, match in enumerate(data['matches'], 1):
    score = match['score'] * 100
    print(f"{i}. {match['name']} - {score:.1f}%")
    print(f"   Can help with: {match['strengths']}")
    print(f"   Needs help with: {match['weaknesses']}\n")
