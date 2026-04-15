# File: c:/Users/work/Documents/lp-agent/backend/services/ai_service.py
# Purpose: Integration with external AI services (e.g., OpenAI).

from openai import OpenAI
from backend.config import settings
from typing import List, Dict
import json
import re

class AIService:
    """
    Handles interactions with the LLM for learning plan generation and enhancement.
    """
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.startswith('sk-'):
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_json(self, text: str) -> dict:
        """
        Extract JSON from text, handling markdown code blocks.
        """
        # Try to find JSON in markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        
        # Try to parse JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find the first { and last }
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
            raise

    async def infer_prerequisites(self, course: Dict, all_courses: List[Dict]) -> List[int]:
        """
        Use AI to infer which courses should be prerequisites based on course titles and descriptions.
        
        Args:
            course: The course to find prerequisites for (dict with id, title, description, difficulty)
            all_courses: List of all available courses
            
        Returns:
            List of course IDs that should be prerequisites
        """
        if not self.client:
            # Fallback: simple rule-based inference
            return self._rule_based_prerequisite_inference(course, all_courses)
        
        try:
            # Build course catalog for AI
            course_catalog = "\n".join([
                f"ID={c['id']}, Title=\"{c['title']}\", Difficulty={c.get('difficulty', 'N/A')}, Description=\"{c.get('description', '')[:100]}...\""
                for c in all_courses if c['id'] != course['id']
            ])
            
            prompt = f"""You are an expert course curriculum designer. Analyze the following course and determine which other courses should be prerequisites.

TARGET COURSE:
- Title: {course['title']}
- Description: {course.get('description', 'N/A')}
- Difficulty: {course.get('difficulty', 'N/A')}

AVAILABLE COURSES:
{course_catalog}

TASK: Identify which courses (by ID) should be prerequisites for the target course. Consider:
1. Foundational knowledge needed (e.g., "Advanced Python" needs "Introduction to Python")
2. Skill dependencies (e.g., "Machine Learning" needs "Statistics" and "Python")
3. Difficulty progression (Advanced courses need Intermediate/Beginner prerequisites)
4. Topic relationships (e.g., "Deep Learning" needs "Machine Learning Fundamentals")

Respond ONLY with valid JSON in this format (no markdown, no extra text):
{{"prerequisite_ids": [1, 2, 3], "reasoning": "Brief explanation"}}

If no prerequisites are needed, return: {{"prerequisite_ids": [], "reasoning": "This is a foundational course"}}"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3  # Lower temperature for more consistent results
            )
            
            response_text = response.choices[0].message.content.strip()
            result = self.extract_json(response_text)
            
            print(f"AI Prerequisites for '{course['title']}': {result.get('prerequisite_ids', [])} - {result.get('reasoning', '')}")
            
            return result.get('prerequisite_ids', [])
            
        except Exception as e:
            print(f"AI prerequisite inference failed for '{course['title']}': {e}")
            # Fallback to rule-based
            return self._rule_based_prerequisite_inference(course, all_courses)
    
    async def infer_required_skills(self, current_role: str, target_role: str, current_skills: List[str], all_course_skills: List[str]) -> List[str]:
        """
        Use AI to infer which skills are required for the target role, considering current role and skills.
        
        Args:
            current_role: User's current job title
            target_role: Desired job title
            current_skills: List of skills user already has
            all_course_skills: List of all skills taught in the course catalog
            
        Returns:
            List of required skills for the target role
        """
        if not self.client:
            # Fallback: simple rule-based skill inference
            return self._rule_based_skill_inference(target_role, all_course_skills)
        
        try:
            course_skills_str = ', '.join(all_course_skills)
            
            prompt = f"""You are a career development expert. Analyze the following career transition and determine which skills are essential for the target role.

CURRENT SITUATION:
- Current Role: {current_role}
- Target Role: {target_role}
- Current Skills: {', '.join(current_skills) if current_skills else 'None specified'}

AVAILABLE SKILLS IN COURSE CATALOG:
{course_skills_str}

TASK: Identify the key skills needed to transition from the current role to the target role. Consider:
1. Core competencies required for the target role
2. Skills that bridge the gap between current and target roles  
3. Technical and soft skills relevant to the career change
4. Skills that are actually taught in our course catalog (prefer these)

