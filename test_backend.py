"""
Test script to verify the backend API is working
"""
import requests
import json
import time
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_profiles():
    """Create test student profiles"""
    print("\n📝 Creating test student profiles...")
    
    profiles = [
        {
            "id": "stu001",
            "name": "Alice Johnson",
            "strengths": "Mathematics, Calculus, Algebra, Problem Solving, Physics",
            "weaknesses": "Literature, Essay Writing, History, Reading Comprehension",
            "preferences": "Evenings, small groups",
            "description": "I love solving complex math problems and prefer visual explanations"
        },
        {
            "id": "stu002",
            "name": "Bob Smith",
            "strengths": "English Literature, Writing, History, Reading Comprehension, Creative Writing",
            "weaknesses": "Mathematics, Calculus, Physics, Science",
            "preferences": "Afternoons, online sessions",
            "description": "I enjoy analyzing literature and helping others with essays"
        },
        {
            "id": "stu003",
            "name": "Carol Davis",
            "strengths": "Biology, Chemistry, Lab Work, Scientific Research",
            "weaknesses": "Computer Science, Programming, Algorithms",
            "preferences": "Mornings, any size group",
            "description": "Science enthusiast who loves hands-on experiments"
        },
        {
            "id": "stu004",
            "name": "David Lee",
            "strengths": "Computer Science, Programming, Algorithms, Web Development, Software Engineering",
            "weaknesses": "Biology, Chemistry, Organic Chemistry",
            "preferences": "Flexible schedule",
            "description": "Passionate programmer who loves teaching coding"
        },
        {
            "id": "stu005",
            "name": "Emma Wilson",
            "strengths": "Statistics, Data Analysis, Economics, Business",
            "weaknesses": "Literature, Creative Writing, Art History",
            "preferences": "Evenings, one-on-one",
            "description": "Data-driven learner who excels at quantitative analysis"
        }
    ]
    
    created = []
    for profile in profiles:
        try:
            response = requests.post(f"{API_BASE}/profiles", json=profile)
            if response.status_code == 201:
                print(f"✅ Created profile for {profile['name']}")
                created.append(profile['id'])
            else:
                print(f"⚠️  Failed to create {profile['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating {profile['name']}: {e}")
    
    return created

def test_get_matches(student_id, student_name):
    """Get matches for a student"""
    print(f"\n🔍 Finding matches for {student_name} (ID: {student_id})...")
    
    try:
        response = requests.get(f"{API_BASE}/match/{student_id}?top_k=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_matches']} matches:")
            
            for i, match in enumerate(data['matches'], 1):
                score_pct = match['score'] * 100
                print(f"\n   {i}. {match['name']} (ID: {match['student_id']})")
                print(f"      Match Score: {score_pct:.1f}%")
                print(f"      Their Strengths: {match['strengths']}")
                print(f"      They Need Help: {match['weaknesses']}")
            
            return data['matches']
        else:
            print(f"❌ Failed to get matches: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting matches: {e}")
        return []

def test_all_profiles():
    """Get all profiles"""
    print("\n📋 Getting all profiles...")
    
    try:
        response = requests.get(f"{API_BASE}/profiles")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total profiles: {data['total']}")
            return data['profiles']
        else:
            print(f"❌ Failed to get profiles: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting profiles: {e}")
        return []

def main():
    print("=" * 70)
    print("🎓 AI-Powered Peer Learning Matcher - Backend Test Suite")
    print("=" * 70)
    
    # Wait for server to be ready
    print("\n⏳ Waiting for server to be ready...")
    for i in range(10):
        if test_health():
            break
        time.sleep(2)
    else:
        print("\n❌ Server is not responding. Please make sure the backend is running:")
        print("   cd backend && python -m uvicorn main:app --reload")
        return
    
    # Create test profiles
    created_ids = test_create_profiles()
    
    if not created_ids:
        print("\n❌ No profiles were created. Cannot proceed with matching tests.")
        return
    
    # Get all profiles
    all_profiles = test_all_profiles()
    
    # Test matching for each student
    print("\n" + "=" * 70)
    print("🤝 TESTING MATCHING ALGORITHM")
    print("=" * 70)
    
    # Expected high match: Alice (Math) <-> Bob (Literature)
    print("\n📊 Test Case 1: Expected HIGH match (complementary skills)")
    test_get_matches("stu001", "Alice Johnson (Math expert)")
    
    # Expected high match: Carol (Biology) <-> David (CS)
    print("\n📊 Test Case 2: Expected HIGH match (complementary skills)")
    test_get_matches("stu003", "Carol Davis (Biology expert)")
    
    # Test for Bob
    print("\n📊 Test Case 3: Finding matches for Literature expert")
    test_get_matches("stu002", "Bob Smith (Literature expert)")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 70)
    print("\n💡 Key Observations:")
    print("   - Students with complementary skills should have scores > 50%")
    print("   - Alice (Math) and Bob (Literature) should be top matches for each other")
    print("   - Carol (Biology) and David (CS) should be good matches")
    print("\n🎉 Backend is working correctly if you see high match scores for complementary students!")

if __name__ == "__main__":
    main()
