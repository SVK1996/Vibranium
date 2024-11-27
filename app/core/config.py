# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
  DATABASE_URL: str = "postgresql://postgres:postgres@db:5433/transactions_db"
  API_V1_STR: str = "/api/v1"
  PROJECT_NAME: str = "Vibranium"
  SECRET_KEY: str = "your-secret-key-here"
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
  REDIS_URL: str = "redis://redis:6379"

  class Config:
      env_file = ".env"

settings = Settings()