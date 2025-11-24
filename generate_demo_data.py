"""
Generate 100 random student profiles and populate the backend
"""
import requests
import random
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000"

# Lists of first and last names
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna",
    "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Catherine", "Patrick", "Carolyn", "Raymond", "Janet",
    "Jack", "Ruth", "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
    "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers"
]

# Subject categories
STEM_SUBJECTS = [
    "Mathematics", "Calculus", "Algebra", "Geometry", "Statistics", "Trigonometry",
    "Physics", "Quantum Physics", "Mechanics", "Thermodynamics", "Electromagnetism",
    "Chemistry", "Organic Chemistry", "Inorganic Chemistry", "Biochemistry",
    "Biology", "Molecular Biology", "Genetics", "Anatomy", "Ecology",
    "Computer Science", "Programming", "Algorithms", "Data Structures", "Web Development",
    "Machine Learning", "Artificial Intelligence", "Database Design", "Software Engineering",
    "Engineering", "Mechanical Engineering", "Electrical Engineering", "Civil Engineering"
]

HUMANITIES_SUBJECTS = [
    "English Literature", "Creative Writing", "Poetry", "Essay Writing", "Reading Comprehension",
    "History", "World History", "American History", "European History", "Ancient Civilizations",
    "Philosophy", "Ethics", "Logic", "Critical Thinking",
    "Psychology", "Social Psychology", "Cognitive Psychology", "Developmental Psychology",
    "Sociology", "Anthropology", "Political Science", "Economics",
    "Foreign Languages", "Spanish", "French", "German", "Mandarin Chinese",
    "Art", "Art History", "Visual Arts", "Drawing", "Painting",
    "Music", "Music Theory", "Music History", "Performance"
]

BUSINESS_SUBJECTS = [
    "Business Administration", "Marketing", "Finance", "Accounting", "Economics",
    "Management", "Entrepreneurship", "Business Strategy", "Operations Management",
    "Data Analysis", "Business Analytics", "Financial Analysis", "Market Research"
]

