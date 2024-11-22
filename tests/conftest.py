# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from fastapi.testclient import TestClient

SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/test_db"

@pytest.fixture(scope="session")
def db_engine():
  engine = create_engine(SQLALCHEMY_DATABASE_URL)
  Base.metadata.create_all(bind=engine)
  yield engine
  Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
  session = SessionLocal()
  yield session
  session.close()

@pytest.fixture(scope="module")
def client():
  with TestClient(app) as c:
      yield c