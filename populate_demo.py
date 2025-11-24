"""
Simplified script to check current profiles and add remaining profiles
"""
import requests
import random
import json

API_BASE = "http://localhost:8000"

# First and last names
FIRST = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
         "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
         "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
         "Matthew", "Betty", "Anthony", "Margaret"," Mark", "Sandra", "Donald", "Ashley"]

LAST = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor",
        "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris"]

# Subject lists
STEM = ["Mathematics", "Calculus", "Algebra", "Physics", "Chemistry", "Biology",
        "Computer Science", "Programming", "Statistics", "Engineering"]

HUMANITIES = ["English Literature", "Creative Writing", "History", "Philosophy",
              "Psychology", "Art", "Music", "Foreign Languages", "Sociology"]

BUSINESS = ["Business", "Marketing", "Finance", "Accounting", "Economics", "Management"]

def gen_profile(num):
    """Generate one profile"""
    name = f"{random.choice(FIRST)} {random.choice(LAST)}"
    focus = random.choice(["STEM", "HUMANITIES", "BUSINESS"])
    
    if focus == "STEM":
        strengths = random.sample(STEM, 3)
        weaknesses = random.sample(HUMANITIES, 3)
    elif focus == "HUMANITIES":
        strengths = random.sample(HUMANITIES, 3)
        weaknesses = random.sample(STEM, 3)
    else:
        strengths = random.sample(BUSINESS, 3)
        weaknesses = random.sample(STEM if random.random() > 0.5 else HUMANITIES, 3)
    
    return {
        "id": f"demo{num:03d}",
        "name": name,
        "strengths": ", ".join(strengths),
        "weaknesses": ", ".join(weaknesses),
        "preferences": "Flexible",
        "description": "Eager to learn and collaborate"
    }

print("Checking current database...")
r = requests.get(f"{API_BASE}/")
current = r.json()['total_profiles']
print(f"Current profiles: {current}")

# Generate remaining profiles
needed = max(0, 100 - current)
print(f"\nGenerating {needed} more profiles...")

profiles = []
success = 0

for i in range(current + 1, current + needed + 1):
    profile = gen_profile(i)
    profiles.append(profile)
    
    try:
        r = requests.post(f"{API_BASE}/profiles", json=profile)
        if r.status_code == 201:
            success += 1
            if success % 10 == 0:
                print(f"Created {success}/{needed}...")
    except Exception as e:
        print(f"Error: {e}")

print(f"\n✅ Added {success} new profiles!")
print(f"Total profiles in database: {current + success}")

# Save all profiles
with open("demo_profiles.json", "w") as f:
    json.dump(profiles, f, indent=2)

print("\n" + "="*70)
print("📋 DEMO PROFILES FOR YOUR PRESENTATION")
print("="*70)

# Get 3 diverse demo profiles
demo1 = {
    "id": "DEMO_A",
    "name": "Alex Rivera", 
    "strengths": "Mathematics, Calculus, Physics, Problem Solving",
    "weaknesses": "English Literature, Creative Writing, Essay Writing",
    "preferences": "Evenings, small groups",
    "description": "I excel at math but struggle with writing assignments"
}

demo2 = {
    "id": "DEMO_B",
    "name": "Sophie Chen",
    "strengths": "English Literature, Creative Writing, Poetry, Reading Analysis",
    "weaknesses": "Calculus, Statistics, Mathematics, Physics",
    "preferences": "Afternoons, one-on-one sessions",
    "description": "Love reading and writing, but math is very challenging for me"
}

demo3 = {
    "id": "DEMO_C",
    "name": "Marcus Johnson",
    "strengths": "Computer Science, Programming, Web Development, Algorithms",
    "weaknesses": "Biology, Chemistry, Organic Chemistry",
    "preferences": "Flexible schedule, online preferred",
    "description": "Passionate about coding, need help with science courses"
}

demos = [demo1, demo2, demo3]

for i, d in enumerate(demos, 1):
    print(f"\n{'='*70}")
    print(f"DEMO PROFILE #{i}")
    print(f"{'='*70}")
    print(f"Student ID: {d['id']}")
    print(f"Name: {d['name']}")
    print(f"Strengths: {d['strengths']}")
    print(f"Weaknesses: {d['weaknesses']}")
    print(f"Preferences: {d['preferences']}")
    print(f"Description: {d['description']}")

# Test matching for demo1
print(f"\n\n{'='*70}")
print(f"TESTING MATCH FOR: {demo1['name']}")
print(f"{'='*70}")

# First create the demo profile if it doesn't exist
try:
    r = requests.post(f"{API_BASE}/profiles", json=demo1)
except:
    pass  # Might already exist

r = requests.get(f"{API_BASE}/match/{demo1['id']}?top_k=5")
if r.status_code == 200:
    matches = r.json()['matches']
    print(f"\nTop 5 matches:")
    for i, m in enumerate(matches, 1):
        print(f"\n  {i}. {m['name']} - {m['score']*100:.1f}%")
        print(f"     Can help with: {m['strengths']}")
        print(f"     Needs help: {m['weaknesses']}")

print(f"\n\n✅ READY FOR DEMO!")
print(f"\n💡 Instructions:")
print(f"1. Open frontend/index.html in your browser")
print(f"2. Use the demo profiles above to create new students")
print(f"3. See intelligent matching in action!")
