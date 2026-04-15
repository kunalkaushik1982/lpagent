# Learning Plan Agent - Masterplan

## 1. App Overview and Objectives
**Product Name:** Learning Plan Agent
**Description:** An intelligent web-based application that generates personalized professional development learning paths for employees. By analyzing an employee's current role, skills, and experience against their desired target role, the agent creates a sequenced, actionable learning roadmap using a hybrid of rule-based logic (for prerequisites) and AI optimization.

**Primary Objectives:**
*   **Bridge Skill Gaps:** specific, actionable paths to move from current state to future goals.
*   **Optimize Learning:** Suggest parallel tracks to accelerate development where possible.
*   **Simplify Discovery:** Navigate complex course catalogs automatically based on relevance and prerequisites.

## 2. Target Audience
*   **Primary Users:** Employees within a single organization.
*   **Scale:** Initially small-scale deployment, but architected to support large employee bases (scalability).

## 3. Core Features & Functionality

### User Profile Management
*   **Input Form:** Users input current Job Role, Years of Experience, Self-assessed Skills, and Target Role.
*   **Authentication:** Simple Username/Password login (Single Role: Employee).

### Intelligent Plan Generation (Hybrid AI)
*   **Rule-Based Engine:** Strictly adheres to hard prerequisites (Course A must be done before Course B).
*   **AI/LLM Layer:** Uses external AI (e.g., OpenAI) to:
    *   Contextualize skill gaps.
    *   Infer soft dependencies.
    *   Optimize the sequence (suggesting parallel tracks).
    *   Generate "Why this course?" explanations.
*   **Output:** A comprehensive timeline view showing the learning path, complete with time estimates and parallel tracks where applicable.
*   **Gap Handling:** Generates full paths regardless of length (no "gap too wide" errors).

### Course Catalog Management
*   **Data Structure:** Rich metadata including Prerequisites (Course & Skill based), Difficulty, Duration, Format, and Granular Skill Tags.
*   **Ingestion:** Import mechanism for existing Excel-based roadmap.
*   **Future Integration:** Architecture ready for future LMS API connections.

### Progress & Interaction
*   **Timeline View:** Visual representation of the learning journey.
*   **Tracking:** Manual "Mark as Complete" function (Hybrid tracking in future).
*   **Plan Modification:** Users can manually add/remove courses or regenerate plans.
*   **Notifications:** Email/In-app reminders for upcoming or overdue courses.

## 4. High-Level Technical Stack

### Backend
*   **Language:** Python
*   **Framework:** FastAPI
    *   *Why:* High performance, easy integration with AI libraries, native async support, auto-generated API docs.
*   **AI Service:** External LLM APIs (e.g., OpenAI / Anthropic via API).

### Frontend
*   **Core:** HTML / CSS / Vanilla JavaScript.
    *   *Strategy:* Simple, lightweight start. Migration path to React available for future complex UI needs.
*   **Design:** Professional, responsive web interface.

### Database
*   **Primary DB:** PostgreSQL.
    *   *Why:* Relational integrity is crucial for `Course -> Prerequisite -> Course` and `User -> LearningPlan -> Course` relationships.
*   **Storage:** Local install for development, scalable cloud instance for production.

## 5. Conceptual Data Model

### Tables / Entities
*   **Users:** `id`, `username`, `password_hash`, `current_role`, `target_role`, `experience_years`.
*   **Skills:** `id`, `name`, `category` (Soft/Technical), `granularity` (High/Low).
*   **Courses:**
    *   `id`, `title`, `description`
    *   `duration_hours`, `difficulty_level`
    *   `format` (Online, In-person), `provider`
*   **Prerequisites:**
    *   `course_id`, `required_course_id` (Self-referential FK)
    *   `course_id`, `required_skill_id` (Skill-based prerequisite)
*   **UserSkills:** `user_id`, `skill_id`, `proficiency_level`.
*   **LearningPlans:** `id`, `user_id`, `generated_at`, `status`.
*   **PlanItems:** `plan_id`, `course_id`, `sequence_order`, `status` (Pending/InProgress/Completed), `estimated_start_date`.

## 6. User Interface Design Principles
*   **Clarity:** The Timeline View is the hero component. It must clearly distinguish between sequential (dependent) and parallel (concurrent) tasks.
*   **Motivation:** Progress bars and visual completion indicators.
*   **Simplicity:** Profile forms should be easy to complete with type-ahead or dropdowns for standardized roles/skills.

## 7. Security Considerations
*   **Authentication:** Secure password hashing (bcrypt/Argon2).
*   **Data Privacy:**
    *   Sanitize data sent to external AI (limit PII sent to LLM functionality).
    *   Secure session management.

## 8. Development Roadmap (Single Phase Build)

Since the strategy is to "Build everything at once", the execution will flow through these technical stages sequentially:

1.  **Environment Setup:** Python, FastAPI, PostgreSQL installation.
2.  **Database Implementation:** Schema creation and **Excel Import Script** development.
3.  **Backend Logic:**
    *   Auth endpoints.
    *   Course retrieval logic.
    *   **The Hybrid Engine:** Developing the Prerequisite Graph Resolver + AI Prompt Engineering for the sequencing logic.
4.  **Frontend Implementation:**
    *   Login / Profile creation pages.
    *   Timeline visualization component.
5.  **Integration & Testing:** Connecting the frontend forms to the backend AI generation.
6.  **Notification System:** Background tasks for email reminders.

## 9. Potential Challenges & Solutions
*   **Challenge:** Circular Dependencies in prerequisites.
    *   *Solution:* Implement DAG (Directed Acyclic Graph) validation during course import to prevent cycles.
*   **Challenge:** AI "Hallucinations" (Suggesting non-existent courses).
    *   *Solution:* Strictly constrain the AI to only select from the provided list of Course IDs/Names in the system context.
*   **Challenge:** Excel Data Quality.
    *   *Solution:* Write a robust cleaning/validation script that runs before DB insertion.

## 10. Future Expansion Possibilities
*   **UI Upgrade:** Migration to React/Vue for more interactive drag-and-drop planning.
*   **LMS Integration:** Direct APIs (Workday/Cornerstone) to sync course completions automatically.
*   **Social Learning:** "See what peers in my role are learning."
*   **Manager Dashboard:** View team progress and assign mandatory courses.