IMPORTANT GUIDELINES:
- DO NOT suggest skills that the user already has listed in Current Skills
- DO NOT suggest programming languages or tools that the user already knows
- Only suggest NEW skills needed for the target role
- For Manual Tester/QA roles: Focus ONLY on testing, QA, quality assurance, and test management skills. Do not suggest any programming languages or development skills.
- For development roles: Focus on programming languages, frameworks, and tools NOT already known
- Avoid generic skills like basic programming unless the user has no programming experience
- If the user already has programming skills, don't suggest them again

Return skills that are missing or need improvement for this transition.

Respond ONLY with valid JSON in this format (no markdown, no extra text):
{{"required_skills": ["Skill1", "Skill2", "Skill3"]}}

If no additional skills are needed, return: {{"required_skills": []}}"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            result = self.extract_json(response_text)
            
            required_skills = result.get('required_skills', [])
            print(f"AI Required Skills for '{target_role}': {required_skills}")
            
            # Filter out skills the user already has
            current_skills_lower = [s.lower() for s in current_skills]
            required_skills = [skill for skill in required_skills if skill.lower() not in current_skills_lower]
            print(f"Filtered Required Skills (excluding user's skills): {required_skills}")
            
            # Additional filter for testing roles: only keep testing-related skills
            target_lower = target_role.lower()
            if 'tester' in target_lower or 'qa' in target_lower or 'testing' in target_lower:
                testing_keywords = ['testing', 'qa', 'quality assurance', 'test management', 'manual testing', 'automation testing', 'quality', 'test']
                required_skills = [skill for skill in required_skills if any(keyword in skill.lower() for keyword in testing_keywords)]
                print(f"Filtered for testing role: {required_skills}")
            
            return required_skills
            
        except Exception as e:
            print(f"AI skill inference failed for '{target_role}': {e}")
            # Fallback to rule-based
            return self._rule_based_skill_inference(target_role, all_course_skills, current_skills)
    
    def _rule_based_skill_inference(self, target_role: str, all_course_skills: List[str], current_skills: List[str]) -> List[str]:
        """
        Simple rule-based skill inference as fallback.
        """
        role_lower = target_role.lower()
        current_skills_lower = [s.lower() for s in current_skills]
        required = []
        
        # Basic mappings
        if 'machine learning' in role_lower or 'ml' in role_lower:
            required.extend(['Python', 'Statistics', 'Machine Learning', 'Data Analysis'])
        if 'data scientist' in role_lower:
            required.extend(['Python', 'Statistics', 'Machine Learning', 'Data Analysis'])
        if 'engineer' in role_lower:
            required.extend(['Python', 'System Design'])
        if 'developer' in role_lower:
            required.extend(['Python', 'JavaScript', 'Git'])
        if 'tester' in role_lower or 'testing' in role_lower or 'qa' in role_lower:
            required.extend(['Testing', 'QA'])
        
        # Filter to only skills available in catalog and not already known
        return [skill for skill in required if skill in all_course_skills and skill.lower() not in current_skills_lower]

    def _rule_based_prerequisite_inference(self, course: Dict, all_courses: List[Dict]) -> List[int]:
        """
        Simple rule-based prerequisite inference as fallback.
        """
        prereqs = []
        title_lower = course['title'].lower()
        difficulty = course.get('difficulty', 'Beginner')
        
        # Rule 1: "Advanced" courses need corresponding "Fundamentals" or "Introduction" courses
        if 'advanced' in title_lower:
            base_topic = title_lower.replace('advanced', '').strip()
            for c in all_courses:
                c_title_lower = c['title'].lower()
                if c['id'] != course['id']:
                    if ('fundamentals' in c_title_lower or 'introduction' in c_title_lower) and base_topic in c_title_lower:
                        prereqs.append(c['id'])
        
        # Rule 2: Specific domain rules
        domain_rules = {
            'deep learning': ['machine learning'],
            'machine learning': ['statistics', 'data analysis', 'python'],
            'computer vision': ['deep learning', 'machine learning'],
            'nlp': ['deep learning', 'machine learning'],
            'natural language processing': ['deep learning', 'machine learning'],
            'react': ['javascript'],
            'node.js': ['javascript'],
            'kubernetes': ['docker'],
            'microservices': ['api', 'docker'],
        }
        
        for keyword, required_keywords in domain_rules.items():
            if keyword in title_lower:
                for c in all_courses:
                    c_title_lower = c['title'].lower()
                    if c['id'] != course['id'] and any(req in c_title_lower for req in required_keywords):
                        if c['id'] not in prereqs:
                            prereqs.append(c['id'])
        
        return prereqs

    async def generate_plan_explanation(self, user_profile: dict, recommended_courses: list) -> str:
        """
        Generates a natural language explanation for why specific courses were chosen.
        """
        if not self.client:
            return "Courses recommended based on your target role and skill gaps."
        
        try:
            prompt = f"""
            User Profile:
            - Current Role: {user_profile.get('current_role')}
            - Target Role: {user_profile.get('target_role')}
            - Experience: {user_profile.get('experience_years')} years
            - Current Skills: {', '.join(user_profile.get('current_skills', []))}
            
            Recommended Courses: {', '.join([c['title'] for c in recommended_courses])}
            
            Explain in 2-3 sentences why this learning path makes sense for this user.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI explanation generation failed: {e}")
            return "Courses recommended based on your target role and skill gaps."

    async def optimize_sequence(self, user_profile: dict, courses: List[Dict]) -> Dict:
        """
        Uses AI to suggest optimal ordering and provide explanations for each course.
        If no API key, falls back to simple rule-based approach.
        """
        if not self.client or not courses:
            # Fallback: return courses as-is with generic explanations
            return {
                "courses": [
                    {
                        **course,
                        "explanation": f"This course teaches {', '.join(course.get('skills', []))} which aligns with your goal."
                    }
                    for course in courses
                ]
            }
        
        try:
            # Build prompt for AI
            course_list = "\n".join([
                f"{i+1}. ID={c['id']}, Title=\"{c['title']}\", Difficulty={c['difficulty']}, Duration={c['duration_hours']}h, Skills=[{', '.join(c['skills'])}]"
                for i, c in enumerate(courses)
            ])
            
            prompt = f"""You are a career development advisor. Analyze this user's profile and provide personalized explanations for each course.

