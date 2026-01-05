import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"

def test_kg_scores():
    # Login as Anjali to check matches
    login_data = {"id": "1RV23AI018", "password": "1RVAn"}
    resp = requests.post(f"{BASE_URL}/login", json=login_data)
    token = resp.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Checking Peer Matches for 1RV23AI018...")
    resp = requests.get(f"{BASE_URL}/match/1RV23AI018?top_k=3", headers=headers)
    matches = resp.json()["matches"]
    for m in matches:
        print(f"Match: {m['name']}, AI: {m['score']}, Graph: {m['graph_score']}")
        assert "graph_score" in m
    
    print("\nChecking Projects...")
    resp = requests.get(f"{BASE_URL}/projects", headers=headers)
    projects = resp.json()["projects"]
    for p in projects[:3]:
        print(f"Project: {p['title']}, AI: {p['relevance_score']}, Graph: {p['graph_score']}")
        assert "graph_score" in p

if __name__ == "__main__":
    try:
        test_kg_scores()
        print("\n[SUCCESS] KG scores verified in API responses!")
    except Exception as e:
        print(f"\n[FAIL] {e}")