def generate_student_profile(student_id):
    """Generate a random student profile"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    
    # Randomly choose if student is STEM-focused, Humanities-focused, or Business-focused
    focus = random.choice(["STEM", "HUMANITIES", "BUSINESS", "MIXED"])
    
    if focus == "STEM":
        # STEM student - strong in STEM, weak in Humanities
        strengths_pool = STEM_SUBJECTS
        weaknesses_pool = HUMANITIES_SUBJECTS
    elif focus == "HUMANITIES":
        # Humanities student - strong in Humanities, weak in STEM
        strengths_pool = HUMANITIES_SUBJECTS
        weaknesses_pool = STEM_SUBJECTS
    elif focus == "BUSINESS":
        # Business student - strong in Business, weak in either STEM or Humanities
        strengths_pool = BUSINESS_SUBJECTS
        weaknesses_pool = STEM_SUBJECTS if random.random() > 0.5 else HUMANITIES_SUBJECTS
    else:
        # Mixed - random strengths and weaknesses
        all_subjects = STEM_SUBJECTS + HUMANITIES_SUBJECTS + BUSINESS_SUBJECTS
        strengths_pool = random.sample(all_subjects, 20)
        # Ensure weaknesses are from different area
        if any(s in STEM_SUBJECTS for s in strengths_pool):
            weaknesses_pool = HUMANITIES_SUBJECTS
        else:
            weaknesses_pool = STEM_SUBJECTS
    
    # Select 3-5 strengths and 3-5 weaknesses
    num_strengths = random.randint(3, 5)
    num_weaknesses = random.randint(3, 5)
    
    strengths = random.sample(strengths_pool, min(num_strengths, len(strengths_pool)))
    weaknesses = random.sample(weaknesses_pool, min(num_weaknesses, len(weaknesses_pool)))
    
    # Preferences
    times = ["Mornings", "Afternoons", "Evenings", "Weekends", "Flexible schedule"]
    group_sizes = ["one-on-one", "small groups", "large groups", "any size group"]
    modes = ["in-person", "online sessions", "hybrid learning"]
    
    preferences = f"{random.choice(times)}, {random.choice(group_sizes)}, {random.choice(modes)}"
    
    # Descriptions
    learning_styles = [
        "I'm a visual learner who loves diagrams and charts",
        "I prefer hands-on practice and real-world examples",
        "I learn best through discussion and collaboration",
        "I enjoy solving problems independently first",
        "I like structured learning with clear objectives",
        "I'm passionate about creative projects",
        "I excel at analytical thinking and problem-solving",
        "I enjoy teaching others what I know",
        "I need help staying motivated and organized",
        "I'm eager to improve my weak areas"
    ]
    
    description = random.choice(learning_styles)
    
    return {
        "id": student_id,
        "name": name,
        "strengths": ", ".join(strengths),
        "weaknesses": ", ".join(weaknesses),
        "preferences": preferences,
        "description": description
    }

def populate_database():
    """Generate and populate 100 student profiles"""
    print("=" * 70)
    print("🎓 Generating 100 Random Student Profiles")
    print("=" * 70)
    
    profiles = []
    success_count = 0
    
    for i in range(1, 101):
        student_id = f"demo{i:03d}"  # demo001, demo002, etc.
        profile = generate_student_profile(student_id)
        profiles.append(profile)
        
        try:
            response = requests.post(f"{API_BASE}/profiles", json=profile)
            if response.status_code == 201:
                success_count += 1
                if i % 10 == 0:  # Progress update every 10 students
                    print(f"✅ Created {i}/100 profiles...")
            else:
                print(f"⚠️  Failed to create {profile['name']}: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Error creating {profile['name']}: {e}")
    
    print(f"\n✅ Successfully created {success_count}/100 profiles!")
    
    # Save profiles to file for reference
    import json
    with open("demo_profiles.json", "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Saved all profiles to: demo_profiles.json")
    
    return profiles

def select_demo_profiles(profiles):
    """Select 3 interesting profiles for demo"""
    print("\n" + "=" * 70)
    print("🎯 DEMO PROFILES - Use these for your presentation")
    print("=" * 70)
    
    # Find a STEM student
    stem_student = next((p for p in profiles if any(s in p['strengths'] for s in ["Mathematics", "Physics", "Computer Science"])), None)
    
    # Find a Humanities student
    humanities_student = next((p for p in profiles if any(s in p['strengths'] for s in ["Literature", "Writing", "History"])), None)
    
    # Find a Business student
    business_student = next((p for p in profiles if any(s in p['strengths'] for s in ["Business", "Marketing", "Finance"])), None)
    
    demo_profiles = []
    if stem_student:
        demo_profiles.append(stem_student)
    if humanities_student:
        demo_profiles.append(humanities_student)
    if business_student:
        demo_profiles.append(business_student)
    
    # If we don't have 3, just pick random ones
    while len(demo_profiles) < 3:
        profile = random.choice(profiles)
        if profile not in demo_profiles:
            demo_profiles.append(profile)
    
    for i, profile in enumerate(demo_profiles, 1):
        print(f"\n📋 DEMO PROFILE #{i}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Student ID: {profile['id']}")
        print(f"Name: {profile['name']}")
        print(f"Strengths: {profile['strengths']}")
        print(f"Weaknesses: {profile['weaknesses']}")
        print(f"Preferences: {profile['preferences']}")
        print(f"Description: {profile['description']}")
    
    # Test matching for first demo profile
    print(f"\n\n🔍 Testing matches for {demo_profiles[0]['name']}...")
    try:
        response = requests.get(f"{API_BASE}/match/{demo_profiles[0]['id']}?top_k=5")
        if response.status_code == 200:
            matches = response.json()
            print(f"\n✅ Top {matches['total_matches']} Matches:")
            for i, match in enumerate(matches['matches'], 1):
                score = match['score'] * 100
                print(f"\n  {i}. {match['name']} - {score:.1f}%")
                print(f"     Can help with: {match['strengths']}")
                print(f"     Needs help with: {match['weaknesses']}")
    except Exception as e:
        print(f"❌ Error testing matches: {e}")

if __name__ == "__main__":
    print("Starting database population...\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ Backend server is online!\n")
        else:
            print("⚠️  Backend server responded but with unexpected status")
    except Exception as e:
        print(f"❌ Backend server is not running!")
        print(f"   Please start it with: cd backend && python -m uvicorn main:app --reload")
        sys.exit(1)
    
    # Generate and populate profiles
    profiles = populate_database()
    
    # Select and display demo profiles
    select_demo_profiles(profiles)
    
    print("\n" + "=" * 70)
    print("✅ DATABASE POPULATED SUCCESSFULLY!")
    print("=" * 70)
    print("\n💡 Tips for your demo:")
    print("   1. Use the 3 demo profiles shown above")
    print("   2. Open frontend/index.html in browser")
    print("   3. Create a new profile using the demo data")
    print("   4. Watch as the system finds perfect matches!")
    print(f"\n📊 Total profiles in database: {len(profiles) + 6}")  # +6 for existing test profiles
