"""
Seed script to populate the database with sample collaboration ratings
for testing the collaborative filtering feature.
"""

import asyncio
import os
import sys
import random
from datetime import datetime, timedelta

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.database import get_db
from motor.motor_asyncio import AsyncIOMotorClient


async def seed_collaborations():
    """Generate sample collaboration ratings between students"""
    
    # Get database
    db = get_db()
    profiles_col = db["profiles"]
    collaborations_col = db["collaborations"]
    
    # Get all student IDs
    cursor = profiles_col.find({}, {"id": 1})
    students = await cursor.to_list(length=None)
    student_ids = [s["id"] for s in students]
    
    if len(student_ids) < 2:
        print("❌ Need at least 2 students in the database to create collaborations")
        return
    
    print(f"📊 Found {len(student_ids)} students")
    
    # Clear existing collaborations
    result = await collaborations_col.delete_many({})
    print(f"🗑️  Cleared {result.deleted_count} existing collaborations")
    
    # Generate realistic collaboration patterns
    collaborations_to_insert = []
    
    # Pattern 1: High performers (stu001-stu020) rate each other highly
    high_performers = [sid for sid in student_ids if sid.startswith("stu0") and int(sid[3:]) <= 20]
    for i, student_a in enumerate(high_performers):
        # Each rates 3-5 others
        num_ratings = random.randint(3, min(5, len(high_performers) - 1))
        rated_students = random.sample([s for s in high_performers if s != student_a], num_ratings)
        
        for student_b in rated_students:
            rating = random.uniform(3.5, 5.0)  # High ratings
            collaborations_to_insert.append({
                "id": f"collab_{len(collaborations_to_insert)}",
                "student_a": student_a,
                "student_b": student_b,
                "rating": round(rating, 1),
                "worked_together": True,
                "feedback": random.choice([
                    "Great teammate, very collaborative",
                    "Excellent problem solver",
                    "Very helpful and patient",
                    "Strong technical skills",
                    None
                ]),
                "project_context": random.choice([
                    "Machine Learning Project",
                    "Web Development",
                    "Data Science Assignment",
                    None
                ]),
                "timestamp": datetime.utcnow() - timedelta(days=random.randint(1, 90))
            })
    
    # Pattern 2: Mid-tier students (stu021-stu060) mixed ratings
    mid_tier = [sid for sid in student_ids if sid.startswith("stu0") and 20 < int(sid[3:]) <= 60]
    for student_a in random.sample(mid_tier, min(30, len(mid_tier))):
        num_ratings = random.randint(2, 4)
        rated_students = random.sample([s for s in student_ids if s != student_a], num_ratings)
        
        for student_b in rated_students:
            rating = random.uniform(2.5, 4.5)  # Mixed ratings
            collaborations_to_insert.append({
                "id": f"collab_{len(collaborations_to_insert)}",
                "student_a": student_a,
                "student_b": student_b,
                "rating": round(rating, 1),
                "worked_together": True,
                "feedback": random.choice([
                    "Good work",
                    "Could improve communication",
                    "Decent collaboration",
                    None
                ]),
                "project_context": random.choice([
                    "Group Project",
                    "Hackathon",
                    None
                ]),
                "timestamp": datetime.utcnow() - timedelta(days=random.randint(1, 60))
            })
    
    # Pattern 3: Random cross-ratings
    for _ in range(50):
        student_a, student_b = random.sample(student_ids, 2)
        rating = random.uniform(2.0, 5.0)
        collaborations_to_insert.append({
            "id": f"collab_{len(collaborations_to_insert)}",
            "student_a": student_a,
            "student_b": student_b,
            "rating": round(rating, 1),
            "worked_together": True,
            "feedback": None,
            "project_context": None,
            "timestamp": datetime.utcnow() - timedelta(days=random.randint(1, 30))
        })
    
    # Insert all collaborations
    if collaborations_to_insert:
        await collaborations_col.insert_many(collaborations_to_insert)
        print(f"✅ Created {len(collaborations_to_insert)} collaboration ratings")
        
        # Show some statistics
        total_ratings = len(collaborations_to_insert)
        avg_rating = sum(c['rating'] for c in collaborations_to_insert) / total_ratings
        high_ratings = sum(1 for c in collaborations_to_insert if c['rating'] >= 4.0)
        
        print(f"📈 Statistics:")
        print(f"   - Total ratings: {total_ratings}")
        print(f"   - Average rating: {avg_rating:.2f}/5.0")
        print(f"   - High ratings (≥4.0): {high_ratings} ({high_ratings/total_ratings*100:.1f}%)")
    else:
        print("❌ No collaborations generated")


async def main():
    print("🌱 Seeding collaboration data...\n")
    try:
        await seed_collaborations()
        print("\n✨ Seeding complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
