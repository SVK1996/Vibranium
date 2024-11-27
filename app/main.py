# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import transaction
from app.core import auth
from app.core.config import settings
from app.core.cache import setup_cache
from app.core.logging import setup_logging

app = FastAPI(
  title=settings.PROJECT_NAME,
  openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
  setup_logging()
  await setup_cache()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(
  transaction.router,
  prefix="/transactionservice",
  tags=["transactions"]
)

@app.get("/health")
async def health_check():
  return {"status": "healthy"}