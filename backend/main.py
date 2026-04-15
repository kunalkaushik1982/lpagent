# File: c:/Users/work/Documents/lp-agent/backend/main.py
# Purpose: Entry point for the FastAPI application.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine, Base
from backend.api import endpoints

# Create database tables
# In a real production app, we would use Alembic for migrations.
# For this MVP/Phase 3, this ensures tables are created if they don't exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for generating personalized learning paths",
    version=settings.VERSION
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def health_check():
    """
    Health check endpoint to verify backend is running.
    """
    return {"status": "ok", "message": "Learning Plan Agent API is running"}
