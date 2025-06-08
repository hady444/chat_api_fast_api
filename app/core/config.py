from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "chat_microservice"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_TTL: int = 3600  # 1 hour in seconds
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Gemini API
    GEMINI_API_KEY: str
    
    # App
    DEBUG: bool = True
    PROJECT_NAME: str = "Chat Microservice"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()