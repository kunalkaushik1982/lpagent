# Learning Path Agent - Architecture & Code Flow

This document provides a complete overview of the codebase, visualizing the data flow from the frontend user interaction to the backend logic and database.

## High-Level Architecture

The application follows a standard **Client-Server** architecture:

- **Frontend**: Vanilla HTML/JS/CSS (No frameworks).
- **Backend**: Python FastAPI.
- **Database**: SQLite (SQLAlchemy ORM).
- **External Services**: OpenAI API (for logic inference).

## Code Flow Visualization

### 1. Project Structure & Key Files

```mermaid
graph TD
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef db fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;

    subgraph User Interaction [Frontend Layer]
        Index[index.html<br>Login/Register]:::frontend
        Dashboard[dashboard.html<br>Main Interface]:::frontend
        AppJS[js/app.js<br>API Client & DOM Logic]:::frontend
    end

    subgraph Server Logic [Backend Layer]
        Main[main.py<br>App Entry Point]:::backend
        Router[api/endpoints.py<br>REST Routes]:::backend
        Engine[services/engine_service.py<br>Orchestration Logic]:::backend
        AI[services/ai_service.py<br>LLM Integration]:::backend
        Models[models.py<br>Data Models]:::backend
        DB_Conn[database.py<br>Connection]:::backend
    end

    subgraph Data [Persistence Layer]
        SQLite[(lp_agent.db)]:::db
    end

    Index --> AppJS
    Dashboard --> AppJS
    AppJS -- "HTTP Request (Fetch)" --> Main
    Main --> Router
    Router -- "Generate Plan" --> Engine
    Router -- "CRUD Operations" --> Models
    Engine -- "Infer Prereqs / Explain" --> AI
    Engine -- "Query / Save" --> Models
    Models -- "SQLAlchemy" --> DB_Conn
    DB_Conn -- "Read/Write" --> SQLite
```

### 2. Detailed "Generate Plan" Sequence

This is the core workflow: taking a user profile and creating a personalized learning path.

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant JS as app.js
    participant API as API (endpoints.py)
    participant LE as LearningEngine
    participant AI as AIService
    participant DB as Database

    U->>JS: Clicks "Generate Plan"
    JS->>API: POST /plans/generate {user_id}
    API->>DB: Get User Profile (skills, role)
    API->>LE: generate_learning_path(user_id)
    
    activate LE
    LE->>LE: Identify Skill Gaps
    LE->>DB: Query Relevant Courses
    
    rect rgb(240, 248, 255)
        note over LE, AI: Course Processing Loop
        LE->>LE: Check Prerequisites (Manual)
        opt If inference needed
            LE->>AI: infer_prerequisites(course)
            AI-->>LE: Return Prereq IDs
        end
    end
    
    LE->>LE: Topological Sort (Build Graph)
    
    rect rgb(255, 250, 240)
        note over LE, AI: Optimization
        LE->>AI: optimize_sequence(sorted_courses)
        AI-->>LE: Returns Optimized + Explained Plan
    end
    
    LE->>DB: Save LearningPlan & PlanItems
    LE-->>API: Return JSON Plan
    deactivate LE
    
    API-->>JS: JSON Response
    JS->>U: Render Timeline UI
```

## File Responsibilities

| Directory | File | Responsibility |
|-----------|------|----------------|
| **Backend** | `main.py` | Initializes FastAPI app, CORS, and database tables. |
| | `api/endpoints.py` | Defines URL routes (`/login`, `/plans/generate`) and calls appropriate services. |
| | `services/engine_service.py` | **Core Logic**. Handles graph algorithms (topological sort), prerequisite checking, and orchestrates the plan creation. |
| | `services/ai_service.py` | Interfaces with OpenAI to add intelligence (explanations, dynamic prerequisite discovery). |
| | `models.py` | Defines the database schema (`User`, `Course`, `LearningPlan`). |
| | `database.py` | Handles SQLite connection and session management. |
| **Frontend** | `index.html` | Login and Registration forms. |
| | `dashboard.html` | Main user interface waiting for dynamic content. |
| | `js/app.js` | Handles button clicks, API calls, and dynamically creating HTML elements to show the plan. |

## Data Models (ER Diagram)

```mermaid
erDiagram
    User ||--o{ LearningPlan : has
    User {
        int id
        string username
        string target_role
        json skills
    }
    
    LearningPlan ||--|{ PlanItem : contains
    LearningPlan {
        int id
        string status
        datetime created_at
    }
    
    Course ||--o{ PlanItem : included_in
    Course {
        int id
        string title
        string difficulty
        json skills
    }
    
    PlanItem {
        int id
        string status
        int sequence_order
    }
    
    Course }|--|{ Course : prerequisites
```
