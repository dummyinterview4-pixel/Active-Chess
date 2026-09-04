from pydantic_settings import BaseSettings
import os
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/active_chess"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"

    def model_post_init(self, __context):
        if self.ENVIRONMENT.lower() == "production" and self.SECRET_KEY == "your-secret-key-change-this-in-production":
            raise ValueError("SECRET_KEY must be set to a strong random value in production")

settings = Settings()
