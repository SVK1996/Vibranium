# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
  DATABASE_URL: str = "postgresql://username:password@localhost/transactions_db"
  API_V1_STR: str = ""
  PROJECT_NAME: str = "Transaction Service"
  SECRET_KEY: str = "your-secret-key-here"
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

  class Config:
      env_file = ".env"

settings = Settings()