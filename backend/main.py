from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from datetime import datetime
import uuid

from models import (
    ProfileInput, MatchResult, TeamResult, 
    UserAuth, UserInDB, Project, ProjectCreate, Comment, ProjectWithScore,
    PasswordChange, CollaborationRating, TeamFeedback, CollaborationStats
)
from matcher import (
    EmbeddingService, find_best_matches, 
    find_team_of_4, calculate_project_relevance
)
from database import get_db
from auth import (
    get_password_hash, verify_password, create_access_token, 
    get_current_user_id, get_current_user_optional
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

def get_collaborations_collection(db=Depends(get_db)):
    return db["collaborations"]

def get_team_history_collection(db=Depends(get_db)):
    return db["team_history"]


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
    user_data: UserAuth,  # Now accepts UserAuth which has id, name, etc.
    users = Depends(get_users_collection),
    profiles = Depends(get_profiles_collection)
):
    # 1. Check/Create Profile
    profile = await profiles.find_one({"id": user_data.id})
    
    if not profile:
        # If we have extra fields (from seeding), create the profile
        print(f"DEBUG: Processing signup for {user_data.id}. hasattr(name)={hasattr(user_data, 'name')}, name={getattr(user_data, 'name', 'N/A')}")
        if hasattr(user_data, 'name') and user_data.name:  
             # Generate embeddings for new profile
            service = EmbeddingService()
            strengths_emb = service.embed_text(user_data.strengths or "")
            weaknesses_emb = service.embed_text(user_data.weaknesses or "")
            
            new_profile = {
                "id": user_data.id,
                "name": user_data.name,
                "strengths": user_data.strengths or "",
                "weaknesses": user_data.weaknesses or "",
                "preferences": user_data.preferences or "",
                "description": user_data.description or "",
                "strengths_emb": strengths_emb,
                "weaknesses_emb": weaknesses_emb
            }
            await profiles.insert_one(new_profile)
            logger.info(f"Created new profile for {user_data.id}")
        else:
             # Basic signup without profile data - still require profile to exist?
             pass

    # 2. Check if user credentials already exist
    existing_user = await users.find_one({"id": user_data.id})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered. Please login.")

    # 3. Create user auth entry
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


