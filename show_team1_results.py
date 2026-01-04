import requests
import json

BASE_URL = "http://127.0.0.1:8000"

USERS = [
    {"id": "1RV23AI018", "name": "Anjali Suresh Kalarikkal", "pass": "1RVAn"},
    {"id": "1RV23CY028", "name": "Meda Mounika", "pass": "1RVMe"},
    {"id": "1RV23CS087", "name": "Eshitha Chowdary Nattem", "pass": "1RVEs"},
    {"id": "1RV23CD019", "name": "Shravani G L", "pass": "1RVSh"}
]

def show_outputs():
    print("Fetching 'Team of 4' outputs for the 4 individuals:\n")
    
    for user in USERS:
        print(f"--- Requesting as: {user['name']} ({user['id']}) ---")
        
        # We don't strictly need login for the matching endpoint as it's GET /match/team/{id} 
        # but let's do it to be safe if there's any session logic (actually the code doesn't require it for this endpoint)
        
        resp = requests.get(f"{BASE_URL}/match/team/{user['id']}")
        if resp.status_code == 200:
            data = resp.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"Error fetching for {user['id']}: {resp.text}")
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    show_outputs()