User Profile:
- Current Role: {user_profile.get('current_role', 'Not specified')}
- Target Role: {user_profile.get('target_role', 'Not specified')}
- Experience: {user_profile.get('experience_years', 0)} years
- Current Skills: {', '.join(user_profile.get('current_skills', []))}

Courses (already sorted by prerequisites):
{course_list}

For each course, write ONE sentence explaining WHY it's valuable for this user's career transition.

Respond ONLY with valid JSON in this exact format (no markdown, no extra text):
{{"courses": [{{"id": 1, "explanation": "Your explanation here"}}, {{"id": 2, "explanation": "Your explanation here"}}]}}"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract and parse JSON
            ai_response = self.extract_json(response_text)
            
            # Merge AI explanations with course data
            explanation_map = {item["id"]: item["explanation"] for item in ai_response["courses"]}
            
            return {
                "courses": [
                    {
                        **course,
                        "explanation": explanation_map.get(course["id"], "Recommended for your learning path.")
                    }
                    for course in courses
                ]
            }
            
        except Exception as e:
            print(f"AI optimization failed: {e}")
            # Fallback to enhanced rule-based explanations
            return {
                "courses": [
                    {
                        **course,
                        "explanation": self._generate_fallback_explanation(course, user_profile)
                    }
                    for course in courses
                ]
            }
    
    def _generate_fallback_explanation(self, course: dict, user_profile: dict) -> str:
        """
        Generate a better rule-based explanation when AI fails.
        """
        skills = ', '.join(course.get('skills', []))
        difficulty = course.get('difficulty', 'N/A')
        target_role = user_profile.get('target_role', 'your career goals')
        
        if difficulty == 'Beginner':
            return f"This foundational course in {skills} provides essential knowledge for {target_role}."
        elif difficulty == 'Intermediate':
            return f"Building on basics, this course develops practical {skills} skills needed for {target_role}."
        else:
            return f"This advanced course in {skills} prepares you for complex challenges in {target_role}."

