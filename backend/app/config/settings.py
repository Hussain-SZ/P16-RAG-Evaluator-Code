from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App Configuration
    app_name: str = "RAG Evaluator API"
    version: str = "1.0.0"
    debug: bool = False
    
    # Database Configuration
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "rag_evaluator")
    
    # JWT Configuration
    jwt_secret: str = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-here-make-it-long-and-random")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = 30
    reset_token_expire_minutes: int = 10
    
    # Email Configuration
    sendgrid_api_key: Optional[str] = os.getenv("SENDGRID_API_KEY")
    sendgrid_from_email: str = os.getenv("SENDGRID_FROM_EMAIL", "noreply@ragevaluator.com")
    
    # AI Configuration
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # CORS Configuration
    cors_origins: list = ["*"]  # In production, specify exact origins
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()