from pydantic import BaseModel, Field
from typing import Optional, List
import numpy as np


class ProfileInput(BaseModel):
    """Input schema for creating a new student profile"""
    id: str = Field(..., description="Unique student ID")
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
    strengths: str
    weaknesses: str
