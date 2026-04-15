# File: c:/Users/work/Documents/lp-agent/seed_data.py
# Purpose: Populate database with sample course catalog data.

from backend.database import SessionLocal, Base, engine
from backend.models import Course, Skill

def seed_database():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Course).count() > 0:
            print("Database already contains courses. Skipping seed.")
            return
        
        print("Seeding database with sample courses...")
        
        # Create Skills
        skills_data = [
            "Python", "JavaScript", "SQL", "Data Analysis", "Machine Learning",
            "Project Management", "Agile", "Leadership", "Communication",
            "Cloud Computing", "AWS", "Docker", "Kubernetes", "Git",
            "React", "Node.js", "FastAPI", "Data Visualization", "Statistics",
            "Deep Learning", "NLP", "Computer Vision", "DevOps", "CI/CD",
            "System Design", "Microservices", "API Design", "Testing"
        ]
        
        skills = {}
        for skill_name in skills_data:
            skill = Skill(name=skill_name)
            db.add(skill)
            db.flush()
            skills[skill_name] = skill
        
        print(f"Created {len(skills)} skills.")
        
        # Create Courses with realistic progression
        courses_data = [
            # Beginner Level - Foundations
            {
                "external_id": "CS101",
                "title": "Introduction to Programming with Python",
                "description": "Learn the fundamentals of programming using Python. No prior experience required.",
                "duration_hours": 40,
                "difficulty_level": "Beginner",
                "provider": "Internal",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/8KlhKkQBsUo",
                "skills": ["Python"]
            },
            {
                "external_id": "CS102",
                "title": "Git and Version Control Basics",
                "description": "Master version control with Git for collaborative development.",
                "duration_hours": 8,
                "difficulty_level": "Beginner",
                "provider": "Coursera",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/FdZecVQSF6E",
                "skills": ["Git"]
            },
            {
                "external_id": "DB101",
                "title": "SQL Fundamentals",
                "description": "Introduction to relational databases and SQL queries.",
                "duration_hours": 20,
                "difficulty_level": "Beginner",
                "provider": "Udemy",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/HXV3zeQKqGY",
                "skills": ["SQL"]
            },
            {
                "external_id": "WEB101",
                "title": "JavaScript Essentials",
                "description": "Learn JavaScript from scratch for web development.",
                "duration_hours": 35,
                "difficulty_level": "Beginner",
                "provider": "Internal",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/lWFqNX8e1k4",
                "skills": ["JavaScript"]
            },
            {
                "external_id": "PM101",
                "title": "Project Management Fundamentals",
                "description": "Core concepts of project management and planning.",
                "duration_hours": 16,
                "difficulty_level": "Beginner",
                "provider": "LinkedIn Learning",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/67qjWP_BtJE",
                "skills": ["Project Management"]
            },
            
            # Intermediate Level
            {
                "external_id": "CS201",
                "title": "Advanced Python Programming",
                "description": "Deep dive into Python: OOP, decorators, generators, and more.",
                "duration_hours": 50,
                "difficulty_level": "Intermediate",
                "provider": "Internal",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/EJVe27tPMRQ",
                "skills": ["Python"],
                "prerequisites": ["Introduction to Programming with Python"]
            },
            {
                "external_id": "DA101",
                "title": "Data Analysis with Python",
                "description": "Learn pandas, numpy, and data manipulation techniques.",
                "duration_hours": 45,
                "difficulty_level": "Intermediate",
                "provider": "Coursera",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/r-uOLxkrihE",
                "skills": ["Python", "Data Analysis"],
                "prerequisites": ["Introduction to Programming with Python", "SQL Fundamentals"]
            },
            {
                "external_id": "WEB201",
                "title": "React Fundamentals",
                "description": "Build modern web applications with React.",
                "duration_hours": 40,
                "difficulty_level": "Intermediate",
                "provider": "Udemy",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/w7ejDZ8SWv8",
                "skills": ["JavaScript", "React"],
                "prerequisites": ["WEB101"]
            },
            {
                "external_id": "WEB202",
                "title": "Node.js Backend Development",
                "description": "Create RESTful APIs with Node.js and Express.",
                "duration_hours": 38,
                "difficulty_level": "Intermediate",
                "provider": "Internal",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/fZQto6ebrFI",
                "skills": ["JavaScript", "Node.js", "API Design"],
                "prerequisites": ["WEB101"]
            },
            {
                "external_id": "API101",
                "title": "Building APIs with FastAPI",
                "description": "Modern Python API development with FastAPI framework.",
                "duration_hours": 30,
                "difficulty_level": "Intermediate",
                "provider": "Udemy",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/GN6ICac3OXY",
                "skills": ["Python", "FastAPI", "API Design"],
                "prerequisites": ["CS201", "DB101"]
            },
            {
                "external_id": "CLOUD101",
                "title": "AWS Cloud Fundamentals",
                "description": "Introduction to Amazon Web Services and cloud computing.",
                "duration_hours": 25,
                "difficulty_level": "Intermediate",
                "provider": "AWS Training",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/SOTamWNgDKc",
                "skills": ["Cloud Computing", "AWS"]
            },
            {
                "external_id": "PM201",
                "title": "Agile and Scrum Mastery",
                "description": "Implement Agile methodologies in your projects.",
                "duration_hours": 20,
                "difficulty_level": "Intermediate",
                "provider": "LinkedIn Learning",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/1aqX9u1EtgA",
                "skills": ["Agile", "Project Management"],
                "prerequisites": ["PM101"]
            },
            {
                "external_id": "STAT101",
                "title": "Statistics for Data Science",
                "description": "Essential statistical concepts for data analysis.",
                "duration_hours": 35,
                "difficulty_level": "Intermediate",
                "provider": "Coursera",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/xxpc2qLkxzA",
                "skills": ["Statistics", "Data Analysis"]
            },
            {
                "external_id": "VIZ101",
                "title": "Data Visualization with Python",
                "description": "Create compelling visualizations using matplotlib and seaborn.",
                "duration_hours": 25,
                "difficulty_level": "Intermediate",
                "provider": "Internal",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/a9urFkq5QK8",
                "skills": ["Python", "Data Visualization"],
                "prerequisites": ["DA101"]
            },
            {
                "external_id": "DEVOPS101",
                "title": "Docker Containerization",
                "description": "Package and deploy applications using Docker.",
                "duration_hours": 20,
                "difficulty_level": "Intermediate",
                "provider": "Udemy",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/rGFKcJgPg5A",
                "skills": ["Docker", "DevOps"]
            },
            
            # Advanced Level
            {
                "external_id": "ML101",
                "title": "Machine Learning Fundamentals",
                "description": "Introduction to ML algorithms and scikit-learn.",
                "duration_hours": 60,
                "difficulty_level": "Advanced",
                "provider": "Coursera",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/JcI5Vnw0B2M",
                "skills": ["Python", "Machine Learning", "Data Analysis"],
                "prerequisites": ["DA101", "STAT101"]
            },
            {
                "external_id": "ML201",
                "title": "Deep Learning with TensorFlow",
                "description": "Neural networks and deep learning architectures.",
                "duration_hours": 70,
                "difficulty_level": "Advanced",
                "provider": "Internal",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/wQ8BIBpH4Vs",
                "skills": ["Python", "Deep Learning", "Machine Learning"],
                "prerequisites": ["ML101"]
            },
            {
                "external_id": "ML301",
                "title": "Natural Language Processing",
                "description": "Advanced NLP techniques and transformer models.",
                "duration_hours": 55,
                "difficulty_level": "Advanced",
                "provider": "Coursera",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/8rXD5-xF5p4",
                "skills": ["Python", "NLP", "Deep Learning"],
                "prerequisites": ["ML201"]
            },
            {
                "external_id": "ML302",
                "title": "Computer Vision with Deep Learning",
                "description": "Image processing and CNN architectures.",
                "duration_hours": 55,
                "difficulty_level": "Advanced",
                "provider": "Udemy",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/IA3WxTTPXiM",
                "skills": ["Python", "Computer Vision", "Deep Learning"],
                "prerequisites": ["ML201"]
            },
            {
                "external_id": "CLOUD201",
                "title": "AWS Solutions Architect",
                "description": "Design scalable cloud architectures on AWS.",
                "duration_hours": 50,
                "difficulty_level": "Advanced",
                "provider": "AWS Training",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/I9VATZyN6DE",
                "skills": ["AWS", "Cloud Computing", "System Design"],
                "prerequisites": ["CLOUD101"]
            },
            {
                "external_id": "DEVOPS201",
                "title": "Kubernetes Orchestration",
                "description": "Deploy and manage containerized applications at scale.",
                "duration_hours": 45,
                "difficulty_level": "Advanced",
                "provider": "Linux Foundation",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/X48VuDVv0Z0",
                "skills": ["Kubernetes", "Docker", "DevOps"],
                "prerequisites": ["DEVOPS101"]
            },
            {
                "external_id": "DEVOPS301",
                "title": "CI/CD Pipeline Engineering",
                "description": "Build automated deployment pipelines.",
                "duration_hours": 35,
                "difficulty_level": "Advanced",
                "provider": "Internal",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/k-7VxPBhAhY",
                "skills": ["CI/CD", "DevOps", "Git"],
                "prerequisites": ["DEVOPS101", "CS102"]
            },
            {
                "external_id": "ARCH101",
                "title": "System Design and Architecture",
                "description": "Design scalable, distributed systems.",
                "duration_hours": 50,
                "difficulty_level": "Advanced",
                "provider": "Internal",
                "format": "In-Person",
                "youtube_url": "https://www.youtube.com/embed/ZgdS0EF0SE0",
                "skills": ["System Design", "Microservices"],
                "prerequisites": ["Building APIs with FastAPI", "SQL Fundamentals"]
            },
            {
                "external_id": "ARCH201",
                "title": "Microservices Architecture",
                "description": "Build and deploy microservices-based applications.",
                "duration_hours": 45,
                "difficulty_level": "Advanced",
                "provider": "Coursera",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/y8OnoxKSvFM",
                "skills": ["Microservices", "System Design", "API Design"],
                "prerequisites": ["ARCH101", "DEVOPS101"]
            },
            {
                "external_id": "WEB301",
                "title": "Full Stack Web Development",
                "description": "End-to-end web application development.",
                "duration_hours": 80,
                "difficulty_level": "Advanced",
                "provider": "Internal",
                "format": "Hybrid",
                "youtube_url": "https://www.youtube.com/embed/GXDjzwhhmJc",
                "skills": ["React", "Node.js", "SQL", "API Design"],
                "prerequisites": ["React Fundamentals", "Node.js Backend Development", "SQL Fundamentals"]
            },
            {
                "external_id": "TEST101",
                "title": "Software Testing and QA",
                "description": "Automated testing strategies and frameworks.",
                "duration_hours": 30,
                "difficulty_level": "Intermediate",
                "provider": "Udemy",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/bbhUQy9oqrU",
                "skills": ["Testing", "Python"],
                "prerequisites": ["Advanced Python Programming"]
            },
            {
                "external_id": "LEAD101",
                "title": "Technical Leadership",
                "description": "Lead engineering teams effectively.",
                "duration_hours": 25,
                "difficulty_level": "Advanced",
                "provider": "LinkedIn Learning",
                "format": "Online",
                "youtube_url": "https://www.youtube.com/embed/y-l-9sTzT3k",
                "skills": ["Leadership", "Communication"],
                "prerequisites": ["PM201"]
            },
            {
                "external_id": "LEAD201",
                "title": "Engineering Management",
                "description": "Transition from individual contributor to manager.",
                "duration_hours": 40,
                "difficulty_level": "Advanced",
                "provider": "Internal",
                "format": "In-Person",
                "youtube_url": "https://www.youtube.com/embed/dKd-gsCsXCQ",
                "skills": ["Leadership", "Project Management", "Communication"],
                "prerequisites": ["LEAD101", "PM201"]
            },
        ]
        
        # Create courses and map to skills
        course_map = {}
        prereq_mapping = {}  # Store prerequisites for second pass
        
        for course_data in courses_data:
            prereq_ids = course_data.pop("prerequisites", [])
            skill_names = course_data.pop("skills", [])
            
            course = Course(**course_data)
            db.add(course)
            db.flush()
            
            # Add skills
            for skill_name in skill_names:
                if skill_name in skills:
                    course.skills.append(skills[skill_name])
            
            course_map[course.external_id] = course
            if prereq_ids:
                prereq_mapping[course.external_id] = prereq_ids
        
        db.commit()
        print(f"Created {len(courses_data)} courses.")
        
        # Link prerequisites (second pass after all courses exist)
        for course_ext_id, prereq_ids in prereq_mapping.items():
            course = course_map[course_ext_id]
            for prereq_id in prereq_ids:
                if prereq_id in course_map:
                    course.prerequisites.append(course_map[prereq_id])
        
        db.commit()
        print(f"Linked prerequisites for {len(prereq_mapping)} courses.")
        print("✅ Database seeding complete!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
