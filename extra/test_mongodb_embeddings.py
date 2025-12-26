"""
Test script to verify MongoDB embedding storage and retrieval.
This script tests that embeddings are properly stored as lists and retrieved correctly.
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed")

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from matcher import EmbeddingService


async def test_embedding_storage():
    """Test that embeddings can be stored and retrieved from MongoDB"""
    
    print("=" * 60)
    print("MongoDB Embedding Storage Test")
    print("=" * 60)
    
    # Get MongoDB URL
    MONGODB_URL = os.getenv("MONGODB_URL")
    if not MONGODB_URL:
        print("❌ ERROR: MONGODB_URL environment variable not set!")
        return False
    
    print(f"✅ MongoDB URL found: {MONGODB_URL[:30]}...")
    
    # Connect to MongoDB
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client["peer_matcher"]
        collection = db["test_embeddings"]
        print("✅ Connected to MongoDB successfully")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False
    
    # Clear test collection
    await collection.delete_many({})
    print("✅ Cleared test collection")
    
    # Initialize embedding service
    print("\n📊 Testing Embedding Generation...")
    embedding_service = EmbeddingService()
    
    # Generate test embeddings
    test_strength = "Python, Machine Learning, Data Analysis"
    test_weakness = "Web Development, Frontend, CSS"
    
    strengths_emb = embedding_service.embed_text(test_strength)
    weaknesses_emb = embedding_service.embed_text(test_weakness)
    
    print(f"  - Strength embedding type: {type(strengths_emb)}")
    print(f"  - Strength embedding length: {len(strengths_emb)}")
    print(f"  - Weakness embedding type: {type(weaknesses_emb)}")
    print(f"  - Weakness embedding length: {len(weaknesses_emb)}")
    
    # Verify embeddings are lists
    if not isinstance(strengths_emb, list):
        print(f"❌ ERROR: Strength embedding is {type(strengths_emb)}, expected list")
        return False
    if not isinstance(weaknesses_emb, list):
        print(f"❌ ERROR: Weakness embedding is {type(weaknesses_emb)}, expected list")
        return False
    
    print("✅ Embeddings generated as lists")
    
    # Store test profile in MongoDB
    print("\n💾 Testing MongoDB Storage...")
    test_profile = {
        "id": "TEST123",
        "name": "Test Student",
        "strengths": test_strength,
        "weaknesses": test_weakness,
        "strengths_emb": strengths_emb,
        "weaknesses_emb": weaknesses_emb,
    }
    
    try:
        result = await collection.insert_one(test_profile)
        print(f"✅ Profile stored with ID: {result.inserted_id}")
    except Exception as e:
        print(f"❌ Failed to store profile: {e}")
        return False
    
    # Retrieve and verify
    print("\n🔍 Testing MongoDB Retrieval...")
    retrieved = await collection.find_one({"id": "TEST123"})
    
    if not retrieved:
        print("❌ ERROR: Failed to retrieve profile from MongoDB")
        return False
    
    print("✅ Profile retrieved successfully")
    
    # Check embedding fields exist
    if "strengths_emb" not in retrieved:
        print("❌ ERROR: strengths_emb field missing from retrieved profile")
        return False
    if "weaknesses_emb" not in retrieved:
        print("❌ ERROR: weaknesses_emb field missing from retrieved profile")
        return False
    
    print("✅ All embedding fields present")
    
    # Check embedding types and lengths
    retrieved_strengths = retrieved["strengths_emb"]
    retrieved_weaknesses = retrieved["weaknesses_emb"]
    
    print(f"  - Retrieved strength embedding type: {type(retrieved_strengths)}")
    print(f"  - Retrieved strength embedding length: {len(retrieved_strengths)}")
    print(f"  - Retrieved weakness embedding type: {type(retrieved_weaknesses)}")
    print(f"  - Retrieved weakness embedding length: {len(retrieved_weaknesses)}")
    
    # Verify they're still lists
    if not isinstance(retrieved_strengths, list):
        print(f"❌ ERROR: Retrieved strength embedding is {type(retrieved_strengths)}, expected list")
        return False
    if not isinstance(retrieved_weaknesses, list):
        print(f"❌ ERROR: Retrieved weakness embedding is {type(retrieved_weaknesses)}, expected list")
        return False
    
    # Verify lengths match
    if len(retrieved_strengths) != len(strengths_emb):
        print(f"❌ ERROR: Strength embedding length mismatch: stored {len(strengths_emb)}, retrieved {len(retrieved_strengths)}")
        return False
    if len(retrieved_weaknesses) != len(weaknesses_emb):
        print(f"❌ ERROR: Weakness embedding length mismatch: stored {len(weaknesses_emb)}, retrieved {len(retrieved_weaknesses)}")
        return False
    
    print("✅ Embeddings retrieved correctly as lists with correct lengths")
    
    # Clean up
    await collection.delete_many({})
    print("\n🧹 Cleaned up test data")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nMongoDB is correctly storing and retrieving embeddings as lists.")
    print("The backend should now work properly with the fixes applied.")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_embedding_storage())
    sys.exit(0 if success else 1)
