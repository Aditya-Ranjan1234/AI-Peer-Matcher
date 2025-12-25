from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from datetime import datetime
import uuid

from models import (
    ProfileInput, MatchResult, TeamResult, 
    UserAuth, UserInDB, Project, ProjectCreate, Comment, ProjectWithScore
)
from matcher import (
    EmbeddingService, find_best_matches, 
    find_team_of_4, calculate_project_relevance
)
from database import get_db
from auth import (
    get_password_hash, verify_password, create_access_token, 
    get_current_user_id
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Peer Learning & Project Matcher",
    description="Intelligent matchmaking system for pairing students and finding projects",
    version="2.0.0",
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

# --- DB HELPERS ---
def get_profiles_collection(db=Depends(get_db)):
    return db["profiles"]

def get_users_collection(db=Depends(get_db)):
    return db["users"]

def get_projects_collection(db=Depends(get_db)):
    return db["projects"]


# ---------------------------------------------------------------------------
# Health check & Identity
# ---------------------------------------------------------------------------
@app.get("/")
async def root(db=Depends(get_db)):
    total = await db["profiles"].count_documents({})
    return {
        "status": "online",
        "message": "AI Peer Matcher & Project Hub API",
        "total_profiles": total,
    }

@app.get("/check-id/{student_id}")
async def check_id(student_id: str, profiles = Depends(get_profiles_collection)):
    """Check if a student ID exists for redirection"""
    profile = await profiles.find_one({"id": student_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Student ID not found")
    return {"exists": True, "name": profile["name"]}


# ---------------------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------------------
@app.post("/signup")
async def signup(
    user_data: UserAuth, 
    users = Depends(get_users_collection),
    profiles = Depends(get_profiles_collection)
):
    # 1. Check if profile exists (must be a student in the system)
    logger.info(f"Signup attempt for USN: '{user_data.id}'")
    profile = await profiles.find_one({"id": user_data.id})
    if not profile:
        logger.warning(f"Profile not found for USN: '{user_data.id}' during signup")
        # Try a case-insensitive check just in case
        profile_case = await profiles.find_one({"id": {"$regex": f"^{user_data.id}$", "$options": "i"}})
        if profile_case:
            logger.info(f"Found profile with case-insensitive match: {profile_case['id']}")
            user_data.id = profile_case["id"] # Sync the ID
        else:
            raise HTTPException(status_code=404, detail=f"Student ID '{user_data.id}' not found in records.")
    
    # 2. Check if already registered
    existing_user = await users.find_one({"id": user_data.id})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered. Please login.")
    
    # 3. Create user
    hashed_pw = get_password_hash(user_data.password)
    new_user = {"id": user_data.id, "hashed_password": hashed_pw}
    await users.insert_one(new_user)
    
    return {"message": "Registration successful"}

@app.post("/login")
async def login(user_data: UserAuth, users = Depends(get_users_collection)):
    user = await users.find_one({"id": user_data.id})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------------------------------------------------------
# PROFILES
# ---------------------------------------------------------------------------
@app.post("/profiles", status_code=201)
async def create_profile(
    profile: ProfileInput,
    collection = Depends(get_profiles_collection),
):
    existing = await collection.find_one({"id": profile.id})
    if existing:
        raise HTTPException(status_code=400, detail=f"Profile '{profile.id}' already exists")

    # Generate embeddings
    strengths_emb = embedding_service.embed_text(profile.strengths)
    weaknesses_emb = embedding_service.embed_text(profile.weaknesses)
    
    profile_data = profile.model_dump()
    profile_data["strengths_emb"] = list(strengths_emb)
    profile_data["weaknesses_emb"] = list(weaknesses_emb)
    
    await collection.insert_one(profile_data)
    logger.info(f"Successfully SAVED profile to DB with USN: '{profile.id}'")
    return {"message": "Profile created", "student_id": profile.id}

@app.get("/profiles")
async def get_all_profiles(collection = Depends(get_profiles_collection)):
    cursor = collection.find({}, {"strengths_emb": 0, "weaknesses_emb": 0})
    profiles = []
    async for doc in cursor:
        doc.pop("_id", None)
        profiles.append(doc)
    return {"total": len(profiles), "profiles": profiles}


# ---------------------------------------------------------------------------
# MATCHING (PEERS & TEAMS)
# ---------------------------------------------------------------------------
@app.get("/match/{student_id}")
async def get_matches(
    student_id: str,
    top_k: int = 3,
    collection = Depends(get_profiles_collection),
):
    target = await collection.find_one({"id": student_id})
    if not target:
        raise HTTPException(status_code=404, detail="Student not found")

    all_docs = await collection.find().to_list(length=None)
    profiles_dict = {doc["id"]: doc for doc in all_docs if "strengths_emb" in doc}
    
    if student_id not in profiles_dict:
         raise HTTPException(status_code=500, detail="Profile missing valid embeddings.")

    matches = find_best_matches(student_id, profiles_dict, top_k)
    return {
        "student_id": student_id,
        "student_name": target["name"],
        "matches": [
            {"student_id": m[0], "name": m[1], "score": round(m[2], 4), "strengths": m[3], "weaknesses": m[4]} 
            for m in matches
        ]
    }

@app.get("/match/team/{student_id}")
async def get_team_matches(
    student_id: str,
    collection = Depends(get_profiles_collection),
):
    """Form a complementary team of 4"""
    target = await collection.find_one({"id": student_id})
    if not target:
        raise HTTPException(status_code=404, detail="Student not found")

    all_docs = await collection.find().to_list(length=None)
    profiles_dict = {doc["id"]: doc for doc in all_docs if "strengths_emb" in doc}
    
    team_members, score = find_team_of_4(student_id, profiles_dict)
    return {
        "student_id": student_id,
        "team_score": round(score, 4),
        "team": team_members
    }


# ---------------------------------------------------------------------------
# PROJECTS HUB
# ---------------------------------------------------------------------------
@app.post("/projects")
async def create_project(
    project_in: ProjectCreate,
    user_id: str = Depends(get_current_user_id),
    projects = Depends(get_projects_collection),
    profiles = Depends(get_profiles_collection)
):
    user_profile = await profiles.find_one({"id": user_id})
    
    # Generate embedding for project description + stack to help matching
    combined_text = f"{project_in.description} {project_in.stack}"
    desc_emb = embedding_service.embed_text(combined_text)
    
    project_doc = {
        "id": str(uuid.uuid4()),
        "creator_id": user_id,
        "creator_name": user_profile["name"],
        "title": project_in.title,
        "description": project_in.description,
        "stack": project_in.stack,
        "votes": 0,
        "voted_by": [],
        "comments": [],
        "created_at": datetime.utcnow(),
        "description_emb": list(desc_emb)
    }
    
    await projects.insert_one(project_doc)
    return {"message": "Project posted", "project_id": project_doc["id"]}

@app.get("/projects")
async def list_projects(
    user_id: Optional[str] = None, # Optional user ID for relevance scoring
    projects = Depends(get_projects_collection),
    profiles = Depends(get_profiles_collection)
):
    cursor = projects.find().sort("votes", -1)
    results = []
    
    user_profile = None
    if user_id:
        user_profile = await profiles.find_one({"id": user_id})
        
    async for doc in cursor:
        doc.pop("_id", None)
        
        # Calculate relevance score if user is logged in
        relevance = 0.0
        if user_profile and "strengths_emb" in user_profile and "description_emb" in doc:
            relevance = calculate_project_relevance(
                user_profile["strengths_emb"], 
                doc["description_emb"]
            )
        
        doc["relevance_score"] = round(relevance, 4)
        results.append(doc)
        
    return {"total": len(results), "projects": results}

@app.post("/projects/{project_id}/vote")
async def vote_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    projects = Depends(get_projects_collection)
):
    project = await projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if user_id in project.get("voted_by", []):
        # Remove vote (toggle)
        await projects.update_one(
            {"id": project_id},
            {"$inc": {"votes": -1}, "$pull": {"voted_by": user_id}}
        )
        return {"message": "Vote removed"}
    else:
        # Add vote
        await projects.update_one(
            {"id": project_id},
            {"$inc": {"votes": 1}, "$push": {"voted_by": user_id}}
        )
        return {"message": "Voted success"}

@app.post("/projects/{project_id}/comment")
async def comment_project(
    project_id: str,
    comment_text: str, # Simple string for now
    user_id: str = Depends(get_current_user_id),
    projects = Depends(get_projects_collection),
    profiles = Depends(get_profiles_collection)
):
    user_profile = await profiles.find_one({"id": user_id})
    comment = {
        "user_id": user_id,
        "user_name": user_profile["name"],
        "text": comment_text,
        "timestamp": datetime.utcnow()
    }
    
    await projects.update_one(
        {"id": project_id},
        {"$push": {"comments": comment}}
    )
    return {"message": "Comment added"}

# ---------------------------------------------------------------------------
# Delete a profile
# ---------------------------------------------------------------------------
@app.delete("/profiles/{student_id}")
async def delete_profile(student_id: str, collection = Depends(get_profiles_collection)):
    """Delete a student profile from MongoDB."""
    result = await collection.delete_one({"id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Profile deleted", "student_id": student_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
