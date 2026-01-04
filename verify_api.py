import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def verify():
    # 1. Login
    print("Logging in as 1RV23AI018...")
    resp = requests.post(f"{BASE_URL}/login", json={"id": "1RV23AI018", "password": "1RVAn"})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
    
    # 2. Get Team
    print("Requesting team match...")
    team_resp = requests.get(f"{BASE_URL}/match/team/1RV23AI018")
    
    if team_resp.status_code == 200:
        data = team_resp.json()
        print("\n--- Team Result ---")
        print(f"Target: {data['student_id']}")
        print(f"Team Score: {data['team_score']}")
        print("Members:")
        for m in data['team']:
            print(f"  - {m['student_id']}: {m['name']}")
            
        # Verify it matches expected fixed team
        expected_ids = ["1RV23AI018", "1RV23CY028", "1RV23CS087", "1RV23CD019"]
        actual_ids = [m['student_id'] for m in data['team']]
        
        if set(expected_ids) == set(actual_ids):
            print("\n[SUCCESS] Team matches expected fixed partition!")
        else:
            print(f"\n[FAIL] Team mismatch. Expected {expected_ids}, got {actual_ids}")
            
    else:
        print(f"Team request failed: {team_resp.text}")

if __name__ == "__main__":
    verify()
