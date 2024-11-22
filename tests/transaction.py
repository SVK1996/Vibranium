# tests/test_transactions.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Transaction

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
  SQLALCHEMY_DATABASE_URL,
  connect_args={"check_same_thread": False},
  poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
  Base.metadata.create_all(bind=engine)
  try:
      db = TestingSessionLocal()
      yield db
  finally:
      db.close()
      Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
  def override_get_db():
      try:
          yield test_db
      finally:
          test_db.close()

  app.dependency_overrides[get_db] = override_get_db
  return TestClient(app)

class TestTransactionScenarios:
  """Test specific transaction scenarios as per the requirements"""

  def test_complete_transaction_flow(self, client):
      """
      Test the complete flow of transactions as specified in the requirements:
      1. Create transaction 10 (cars, 5000)
      2. Create transaction 11 (shopping, 10000, parent_id=10)
      3. Get transactions by type 'cars'
      4. Get sum for transaction 10
      5. Get sum for transaction 11
      """

      # Step 1: Create transaction 10
      response = client.put(
          "/transactionservice/transaction/10",
          json={
              "amount": 5000,
              "type": "cars"
          }
      )
      assert response.status_code == 200
      assert response.json() == {"status": "ok"}

      # Step 2: Create transaction 11 with parent_id 10
      response = client.put(
          "/transactionservice/transaction/11",
          json={
              "amount": 10000,
              "type": "shopping",
              "parent_id": 10
          }
      )
      assert response.status_code == 200
      assert response.json() == {"status": "ok"}

      # Step 3: Get transactions by type 'cars'
      response = client.get("/transactionservice/types/cars")
      assert response.status_code == 200
      assert response.json() == [10]  # Should only return transaction 10

      # Step 4: Get sum for transaction 10
      response = client.get("/transactionservice/sum/10")
      assert response.status_code == 200
      assert response.json() == {"sum": 15000}  # 5000 + 10000

      # Step 5: Get sum for transaction 11
      response = client.get("/transactionservice/sum/11")
      assert response.status_code == 200
      assert response.json() == {"sum": 10000}  # Only includes transaction 11

  def test_individual_endpoints(self, client):
      """Test each endpoint individually with verification steps"""

      # Test creating transaction 10
      response = client.put(
          "/transactionservice/transaction/10",
          json={
              "amount": 5000,
              "type": "cars"
          }
      )
      assert response.status_code == 200
      assert response.json() == {"status": "ok"}

      # Verify transaction 10 was created correctly
      response = client.get("/transactionservice/transaction/10")
      assert response.status_code == 200
      assert response.json() == {
          "amount": 5000,
          "type": "cars",
          "parent_id": None
      }

      # Test creating transaction 11
      response = client.put(
          "/transactionservice/transaction/11",
          json={
              "amount": 10000,
              "type": "shopping",
              "parent_id": 10
          }
      )
      assert response.status_code == 200
      assert response.json() == {"status": "ok"}

      # Verify transaction 11 was created correctly
      response = client.get("/transactionservice/transaction/11")
      assert response.status_code == 200
      assert response.json() == {
          "amount": 10000,
          "type": "shopping",
          "parent_id": 10
      }

  def test_error_cases(self, client):
      """Test error cases and edge scenarios"""

      # Test getting non-existent transaction
      response = client.get("/transactionservice/transaction/999")
      assert response.status_code == 404

      # Test creating transaction with non-existent parent
      response = client.put(
          "/transactionservice/transaction/12",
          json={
              "amount": 5000,
              "type": "cars",
              "parent_id": 999
          }
      )
      assert response.status_code == 404

      # Test invalid amount
      response = client.put(
          "/transactionservice/transaction/13",
          json={
              "amount": "invalid",
              "type": "cars"
          }
      )
      assert response.status_code == 422

      # Test missing required fields
      response = client.put(
          "/transactionservice/transaction/14",
          json={
              "type": "cars"
          }
      )
      assert response.status_code == 422

  def test_type_queries(self, client):
      """Test queries for transaction types"""

      # Create multiple transactions of different types
      transactions = [
          {"id": 10, "amount": 5000, "type": "cars"},
          {"id": 11, "amount": 10000, "type": "shopping", "parent_id": 10},
          {"id": 12, "amount": 7000, "type": "cars"},
      ]

      for trans in transactions:
          client.put(
              f"/transactionservice/transaction/{trans['id']}",
              json={k: v for k, v in trans.items() if k != 'id'}
          )

      # Test getting all 'cars' transactions
      response = client.get("/transactionservice/types/cars")
      assert response.status_code == 200
      assert sorted(response.json()) == [10, 12]

      # Test getting 'shopping' transactions
      response = client.get("/transactionservice/types/shopping")
      assert response.status_code == 200
      assert response.json() == [11]

      # Test getting non-existent type
      response = client.get("/transactionservice/types/nonexistent")
      assert response.status_code == 200
      assert response.json() == []