# File: c:/Users/work/Documents/lp-agent/backend/services/engine_service.py
# Purpose: Core hybrid logic for generating the learning plan.

from sqlalchemy.orm import Session
from backend.models import Course, User, LearningPlan, PlanItem, Skill
from backend.services.ai_service import AIService
from typing import List, Set, Dict
from collections import deque

class LearningEngine:
    """
    Orchestrates the plan generation using both rule-based prerequisite checks
    and AI-based optimization.
    """

    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService()
        self._prerequisite_cache = {}  # Cache AI-inferred prerequisites

    async def get_course_prerequisites(self, course: Course, all_courses: List[Course] = None) -> List[Course]:
        """
        Get prerequisites for a course. Priority:
        1. Manual prerequisites (if defined in database)
        2. AI-inferred prerequisites (cached)
        
        Args:
            course: The course to get prerequisites for
            all_courses: Optional list of all courses (for AI inference)
            
        Returns:
            List of prerequisite courses
        """
        # Priority 1: Use manual prerequisites if they exist
        if course.prerequisites and len(course.prerequisites) > 0:
            return course.prerequisites
        
        # Priority 2: Check cache
        if course.id in self._prerequisite_cache:
            prereq_ids = self._prerequisite_cache[course.id]
            return [c for c in (all_courses or self.db.query(Course).all()) if c.id in prereq_ids]
        
        # Priority 3: Use AI inference
        if all_courses is None:
            all_courses = self.db.query(Course).all()
        
        # Convert courses to dict format for AI
        course_dict = {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'difficulty': course.difficulty_level
        }
        
        all_courses_dict = [{
            'id': c.id,
            'title': c.title,
            'description': c.description,
            'difficulty': c.difficulty_level
        } for c in all_courses]
        
        # Get AI inference
        prereq_ids = await self.ai.infer_prerequisites(course_dict, all_courses_dict)
        
        # Cache the result
        self._prerequisite_cache[course.id] = prereq_ids
        
        # Return course objects
        return [c for c in all_courses if c.id in prereq_ids]

    def check_prerequisites(self, course: Course, completed_course_ids: Set[int]) -> bool:
        """
        Rule-based check: valid if user has completed all required prereqs.
        """
        for prereq in course.prerequisites:
            if prereq.id not in completed_course_ids:
                return False
        return True

    async def get_skill_gap(self, user: User) -> List[str]:
        """
        Use AI to identify skills needed for target role that user doesn't have.
        """
        if not user.target_role:
            return []
        
        # Get all unique skills from course catalog
        all_course_skills = list(set(
            skill.name for course in self.db.query(Course).all() 
            for skill in course.skills
        ))
        
        # Use AI to infer required skills
        required_skills = await self.ai.infer_required_skills(
            current_role=user.current_role or "",
            target_role=user.target_role,
            current_skills=[s.name for s in user.skills],
            all_course_skills=all_course_skills
        )
        
        # Get user's current skills (case-insensitive)
        user_skill_names = {skill.name.lower() for skill in user.skills}
        
        # Return skills user doesn't have
        missing_skills = []
        for req_skill in required_skills:
            if req_skill.lower() not in user_skill_names:
                missing_skills.append(req_skill)
        
        return missing_skills
    
    
    async def get_prerequisite_chain(self, course: Course, visited: set = None, all_courses: List[Course] = None) -> List[Course]:
        """
        Get all prerequisites for a course recursively, using AI inference when needed.
        """
        if visited is None:
            visited = set()
        
        if course.id in visited:
            return []
        
        visited.add(course.id)
        chain = []
        
        # Get prerequisites (manual or AI-inferred)
        prerequisites = await self.get_course_prerequisites(course, all_courses)
        
        for prereq in prerequisites:
            chain.extend(await self.get_prerequisite_chain(prereq, visited, all_courses))
            if prereq not in chain:
                chain.append(prereq)
        
        return chain

    def build_prerequisite_graph(self, courses: List[Course]) -> Dict[int, List[int]]:
        """
        Build a directed graph of course dependencies.
        Returns: {course_id: [prerequisite_ids]}
        """
        graph = {}
        for course in courses:
            graph[course.id] = [prereq.id for prereq in course.prerequisites]
        return graph

    def get_skill_domain(self, course: Course) -> str:
        """
        Determine the primary skill domain for a course based on its skills.
        """
        skill_names = [s.name.lower() for s in course.skills]
        
        # Define skill domain priorities
        if any('python' in s for s in skill_names):
            return 'Programming'
        elif any(s in ['sql', 'database', 'data analysis', 'data visualization'] for s in skill_names):
            return 'Data'
        elif any(s in ['machine learning', 'deep learning', 'ai', 'nlp', 'computer vision'] for s in skill_names):
            return 'AI/ML'
        elif any(s in ['web development', 'react', 'node.js', 'api', 'fastapi'] for s in skill_names):
            return 'Web Development'
        elif any(s in ['devops', 'docker', 'kubernetes', 'cloud'] for s in skill_names):
            return 'DevOps'
        elif any(s in ['git', 'version control', 'testing', 'qa'] for s in skill_names):
            return 'Engineering Practices'
        else:
            return 'Other'
    
    
    async def topological_sort(self, courses: List[Course]) -> List[Course]:
        """
        Sort courses respecting prerequisites using topological sort (Kahn's algorithm).
        Uses AI-inferred prerequisites when manual ones aren't available.
        When multiple courses are available at the same level, prioritize by:
        1. Skill domain (to group related courses)
        2. Difficulty level (beginner → intermediate → advanced)
        3. Title (for consistency)
        """
        # Build graph
        in_degree = {course.id: 0 for course in courses}
        adj_list = {course.id: [] for course in courses}
        course_map = {course.id: course for course in courses}
        
        # Difficulty ordering
        difficulty_order = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
        
        # Skill domain ordering (logical learning progression)
        domain_order = {
            'Programming': 0,
            'Engineering Practices': 1,
            'Data': 2,
            'Web Development': 3,
            'AI/ML': 4,
            'DevOps': 5,
            'Other': 6
        }
        
        # Build adjacency list using AI-inferred prerequisites
        for course in courses:
            prerequisites = await self.get_course_prerequisites(course, courses)
            for prereq in prerequisites:
                if prereq.id in adj_list:  # Only if prereq is in our course list
                    adj_list[prereq.id].append(course.id)
                    in_degree[course.id] += 1
        
        # Find all nodes with no incoming edges, sorted by difficulty, then domain
        initial_nodes = [cid for cid in in_degree if in_degree[cid] == 0]
        initial_nodes.sort(key=lambda cid: (
            difficulty_order.get(course_map[cid].difficulty_level, 0),
            domain_order.get(self.get_skill_domain(course_map[cid]), 6),
            course_map[cid].title
        ))
        
        queue = deque(initial_nodes)
        sorted_courses = []
        
        while queue:
            current_id = queue.popleft()
            sorted_courses.append(course_map[current_id])
            
            # Collect neighbors that become available
            available_neighbors = []
            for neighbor_id in adj_list[current_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    available_neighbors.append(neighbor_id)
            
            # Sort available neighbors by difficulty, then domain
            available_neighbors.sort(key=lambda cid: (
                difficulty_order.get(course_map[cid].difficulty_level, 0),
                domain_order.get(self.get_skill_domain(course_map[cid]), 6),
                course_map[cid].title
            ))
            
            queue.extend(available_neighbors)
        
        # If we couldn't sort all courses, there's a cycle (shouldn't happen with our data)
        if len(sorted_courses) != len(courses):
            # Fallback: return courses sorted by difficulty and domain
            return sorted(courses, key=lambda c: (
                difficulty_order.get(c.difficulty_level, 0),
                domain_order.get(self.get_skill_domain(c), 6),
                c.title
            ))
        
        return sorted_courses

    async def generate_learning_path(self, user_id: int) -> dict:
        """
        Main function to create the timeline.
        1. Fetch user goal & skills.
        2. Identify gap (required courses).
        3. Build dependency graph.
        4. Use AI to optimize parallel tracks and provide explanations.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Step 1: Identify skill gap
        missing_skills = await self.get_skill_gap(user)
        
        # Track if target role matched any courses
        role_matched_catalog = len(missing_skills) > 0
        
        # Step 2: Find courses that teach these skills
        relevant_courses = []
        all_courses_needed = set()
        
        if missing_skills:
            # Get courses that teach missing skills
            target_courses = self.db.query(Course).join(Course.skills).filter(
                Skill.name.in_(missing_skills)
            ).distinct().all()
            
            if not target_courses:
                # No courses found for the required skills
                warning = f"No courses are currently available for the skills required for '{user.target_role}'. Required skills: {', '.join(missing_skills)}"
                plan = LearningPlan(user_id=user_id, status="no_courses_available")
                self.db.add(plan)
                self.db.commit()
                self.db.refresh(plan)
                return {
                    "plan_id": plan.id,
                    "user_id": user.id,
                    "created_at": plan.created_at,
                    "status": plan.status,
                    "total_duration_hours": 0,
                    "items": [],
                    "warning": warning
                }
            
            # For each target course, include all prerequisites
            for course in target_courses:
                all_courses_needed.add(course)
                # Add all prerequisites recursively
                prereq_chain = await self.get_prerequisite_chain(course)
                
                # Check user skills for filtering prerequisites
                user_skill_names = {skill.name.lower() for skill in user.skills}
                
                for prereq in prereq_chain:
                    # Skip prerequisite if user already has all skills taught by this course
                    prereq_skills = {skill.name.lower() for skill in prereq.skills}
                    if not prereq_skills.issubset(user_skill_names):
                        all_courses_needed.add(prereq)
            
            relevant_courses = list(all_courses_needed)
        else:
            # No skill gap found - target role might be irrelevant to catalog
            # Provide a curated starter path instead of all courses
            
            # Check if we have ANY courses at all
            total_courses = self.db.query(Course).count()
            
            if total_courses > 15:
                # Offer a balanced learning path across difficulty levels
                beginner = self.db.query(Course).filter(
                    Course.difficulty_level == "Beginner"
                ).limit(5).all()
                
                intermediate = self.db.query(Course).filter(
                    Course.difficulty_level == "Intermediate"
                ).limit(5).all()
                
                advanced = self.db.query(Course).filter(
                    Course.difficulty_level == "Advanced"
                ).limit(5).all()
                
                # Combine and get prerequisites
                starter_courses = beginner + intermediate + advanced
                all_courses_needed = set(starter_courses)
                
                for course in starter_courses:
                    prereq_chain = await self.get_prerequisite_chain(course)
                    all_courses_needed.update(prereq_chain)
                
                relevant_courses = list(all_courses_needed)
            else:
                # Small catalog, show everything
                relevant_courses = self.db.query(Course).all()
        
        # Step 3: Sort by prerequisites (topological sort with AI inference)
        sorted_courses = await self.topological_sort(relevant_courses)
        
        # Step 4: Use AI to optimize and explain
        optimized_plan = await self.ai.optimize_sequence(
            user_profile={
                "current_role": user.current_role,
                "target_role": user.target_role,
                "experience_years": user.experience_years,
                "current_skills": [s.name for s in user.skills]
            },
            courses=[{
                "id": c.id,
                "title": c.title,
                "skills": [s.name for s in c.skills],
                "duration_hours": c.duration_hours,
                "difficulty": c.difficulty_level
            } for c in sorted_courses]
        )
        
        # Step 5: Create the learning plan in database
        plan = LearningPlan(user_id=user_id, status="active")
        self.db.add(plan)
        self.db.flush()
        
        total_duration = 0
        items = []
        
        for idx, course_data in enumerate(optimized_plan["courses"], start=1):
            course = self.db.query(Course).filter(Course.id == course_data["id"]).first()
            
            plan_item = PlanItem(
                learning_plan_id=plan.id,
                course_id=course.id,
                sequence_order=idx,
                status="pending"
            )
            self.db.add(plan_item)
            self.db.flush()  # Flush to get the plan_item id
            
            items.append({
                "id": plan_item.id,
                "course_id": course.id,
                "course_title": course.title,
                "status": "pending",
                "sequence_order": idx,
                "duration_hours": course.duration_hours,
                "difficulty_level": course.difficulty_level,
                "explanation": course_data.get("explanation", "")
            })
            
            total_duration += course.duration_hours or 0
        
        self.db.commit()
        
        # Add warning if target role didn't match catalog
        warning = None
        if not role_matched_catalog and user.target_role:
            warning = f"Note: '{user.target_role}' doesn't match our current course catalog (focused on software/data roles). Showing a curated selection of available courses."
        
        return {
            "plan_id": plan.id,
            "user_id": user.id,
            "created_at": plan.created_at,
            "status": plan.status,
            "total_duration_hours": total_duration,
            "items": items,
            "warning": warning
        }
