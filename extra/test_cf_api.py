"""
Simple test script to verify collaborative filtering API endpoints work correctly
Run the backend server first, then run this script
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test basic health check"""
    print("\n🏥 Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200

def test_match_endpoint_without_cf():
    """Test match endpoint with CF disabled"""
    print("\n🔍 Testing match endpoint (CF disabled)...")
    try:
        response = requests.get(f"{BASE_URL}/match/stu001?use_cf=false")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Using CF: {data.get('using_collaborative_filtering', 'N/A')}")
        print(f"   Total collaborations: {data.get('total_collaborations', 0)}")
        if data.get('matches'):
            first_match = data['matches'][0]
            print(f"   First match: {first_match['name']}")
            print(f"      - Hybrid: {first_match.get('hybrid_score', 0):.3f}")
            print(f"      - NLP: {first_match.get('nlp_score', 0):.3f}")
            print(f"      - CF: {first_match.get('cf_score', 0):.3f}")
            print(f"      - Graph: {first_match.get('graph_score', 0):.3f}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_match_endpoint_with_cf():
    """Test match endpoint with CF enabled"""
    print("\n🤖 Testing match endpoint (CF enabled)...")
    try:
        response = requests.get(f"{BASE_URL}/match/stu001?use_cf=true")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Using CF: {data.get('using_collaborative_filtering', 'N/A')}")
        print(f"   Total collaborations: {data.get('total_collaborations', 0)}")
        if data.get('matches'):
            first_match = data['matches'][0]
            print(f"   First match: {first_match['name']}")
            print(f"      - Hybrid: {first_match.get('hybrid_score', 0):.3f}")
            print(f"      - NLP: {first_match.get('nlp_score', 0):.3f}")
            print(f"      - CF: {first_match.get('cf_score', 0):.3f}")
            print(f"      - Graph: {first_match.get('graph_score', 0):.3f}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("  Collaborative Filtering API Tests")
    print("=" * 60)
    print("\n⚠️  Make sure the backend server is running on port 8000!")
    print("   Start it with: python -m uvicorn main:app --reload")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Match without CF", test_match_endpoint_without_cf()))
    results.append(("Match with CF", test_match_endpoint_with_cf()))
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Results Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    print(f"\n  Total: {total_passed}/{total_tests} tests passed")
    print("=" * 60)

if __name__ == "__main__":
    main()
