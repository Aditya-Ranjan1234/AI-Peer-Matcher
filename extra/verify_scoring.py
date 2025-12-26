import requests

BASE_URL = "http://localhost:8000"
USN = "1RV23CS001" # A seeded user
PASSWORD = "12345678"

def verify():
    # 1. Login
    print(f"Logging in as {USN}...")
    try:
        resp = requests.post(f"{BASE_URL}/login", json={"id": USN, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        token = resp.json()["access_token"]
        print("Login successful.")
        
        # 2. Get Projects
        print("Fetching projects...")
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/projects", headers=headers)
        
        if resp.status_code != 200:
            print(f"Get projects failed: {resp.text}")
            return
            
        data = resp.json()
        projects = data.get("projects", [])
        print(f"Found {len(projects)} projects.")
        
        for p in projects:
            score = p.get("relevance_score")
            creator = p.get("creator_id")
            title = p.get("title")
            print(f"Project: {title[:20]}... | Creator: {creator} | Score: {score}")
            
            if creator != USN and score is not None:
                print("  -> PASSED: Score present for non-owner.")
            elif creator == USN and (score is None or score == 0):
                print("  -> PASSED: No score for owner.")
            else:
                 # It's possible score is 0 if no match, so just checking presence usually
                 print(f"  -> CHECK: {title} Score={score}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
