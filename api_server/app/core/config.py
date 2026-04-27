from pydantic_settings import BaseSettings
from typing import Dict, List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # 🧠 App
    APP_NAME: str = "api_server"
    DEBUG: bool = True
    API_KEY: str
    CORS_ALLOW_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://web.postman.co",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # 🤖 AI
    AI_MODEL_NAME: str = "qwen2.5:7b"
    OLLAMA_HOST: str = "http://localhost:11434"

    # 🔎 Job Search API
    JSEARCH_HOST: str = "https://jsearch.p.rapidapi.com"
    RAPIDAPI_KEY: str

    # 🔐 JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # 🗄️ Database
    SQL_DB_URL: str

    # ⚡ Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"

    # 🔥 Dynamic property (cleaner than hardcoding dict)
    @property
    def JSEARCH_HEADERS(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-rapidapi-host": "jsearch.p.rapidapi.com",
            "x-rapidapi-key": self.RAPIDAPI_KEY,
        }

# Singleton settings object
settings = Settings()