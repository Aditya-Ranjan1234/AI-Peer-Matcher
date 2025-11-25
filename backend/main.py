"""
FastAPI Backend for AI-Powered Peer Learning Matcher
Provides REST API endpoints for student profile management and matching.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import logging

from models import ProfileInput, ProfileStored, MatchResult
from matcher import EmbeddingService, find_best_matches

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Peer Learning Matcher",
    description="Intelligent matchmaking system for pairing students with complementary skills",
    version="1.0.0"
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

# Initialize embedding service
embedding_service = EmbeddingService()

# In-memory storage for student profiles
profiles: Dict[str, Dict] = {}


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AI-Powered Peer Learning Matcher API",
        "total_profiles": len(profiles)
    }


@app.post("/profiles", status_code=201)
async def create_profile(profile: ProfileInput):
    """
    Create a new student profile with NLP embeddings
    
    Args:
        profile: Student profile data
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If profile ID already exists
    """
    if profile.id in profiles:
        raise HTTPException(
            status_code=400,
            detail=f"Profile with ID '{profile.id}' already exists"
        )
    
    logger.info(f"Creating profile for student: {profile.id}")
    
    # Generate embeddings for strengths and weaknesses
    try:
        strengths_emb = embedding_service.embed_text(profile.strengths)
        weaknesses_emb = embedding_service.embed_text(profile.weaknesses)
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate embeddings. Please try again."
        )
    
    # Store profile with embeddings
    profile_data = profile.model_dump()
    profile_data['strengths_emb'] = strengths_emb
    profile_data['weaknesses_emb'] = weaknesses_emb
    
    profiles[profile.id] = profile_data
    
    logger.info(f"Profile created successfully for {profile.id}")
    
    return {
        "message": "Profile created successfully",
        "student_id": profile.id,
        "name": profile.name
    }


@app.get("/profiles")
async def get_all_profiles():
    """
    Get all student profiles (without embeddings for cleaner response)
    
    Returns:
        List of all student profiles
    """
    # Return profiles without embedding vectors for cleaner output
    clean_profiles = []
    for pid, profile in profiles.items():
        clean_profile = {
            "id": profile["id"],
            "name": profile["name"],
            "strengths": profile["strengths"],
            "weaknesses": profile["weaknesses"],
            "preferences": profile.get("preferences", ""),
            "description": profile.get("description", "")
        }
        clean_profiles.append(clean_profile)
    
    return {
        "total": len(clean_profiles),
        "profiles": clean_profiles
    }


@app.get("/match/{student_id}")
async def get_matches(student_id: str, top_k: int = 3):
    """
    Find the best matching peers for a student
    
    Args:
        student_id: ID of the student to find matches for
        top_k: Number of top matches to return (default: 3)
        
    Returns:
        List of best matching students with scores
        
    Raises:
        HTTPException: If student ID not found or no other profiles exist
    """
    if student_id not in profiles:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found"
        )
    
    if len(profiles) < 2:
        raise HTTPException(
            status_code=400,
            detail="Not enough profiles to generate matches. Need at least 2 profiles."
        )
    
    logger.info(f"Finding matches for student: {student_id}")
    
    # Find best matches
    matches = find_best_matches(student_id, profiles, top_k)
    
    # Format response
    match_results = []
    for match in matches:
        match_results.append(MatchResult(
            student_id=match[0],
            name=match[1],
            score=round(match[2], 4),
            strengths=match[3],
            weaknesses=match[4]
        ))
    
    target_student = profiles[student_id]
    
    return {
        "student_id": student_id,
        "student_name": target_student["name"],
        "total_matches": len(match_results),
        "matches": [m.model_dump() for m in match_results]
    }


@app.delete("/profiles/{student_id}")
async def delete_profile(student_id: str):
    """
    Delete a student profile
    
    Args:
        student_id: ID of the student to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If student ID not found
    """
    if student_id not in profiles:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID '{student_id}' not found"
        )
    
    del profiles[student_id]
    logger.info(f"Profile deleted: {student_id}")
    
    return {
        "message": "Profile deleted successfully",
        "student_id": student_id
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
