"""create_random_profiles.py
Generates 100 random student profiles and writes them to ``random_profiles.json``.

Run it with:
    python demo/create_random_profiles.py

The script uses ``faker`` to generate realistic names and descriptions.
"""

import json
from faker import Faker
import random

fake = Faker()

STRENGTHS = [
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Computer Science",
    "Programming",
    "English Literature",
    "Creative Writing",
    "History",
    "Economics",
    "Statistics",
    "Art",
    "Music",
    "Philosophy",
    "Sociology",
]

WEAKNESSES = STRENGTHS  # reuse same pool for simplicity

PREFERENCES = [
    "Morning sessions",
    "Evening sessions",
    "Weekend study",
    "Online sessions",
    "In-person meetings",
    "Small groups",
    "One-on-one",
]

def random_subset(pool, min_n=2, max_n=5):
    n = random.randint(min_n, max_n)
    return random.sample(pool, n)

profiles = []
for i in range(1, 101):
    profile = {
        "id": f"RND{i:03d}",
        "name": fake.name(),
        "strengths": random_subset(STRENGTHS),
        "weaknesses": random_subset(WEAKNESSES),
        "preferences": random_subset(PREFERENCES, min_n=1, max_n=3),
        "description": fake.sentence(nb_words=12),
    }
    profiles.append(profile)

with open("demo/random_profiles.json", "w", encoding="utf-8") as f:
    json.dump(profiles, f, indent=2, ensure_ascii=False)

print("✅ Generated 100 random profiles to demo/random_profiles.json")
