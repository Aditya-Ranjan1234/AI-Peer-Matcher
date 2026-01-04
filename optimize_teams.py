import os
from pymongo import MongoClient
import itertools
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "peer_matcher" 

TARGET_IDS = [
    "1RV23AI018", "1RV23AI054", "1RV23AI034", "1RV23CY028", 
    "1RV23CY019", "1RV23CS087", "1RV23CD019", "1RV23CY006", 
    "1RV23CY063", "1RV23AI050", "1RV23CD061", "1RV23CD055"
]

# --- Copied Logic from backend/matcher.py ---
def cosine_sim(vec1, vec2):
    vec1_np = np.array(vec1).reshape(1, -1)
    vec2_np = np.array(vec2).reshape(1, -1)
    if np.all(vec1_np == 0) or np.all(vec2_np == 0):
        return 0.0
    return float(cosine_similarity(vec1_np, vec2_np)[0][0])

def complementary_score(profile_a, profile_b):
    try:
        score_1 = cosine_sim(profile_a['strengths_emb'], profile_b['weaknesses_emb'])
        score_2 = cosine_sim(profile_b['strengths_emb'], profile_a['weaknesses_emb'])
        return max(0.0, min(1.0, (score_1 + score_2) / 2.0))
    except:
        return 0.0

def get_team_score(team_profiles):
    total_pair_score = 0.0
    pair_count = 0
    for p1, p2 in itertools.combinations(team_profiles, 2):
        total_pair_score += complementary_score(p1, p2)
        pair_count += 1
    return total_pair_score / pair_count if pair_count > 0 else 0.0

def main():
    print("Fetching profiles...")
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"Connected to {DB_NAME} at {MONGO_URL.split('@')[-1] if '@' in MONGO_URL else 'localhost'}")
    total = db.profiles.count_documents({})
    print(f"Total profiles in DB: {total}")
    
    profiles = list(db.profiles.find({"id": {"$in": TARGET_IDS}}))
    print(f"Found {len(profiles)} target profiles.")
    
    if len(profiles) != 12:
        print(f"Error: Expected 12 profiles, found {len(profiles)}. Wait for update_batch.py to finish.")
        return

    print("Optimizing teams (Brute Force)...")
    
    # Map ID to profile for easy access
    p_map = {p["id"]: p for p in profiles}
    ids = list(p_map.keys())
    
    best_total_score = -1.0
    best_partition = []
    
    # Canonical logic to reduce search space
    # Fix the first available person (ids[0]) into Team 1
    # Choose 3 others from remaining 11
    
    remaining_pool = ids[1:]
    
    count = 0
    
    for team1_others in itertools.combinations(remaining_pool, 3):
        team1_ids = [ids[0]] + list(team1_others)
        team1_score = get_team_score([p_map[pid] for pid in team1_ids])
        
        # Remaining pool for Team 2/3
        pool_2 = [pid for pid in remaining_pool if pid not in team1_others]
        
        # From remaining 8, fix pool_2[0] into Team 2
        pool_2_others = pool_2[1:]
        
        for team2_others in itertools.combinations(pool_2_others, 3):
            team2_ids = [pool_2[0]] + list(team2_others)
            team2_score = get_team_score([p_map[pid] for pid in team2_ids])
            
            # Remaining 4 are Team 3
            team3_ids = [pid for pid in pool_2_others if pid not in team2_others]
            team3_score = get_team_score([p_map[pid] for pid in team3_ids])
            
            total_score = team1_score + team2_score + team3_score
            
            if total_score > best_total_score:
                best_total_score = total_score
                best_partition = [team1_ids, team2_ids, team3_ids]
            
            count += 1
            if count % 100 == 0:
                print(f"Checked {count} combinations...")

    print(f"\n--- Best Partition Found (Total Score: {best_total_score:.4f}) ---")
    
    fixed_teams_map = {}
    
    for i, team in enumerate(best_partition):
        t_profiles = [p_map[pid] for pid in team]
        score = get_team_score(t_profiles)
        print(f"\nTeam {i+1} (Score: {score:.4f}):")
        for p in t_profiles:
            print(f"  - {p['id']}: {p['name']}")
            # Map this user to this specific team (for potential backend enforcement)
            fixed_teams_map[p['id']] = {
                "team_members": team,
                "score": score
            }
            
    # Write result to a file for backend to consume
    import json
    with open("fixed_teams.json", "w") as f:
        json.dump(fixed_teams_map, f, indent=2)
    print("\nSaved optimal teams to 'fixed_teams.json'")

if __name__ == "__main__":
    main()
