# File: c:/Users/work/Documents/lp-agent/backend/schemas.py
# Purpose: Pydantic models for request/response validation.

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- User Schemas ---
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    current_role: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: Optional[int] = 0

class UserProfileUpdate(BaseModel):
    current_role: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[List[str]] = None

class UserResponse(BaseModel):
    id: int
    username: str
    current_role: Optional[str]
    target_role: Optional[str]
    experience_years: int
    skills: List[str] = []
    
    class Config:
        from_attributes = True

# --- Course Schemas ---
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_hours: Optional[int] = None
    difficulty_level: Optional[str] = None
    provider: Optional[str] = None
    format: Optional[str] = None

class CourseResponse(BaseModel):
    id: int
    external_id: Optional[str]
    title: str
    description: Optional[str]
    duration_hours: Optional[int]
    difficulty_level: Optional[str]
    provider: Optional[str]
    format: Optional[str]
    youtube_url: Optional[str]
    skills: List[str] = []
    prerequisites: List[str] = []  # List of course titles
    
    class Config:
        from_attributes = True

# --- Plan Schemas ---
class LearningPlanRequest(BaseModel):
    user_id: int

class PlanItemStatusUpdate(BaseModel):
    status: str

class PlanItemResponse(BaseModel):
    id: Optional[int] = None
    course_id: int
    course_title: str
    status: str
    sequence_order: int
    duration_hours: Optional[int]
    difficulty_level: Optional[str]
    explanation: Optional[str] = None  # Why this course is recommended
    
    class Config:
        from_attributes = True

class LearningPlanResponse(BaseModel):
    plan_id: int
    user_id: int
    created_at: datetime
    status: str
    total_duration_hours: int
    items: List[PlanItemResponse]
    warning: str | None = None
    
    class Config:
        from_attributes = True
