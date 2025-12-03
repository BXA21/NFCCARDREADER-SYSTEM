"""
Application configuration management.
Loads settings from environment variables and provides type-safe access.
"""

import os
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Database - Railway uses DATABASE_URL, fallback to SQLite for local dev
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        os.getenv("DATABASE_PRIVATE_URL", "sqlite+aiosqlite:///./nfc_attendance.db")
    )
    
    # Security - Generate a default for development, MUST be set in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-123!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Application
    APP_NAME: str = "NFC Attendance System"
    COMPANY_NAME: str = "Your Company"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS - Allow Netlify domain and localhost
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,https://*.netlify.app"
    )
    
    # Railway specific
    PORT: int = int(os.getenv("PORT", "8000"))
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()



