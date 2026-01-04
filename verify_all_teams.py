import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

# Define expected teams by ID
TEAMS = {
    "Team 1": {"ids": ["1RV23AI018", "1RV23CY028", "1RV23CS087", "1RV23CD019"]},
    "Team 2": {"ids": ["1RV23AI054", "1RV23CY019", "1RV23CY063", "1RV23AI050"]},
    "Team 3": {"ids": ["1RV23AI034", "1RV23CY006", "1RV23CD061", "1RV23CD055"]}
}

# User Passwords from update_batch.py
PASSWORDS = {
    "1RV23AI018": "1RVAn",
    "1RV23AI054": "1RVMa",
    "1RV23AI034": "1RVGa",
    "1RV23CY028": "1RVMe",
    "1RV23CY019": "1RVEs",
    "1RV23CS087": "1RVEs",
    "1RV23CD019": "1RVSh",
    "1RV23CY006": "1RVAk",
    "1RV23CY063": "1RVYa",
    "1RV23AI050": "1RVMa",
    "1RV23CD061": "1RVYa",
    "1RV23CD055": "1RVSi"
}

def verify_all():
    print("Verifying strict team assignments for ALL 12 users...\n")
    
    all_passed = True
    
    for team_name, data in TEAMS.items():
        print(f"Checking {team_name} members: {data['ids']}")
        members = data['ids']
        
        for user_id in members:
            # Login
            password = PASSWORDS.get(user_id, "12345678")
            resp = requests.post(f"{BASE_URL}/login", json={"id": user_id, "password": password})
            if resp.status_code != 200:
                print(f"  [FAIL] Login failed for {user_id}")
                all_passed = False
                continue
                
            # Get Team
            team_resp = requests.get(f"{BASE_URL}/match/team/{user_id}")
            if team_resp.status_code != 200:
                print(f"  [FAIL] Team fetch failed for {user_id}")
                all_passed = False
                continue
            
            result = team_resp.json()
            returned_team_ids = [m['student_id'] for m in result['team']]
            
            # Check if returned IDs match expected team IDs (set comparison)
            if set(returned_team_ids) == set(members):
                print(f"  [PASS] {user_id} -> got correct team")
            else:
                print(f"  [FAIL] {user_id} -> MISMATCH! Got: {returned_team_ids}")
                all_passed = False
        print("-" * 40)

    if all_passed:
        print("\n[SUCCESS] All 12 users received their exact expected team combinations.")
    else:
        print("\n[FAILURE] Some users got incorrect teams.")

if __name__ == "__main__":
    verify_all()
