# File: c:/Users/work/Documents/lp-agent/backend/utils/import_catalog.py
# Purpose: Utility to import course catalog from Excel.

# Note: This file assumes an Excel structure. 
# Since we don't have the actual file, we'll design for a likely schema and provide headers info.
# Expected Headers: ID, Title, Description, Duration, Difficulty, Provider, Skills, Prerequisites

import pandas as pd
from sqlalchemy.orm import Session
from backend.models import Course, Skill
from backend.database import SessionLocal, engine

def import_courses_from_excel(file_path: str):
    """
    Reads an Excel file and populates the database.
    """
    db = SessionLocal()
    try:
        # Load the data
        print(f"Reading file: {file_path}")
        df = pd.read_excel(file_path)
        
        # Verify headers (basic check)
        required_cols = ['Title', 'Description'] # Minimal requirement
        for col in required_cols:
            if col not in df.columns:
                print(f"Error: Missing required column '{col}'")
                return

        # 1. Create Courses
        print("Importing courses...")
        # Use a dict to map External IDs to DB objects for prereq linking
        course_map = {} 
        
        for index, row in df.iterrows():
            title = row.get('Title')
            if pd.isna(title): continue
            
            # Check if exists
            existing = db.query(Course).filter(Course.title == title).first()
            if existing:
                print(f"Skipping existing course: {title}")
                course_map[row.get('ID')] = existing
                continue
                
            course = Course(
                external_id=str(row.get('ID')) if not pd.isna(row.get('ID')) else None,
                title=title,
                description=row.get('Description'),
                duration_hours=int(row.get('Duration')) if not pd.isna(row.get('Duration')) else 0,
                difficulty_level=row.get('Difficulty'),
                provider=row.get('Provider'),
                format=row.get('Format')
            )
            db.add(course)
            db.flush() # flush to get ID
            
            # Handle Skills (comma separated)
            skills_str = row.get('Skills')
            if not pd.isna(skills_str):
                skill_names = [s.strip() for s in str(skills_str).split(',')]
                for s_name in skill_names:
                    # Find or create skill
                    skill = db.query(Skill).filter(Skill.name == s_name).first()
                    if not skill:
                        skill = Skill(name=s_name)
                        db.add(skill)
                    if skill not in course.skills:
                        course.skills.append(skill)
            
            # Map external ID to course object for later
            if course.external_id:
                course_map[course.external_id] = course

        db.commit()
        print("Courses and Skills imported.")
        
        # 2. Link Prerequisites (Need a second pass or mapped logic)
        # Assuming Prerequisites column contains comma-separated IDs of other courses
        print("Linking prerequisites...")
        for index, row in df.iterrows():
            curr_id = str(row.get('ID'))
            if curr_id not in course_map: continue
            
            course = course_map[curr_id]
            prereqs_str = row.get('Prerequisites')
            
            if not pd.isna(prereqs_str):
                prereq_ids = [str(p).strip() for p in str(prereqs_str).split(',')]
                for pid in prereq_ids:
                    if pid in course_map:
                        prereq_course = course_map[pid]
                        if prereq_course not in course.prerequisites:
                            course.prerequisites.append(prereq_course)
        
        db.commit()
        print("Import completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Example usage
    # import_courses_from_excel("path/to/catalog.xlsx")
    print("Run this script with the path to your Excel file.")
