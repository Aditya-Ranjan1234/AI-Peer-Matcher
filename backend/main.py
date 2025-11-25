"""FastAPI Backend for AI-Powered Peer Learning Matcher with MongoDB persistence.

All profile data is stored in a MongoDB Atlas collection named ``profiles``.
The async Motor driver is used via the ``backend.database`` helper.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging

from models import ProfileInput, MatchResult
from matcher import EmbeddingService, find_best_matches
from .database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Peer Learning Matcher",
    description="Intelligent matchmaking system for pairing students with complementary skills",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-peer-matcher.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embedding service (still in‑memory, no DB needed)
embedding_service = EmbeddingService()

# Helper to get the MongoDB collection used for profiles
def get_profiles_collection(db=Depends(get_db)):
    return db["profiles"]

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/")
async def root(db=Depends(get_db)):
    """Health check endpoint – returns basic status and total profile count."""
    total = await db["profiles"].count_documents({})
    return {
        "status": "online",
        "message": "AI-Powered Peer Learning Matcher API",
        "total_profiles": total,
    }

# ---------------------------------------------------------------------------
# Create a new profile
# ---------------------------------------------------------------------------
@app.post("/profiles", status_code=201)
async def create_profile(
    profile: ProfileInput,
    collection = Depends(get_profiles_collection),
):
    """Create a new student profile with NLP embeddings and store it in MongoDB."""
    # Check for duplicate ID
    existing = await collection.find_one({"id": profile.id})
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Profile with ID '{profile.id}' already exists",
        )

    logger.info(f"Creating profile for student: {profile.id}")

    # Generate embeddings
    try:
        strengths_emb = embedding_service.embed_text(profile.strengths)
        weaknesses_emb = embedding_service.embed_text(profile.weaknesses)
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate embeddings. Please try again.",
        )

    # Prepare document for MongoDB
    profile_data = profile.model_dump()
    profile_data["strengths_emb"] = strengths_emb
    profile_data["weaknesses_emb"] = weaknesses_emb

    await collection.insert_one(profile_data)
    logger.info(f"Profile created successfully for {profile.id}")

    return {
        "message": "Profile created successfully",
        "student_id": profile.id,
        "name": profile.name,
    }

# ---------------------------------------------------------------------------
# Retrieve all profiles (without embedding vectors)
# ---------------------------------------------------------------------------
@app.get("/profiles")
async def get_all_profiles(collection = Depends(get_profiles_collection)):
    """Return a list of all stored profiles, omitting heavy embedding fields."""
    cursor = collection.find(
        {},
        {"strengths_emb": 0, "weaknesses_emb": 0},
    )
    clean_profiles: List[dict] = []
    async for doc in cursor:
        clean_profiles.append({
            "id": doc["id"],
            "name": doc["name"],
            "strengths": doc["strengths"],
            "weaknesses": doc["weaknesses"],
            "preferences": doc.get("preferences", ""),
            "description": doc.get("description", ""),
        })
    return {"total": len(clean_profiles), "profiles": clean_profiles}

# ---------------------------------------------------------------------------
# Find matches for a given student
# ---------------------------------------------------------------------------
@app.get("/match/{student_id}")
async def get_matches(
    student_id: str,
    top_k: int = 3,
    collection = Depends(get_profiles_collection),
):
    """Find the best matching peers for a student using the complementary scoring algorithm."""
    target = await collection.find_one({"id": student_id})
    if not target:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found",
        )

    # Need at least two profiles to match
    total_profiles = await collection.count_documents({})
    if total_profiles < 2:
        raise HTTPException(
            status_code=400,
            detail="Not enough profiles to generate matches. Need at least 2 profiles.",
        )

    logger.info(f"Finding matches for student: {student_id}")

    # Load all profiles into a dict compatible with the existing matcher utility
    all_docs = await collection.find().to_list(length=None)
    profiles_dict = {doc["id"]: doc for doc in all_docs}

    matches = find_best_matches(student_id, profiles_dict, top_k)

    match_results = []
    for match in matches:
        match_results.append(
            MatchResult(
                student_id=match[0],
                name=match[1],
                score=round(match[2], 4),
                strengths=match[3],
                weaknesses=match[4],
            )
        )

    return {
        "student_id": student_id,
        "student_name": target["name"],
        "total_matches": len(match_results),
        "matches": [m.model_dump() for m in match_results],
    }

# ---------------------------------------------------------------------------
# Delete a profile
# ---------------------------------------------------------------------------
@app.delete("/profiles/{student_id}")
async def delete_profile(student_id: str, collection = Depends(get_profiles_collection)):
    """Delete a student profile from MongoDB."""
    result = await collection.delete_one({"id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found",
        )
    logger.info(f"Profile deleted: {student_id}")
    return {"message": "Profile deleted successfully", "student_id": student_id}

# ---------------------------------------------------------------------------
# Run with uvicorn when executed directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
