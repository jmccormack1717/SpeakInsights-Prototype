"""Application configuration"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"
    
    # Database Configuration
    database_type: str = "sqlite"
    database_path: str = "./data"
    
    # Application Configuration
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Auth / JWT configuration (sane defaults for a demo app)
    jwt_secret: str = os.environ.get("JWT_SECRET", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # CORS Configuration - handle comma-separated string from env
    cors_origins: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000,https://speakinsights-prototype.onrender.com"
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            # Default origins if empty
            if not origins:
                origins = [
                    "http://localhost:5173",
                    "http://localhost:3000",
                    "https://speakinsights-prototype.onrender.com"
                ]
            return origins
        if isinstance(v, list):
            return v
        # Default fallback
        return [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://speakinsights-prototype.onrender.com"
        ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

