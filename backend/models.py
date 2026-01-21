from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import numpy as np


from datetime import datetime

class ProfileInput(BaseModel):
    """Input schema for creating a new student profile"""
    id: str = Field(..., description="Unique student ID (USN)")
    name: str = Field(..., description="Student name")
    strengths: str = Field(..., description="Subjects or topics the student excels at")
    weaknesses: str = Field(..., description="Subjects or topics the student needs help with")
    preferences: Optional[str] = Field("", description="Study preferences (time, group size, etc.)")
    description: Optional[str] = Field("", description="Additional information about learning style")


class ProfileStored(ProfileInput):
    """Extended schema with computed embeddings"""
    strengths_emb: List[float] = Field(..., description="Embedding vector for strengths")
    weaknesses_emb: List[float] = Field(..., description="Embedding vector for weaknesses")


class MatchResult(BaseModel):
    """Schema for match result"""
    student_id: str
    name: str
    score: float
    graph_score: float
    strengths: str
    weaknesses: str


class TeamResult(BaseModel):
    """Schema for a team of complementary students"""
    team_members: List[MatchResult]
    overall_score: float


# --- NEW MODELS ---

class UserAuth(BaseModel):
    """Schema for login/signup"""
    id: str = Field(..., description="USN")
    password: str = Field(..., description="Unique password")
    
    # Optional fields for signup-with-profile
    name: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    preferences: Optional[str] = None
    description: Optional[str] = None


class PasswordChange(BaseModel):
    """Schema for changing password"""
    old_password: str
    new_password: str


class UserInDB(BaseModel):
    """Stored user credentials"""
    id: str
    hashed_password: str


class Comment(BaseModel):
    """Project comment"""
    user_id: str
    user_name: str
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProjectBase(BaseModel):
    title: str
    description: str
    stack: str
    tags: List[str] = []


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: str
    creator_id: str
    creator_name: str
    votes: int = 0
    voted_by: List[str] = [] # List of user IDs who voted
    comments: List[Comment] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Store embedding of the project description/stack for relevance matching
    description_emb: Optional[List[float]] = None 


class ProjectWithScore(Project):
    relevance_score: float = 0.0
    graph_score: float = 0.0


# --- COLLABORATIVE FILTERING MODELS ---

class CollaborationRating(BaseModel):
    """User rates another student they worked with"""
    student_id: str = Field(..., description="ID of student being rated")
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating from 1-5")
    worked_together: bool = Field(True, description="Confirm they worked together")
    feedback: Optional[str] = Field(None, description="Optional text feedback")
    project_context: Optional[str] = Field(None, description="What project/context")


class TeamFeedback(BaseModel):
    """Feedback for an entire team"""
    members: List[str] = Field(..., description="All team member IDs including self")
    project: str = Field(..., description="Project name/description")
    success_rating: float = Field(..., ge=1.0, le=5.0, description="Overall team success")


class CollaborationStats(BaseModel):
    """Statistics about a student's collaboration history"""
    total_collaborations: int
    average_rating: float
    top_rated_peers: List[Dict]  # [{student_id, name, avg_rating}, ...]