@app.post("/change-password")
async def change_password(
    data: PasswordChange,
    user_id: str = Depends(get_current_user_id),
    users = Depends(get_users_collection)
):
    user = await users.find_one({"id": user_id})
    if not user or not verify_password(data.old_password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect current password")
    
    hashed_pw = get_password_hash(data.new_password)
    await users.update_one(
        {"id": user_id},
        {"$set": {"hashed_password": hashed_pw}}
    )
    return {"message": "Password updated successfully"}


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


@app.get("/profiles/{student_id}")
async def get_profile(student_id: str, collection = Depends(get_profiles_collection)):
    profile = await collection.find_one({"id": student_id}, {"strengths_emb": 0, "weaknesses_emb": 0})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile.pop("_id", None)
    return profile

@app.put("/profiles/{student_id}")
async def update_profile(
    student_id: str, 
    profile: ProfileInput, 
    collection = Depends(get_profiles_collection),
    user_id: str = Depends(get_current_user_id)
):
    # Ensure user can only update their own profile
    if student_id != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own profile")
        
    existing = await collection.find_one({"id": student_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Re-generate embeddings
    strengths_emb = embedding_service.embed_text(profile.strengths)
    weaknesses_emb = embedding_service.embed_text(profile.weaknesses)
    
    updated_data = profile.model_dump()
    updated_data["strengths_emb"] = list(strengths_emb)
    updated_data["weaknesses_emb"] = list(weaknesses_emb)
    
    
    await collection.update_one({"id": student_id}, {"$set": updated_data})
    
    return {"message": "Profile updated", "student_id": student_id}


# ---------------------------------------------------------------------------
# MATCHING (PEERS & TEAMS)
# ---------------------------------------------------------------------------
@app.get("/match/{student_id}")
async def get_matches(
    student_id: str,
    top_k: int = 3,
    use_cf: bool = True,
    profiles_col = Depends(get_profiles_collection),
    collaborations_col = Depends(get_collaborations_collection)
):
    """Get top matches for a student using hybrid scoring with collaborative filtering"""
    target = await profiles_col.find_one({"id": student_id})
    if not target:
        raise HTTPException(status_code=404, detail="Student not found")

    all_docs = await profiles_col.find().to_list(length=None)
    profiles_dict = {doc["id"]: doc for doc in all_docs if "strengths_emb" in doc}
    
    if student_id not in profiles_dict:
         raise HTTPException(status_code=500, detail="Profile missing valid embeddings.")

    # Fetch collaboration data for CF
    collaborations = []
    if use_cf:
        cursor = collaborations_col.find()
        collaborations = await cursor.to_list(length=None)
    
    matches = find_best_matches(student_id, profiles_dict, collaborations, top_k, use_cf)
    
    return {
        "student_id": student_id,
        "student_name": target["name"],
        "using_collaborative_filtering": use_cf and len(collaborations) > 0,
        "total_collaborations": len(collaborations),
        "matches": [
            {
                "student_id": m[0], 
                "name": m[1], 
                "hybrid_score": round(m[2], 4),
                "nlp_score": round(m[3], 4),
                "cf_score": round(m[4], 4),
                "graph_score": round(m[5], 4),
                "strengths": m[6], 
                "weaknesses": m[7]
            } 
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
    
    # Generate embedding for project description + stack + tags to help matching
    tags_str = " ".join(project_in.tags)
    combined_text = f"{project_in.title} {project_in.description} {project_in.stack} {tags_str}"
    desc_emb = embedding_service.embed_text(combined_text)
    logger.info(f"Project '{project_in.title}' description embedding: {desc_emb[:5]}...")  # print first 5 dims
    print(f"Project '{project_in.title}' description embedding: {desc_emb[:5]}...")
    project_doc = {
        "id": str(uuid.uuid4()),
        "creator_id": user_id,
        "creator_name": user_profile["name"],
        "title": project_in.title,
        "description": project_in.description,
        "stack": project_in.stack,
        "tags": project_in.tags,
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
    user_id: Optional[str] = Depends(get_current_user_optional),
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
        g_relevance = 0.0
        creator_id = doc.get("creator_id")

        if user_profile and "strengths_emb" in user_profile and "description_emb" in doc:
            # Only show score if NOT the owner
            if user_id != creator_id:
                # Use raw text for KG matching
                u_strengths = user_profile.get("strengths", "")
                # Combine title, description and stack for better entity extraction
                p_text = f"{doc.get('title', '')} {doc.get('description', '')} {doc.get('stack', '')}"
                
                relevance, g_relevance = calculate_project_relevance(
                    user_profile["strengths_emb"], 
                    doc["description_emb"],
                    u_strengths,
                    p_text
                )
        
        doc["relevance_score"] = round(relevance * 100, 0)
        doc["graph_score"] = round(g_relevance * 100, 0)
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

@app.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    user_id: str = Depends(get_current_user_id),
    projects = Depends(get_projects_collection)
):
    project = await projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["creator_id"] != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own projects")
    
    await projects.delete_one({"id": project_id})
    return {"message": "Project deleted"}

# ---------------------------------------------------------------------------
# COLLABORATIVE FILTERING
# ---------------------------------------------------------------------------
@app.post("/collaborations/rate")
async def rate_collaboration(
    rating_data: CollaborationRating,
    user_id: str = Depends(get_current_user_id),
    collaborations = Depends(get_collaborations_collection)
):
    """Record a collaboration rating from one student to another"""
    # Prevent self-rating
    if rating_data.student_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot rate yourself")
    
    collab_doc = {
        "id": str(uuid.uuid4()),
        "student_a": user_id,
        "student_b": rating_data.student_id,
        "rating": rating_data.rating,
        "worked_together": rating_data.worked_together,
        "feedback": rating_data.feedback,
        "project_context": rating_data.project_context,
        "timestamp": datetime.utcnow()
    }
    
    await collaborations.insert_one(collab_doc)
    logger.info(f"Collaboration rated: {user_id} -> {rating_data.student_id} ({rating_data.rating}/5)")
    
    return {"message": "Rating recorded successfully"}

@app.get("/collaborations/stats/{student_id}")
async def get_collaboration_stats(
    student_id: str,
    collaborations = Depends(get_collaborations_collection),
    profiles = Depends(get_profiles_collection)
):
    """Get collaboration statistics for a student"""
    # Find all ratings received by this student
    cursor = collaborations.find({"student_b": student_id})
    ratings = await cursor.to_list(length=None)
    
    if not ratings:
        return {
            "student_id": student_id,
            "total_collaborations": 0,
            "average_rating": 0.0,
            "top_rated_peers": []
        }
    
    total = len(ratings)
    avg_rating = sum(r['rating'] for r in ratings) / total
    
    # Count ratings by peer
    peer_ratings = {}
    for r in ratings:
        peer_id = r['student_a']
        if peer_id not in peer_ratings:
            peer_ratings[peer_id] = []
        peer_ratings[peer_id].append(r['rating'])
    
    # Calculate average per peer
    top_peers = []
    for peer_id, ratings_list in peer_ratings.items():
        peer_profile = await profiles.find_one({"id": peer_id})
        if peer_profile:
            top_peers.append({
                "student_id": peer_id,
                "name": peer_profile['name'],
                "avg_rating": sum(ratings_list) / len(ratings_list),
                "num_ratings": len(ratings_list)
            })
    
    # Sort by average rating
    top_peers.sort(key=lambda x: x['avg_rating'], reverse=True)
    
    return {
        "student_id": student_id,
        "total_collaborations": total,
        "average_rating": round(avg_rating, 2),
        "top_rated_peers": top_peers[:5]
    }

@app.post("/teams/record")
async def record_team(
    team_data: TeamFeedback,
    user_id: str = Depends(get_current_user_id),
    teams = Depends(get_team_history_collection)
):
    """Record a team formation and its success rating"""
    if user_id not in team_data.members:
        raise HTTPException(status_code=400, detail="You must be a team member")
    
    team_doc = {
        "team_id": str(uuid.uuid4()),
        "members": team_data.members,
        "project": team_data.project,
        "success_rating": team_data.success_rating,
        "created_at": datetime.utcnow(),
        "completed_at": datetime.utcnow()
    }
    
    await teams.insert_one(team_doc)
    return {"message": "Team recorded successfully"}

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
