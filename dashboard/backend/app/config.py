from typing import List
from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    ENV: str = "development"

    # App
    APP_NAME: str = "Discord Dashboard"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]

    # Discord OAuth
    DISCORD_CLIENT_ID: str
    DISCORD_CLIENT_SECRET: str
    DISCORD_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data.db"

    # Redis (optional)
    REDIS_URL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
