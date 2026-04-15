# File: c:/Users/work/Documents/lp-agent/backend/api/endpoints.py
# Purpose: Definition of API routes.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User, Course, LearningPlan, PlanItem, Skill
from backend.schemas import (
    UserLogin, UserCreate, UserProfileUpdate, UserResponse,
    CourseResponse, LearningPlanRequest, LearningPlanResponse, PlanItemResponse,
    PlanItemStatusUpdate
)
from backend.auth import hash_password, verify_password
from backend.services.engine_service import LearningEngine

router = APIRouter()

# --- Auth & User Endpoints ---
@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Check if username exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        current_role=user_data.current_role,
        target_role=user_data.target_role,
        experience_years=user_data.experience_years
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return user info.
    """
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "user_id": user.id,
        "username": user.username,
        "message": "Login successful"
    }

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user profile by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "current_role": user.current_role,
        "target_role": user.target_role,
        "experience_years": user.experience_years,
        "skills": [skill.name for skill in user.skills]
    }

@router.put("/users/{user_id}/profile", response_model=UserResponse)
def update_profile(user_id: int, profile: UserProfileUpdate, db: Session = Depends(get_db)):
    """
    Update user profile information.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if profile.current_role is not None:
        user.current_role = profile.current_role
    if profile.target_role is not None:
        user.target_role = profile.target_role
    if profile.experience_years is not None:
        user.experience_years = profile.experience_years
    
    # Update skills
    if profile.skills is not None:
        user.skills.clear()
        for skill_name in profile.skills:
            # Try to find existing skill
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            
            # If skill doesn't exist, create it
            if not skill:
                skill = Skill(name=skill_name)
                db.add(skill)
                db.flush()  # Flush to get the skill ID
            
            user.skills.append(skill)
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "current_role": user.current_role,
        "target_role": user.target_role,
        "experience_years": user.experience_years,
        "skills": [skill.name for skill in user.skills]
    }

# --- Course Endpoints ---
@router.get("/courses", response_model=List[CourseResponse])
def get_courses(
    difficulty: str = None,
    skill: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all courses, optionally filtered by difficulty or skill.
    """
    query = db.query(Course)
    
    if difficulty:
        query = query.filter(Course.difficulty_level == difficulty)
    
    if skill:
        query = query.join(Course.skills).filter(Skill.name == skill)
    
    courses = query.all()
    
    # Format response
    result = []
    for course in courses:
        result.append({
            "id": course.id,
            "external_id": course.external_id,
            "title": course.title,
            "description": course.description,
            "duration_hours": course.duration_hours,
            "difficulty_level": course.difficulty_level,
            "provider": course.provider,
            "format": course.format,
            "youtube_url": course.youtube_url,
            "skills": [s.name for s in course.skills],
            "prerequisites": [p.title for p in course.prerequisites]
        })
    
    return result

@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    Get a specific course by ID.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "id": course.id,
        "external_id": course.external_id,
        "title": course.title,
        "description": course.description,
        "duration_hours": course.duration_hours,
        "difficulty_level": course.difficulty_level,
        "provider": course.provider,
        "format": course.format,
        "youtube_url": course.youtube_url,
        "skills": [s.name for s in course.skills],
        "prerequisites": [p.title for p in course.prerequisites]
    }

# --- Learning Plan Endpoints ---
@router.post("/plans/generate", response_model=LearningPlanResponse)
async def generate_plan(request: LearningPlanRequest, db: Session = Depends(get_db)):
    """
    Generate a learning plan for a user.
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.target_role:
        raise HTTPException(status_code=400, detail="User must set a target role first")
    
    # Use the learning engine to generate the plan
    engine = LearningEngine(db)
    plan_data = await engine.generate_learning_path(user.id)
    
    return plan_data

@router.get("/plans/user/{user_id}", response_model=LearningPlanResponse)
def get_user_plan(user_id: int, db: Session = Depends(get_db)):
    """
    Get the active learning plan for a user.
    """
    plan = db.query(LearningPlan).filter(
        LearningPlan.user_id == user_id,
        LearningPlan.status == "active"
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan found")
    
    # Format response
    items = []
    total_duration = 0
    
    for item in sorted(plan.items, key=lambda x: x.sequence_order):
        course = item.course
        items.append({
            "id": item.id,
            "course_id": course.id,
            "course_title": course.title,
            "status": item.status,
            "sequence_order": item.sequence_order,
            "duration_hours": course.duration_hours,
            "difficulty_level": course.difficulty_level
        })
        total_duration += course.duration_hours or 0
    
    return {
        "plan_id": plan.id,
        "user_id": plan.user_id,
        "created_at": plan.created_at,
        "status": plan.status,
        "total_duration_hours": total_duration,
        "items": items
    }

@router.put("/plans/{plan_id}/items/{item_id}/status")
def update_item_status(
    plan_id: int,
    item_id: int,
    payload: PlanItemStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update the status of a plan item (e.g., mark as completed).
    """
    item = db.query(PlanItem).filter(
        PlanItem.id == item_id,
        PlanItem.learning_plan_id == plan_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Plan item not found")
    
    if payload.status not in ["pending", "in_progress", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    item.status = payload.status
    db.commit()
    
    return {"message": "Status updated", "item_id": item_id, "new_status": payload.status}

@router.get("/skills", response_model=List[str])
def get_all_skills(db: Session = Depends(get_db)):
    """
    Get list of all available skills.
    """
    skills = db.query(Skill).all()
    return [skill.name for skill in skills]
