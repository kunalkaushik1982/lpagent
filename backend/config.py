# File: c:/Users/work/Documents/lp-agent/backend/config.py
# Purpose: Configuration settings (environment variables).

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Learning Plan Agent"
    VERSION: str = "0.1.0"
    
    # Database (Default to SQLite for MVP)
    DATABASE_URL: str = "sqlite:///./lp_agent.db"
    
    # External AI API
    OPENAI_API_KEY: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
