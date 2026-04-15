# File: c:/Users/work/Documents/lp-agent/backend/models.py
# Purpose: SQLAlchemy models representing database tables.

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base

# Association table for Course Prerequisites (Many-to-Many self-referential)
course_prerequisites = Table(
    'course_prerequisites', Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('prerequisite_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

# Association table for Course Skills (Many-to-Many)
course_skills = Table(
    'course_skills', Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

# Association table for User Skills (Many-to-Many)
user_skills = Table(
    'user_skills', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)

class User(Base):
    """
    Represents an employee user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # In MVP, we might store plain or simple hash
    
    # Profile fields
    current_role = Column(String)
    target_role = Column(String)
    experience_years = Column(Integer, default=0)
    
    # Relationships
    skills = relationship("Skill", secondary=user_skills, back_populates="users")
    learning_plans = relationship("LearningPlan", back_populates="user")

class Skill(Base):
    """
    Represents a skill (e.g., 'Python', 'Project Management').
    """
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    # Relationships
    courses = relationship("Course", secondary=course_skills, back_populates="skills")
    users = relationship("User", secondary=user_skills, back_populates="skills")

class Course(Base):
    """
    Represents a course in the catalog.
    """
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    # External ID from source system (e.g. Excel ID)
    external_id = Column(String, index=True, nullable=True) 
    
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    duration_hours = Column(Integer) # Estimated duration
    difficulty_level = Column(String) # Beginner, Intermediate, Advanced
    provider = Column(String) # e.g. "Coursera", "Internal", "Udemy"
    format = Column(String) # Online, In-Person
    youtube_url = Column(String, nullable=True) # YouTube video URL for the course
    
    # Relationships
    skills = relationship("Skill", secondary=course_skills, back_populates="courses")
    
    # Self-referential Many-to-Many for prerequisites
    prerequisites = relationship(
        "Course",
        secondary=course_prerequisites,
        primaryjoin=id==course_prerequisites.c.course_id,
        secondaryjoin=id==course_prerequisites.c.prerequisite_id,
        backref="required_for"
    )

class LearningPlan(Base):
    """
    Represents a generated learning plan for a user.
    """
    __tablename__ = "learning_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="active") # active, completed, archived

    # Relationships
    user = relationship("User", back_populates="learning_plans")
    items = relationship("PlanItem", back_populates="learning_plan", cascade="all, delete-orphan")

class PlanItem(Base):
    """
    A specific course assignment within a learning plan.
    """
    __tablename__ = "plan_items"

    id = Column(Integer, primary_key=True, index=True)
    learning_plan_id = Column(Integer, ForeignKey("learning_plans.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    
    status = Column(String, default="pending") # pending, in_progress, completed
    sequence_order = Column(Integer) # 1, 2, 3... used for ordering
    
    # Relationships
    learning_plan = relationship("LearningPlan", back_populates="items")
    course = relationship("Course")
