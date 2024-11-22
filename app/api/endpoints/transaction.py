# app/api/endpoints/transaction.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi_cache.decorator import cache
from loguru import logger
from ...database import get_db
from ...models.transaction import Transaction
from ...schemas.transaction import TransactionCreate, TransactionResponse, TransactionTypeResponse, SumResponse, StatusResponse
from ...core.auth import get_current_user

router = APIRouter()

@router.put("/transaction/{transaction_id}", response_model=StatusResponse)
async def create_transaction(
  transaction_id: int,
  transaction: TransactionCreate,
  db: Session = Depends(get_db),
  current_user: int = Depends(get_current_user)
):
  try:
      # Validate parent_id if provided
      if transaction.parent_id:
          parent = db.query(Transaction).filter(
              Transaction.id == transaction.parent_id,
              Transaction.user_id == current_user
          ).first()
          if not parent:
              raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail="Parent transaction not found"
              )

      db_transaction = Transaction(
          id=transaction_id,
          amount=transaction.amount,
          type=transaction.type,
          parent_id=transaction.parent_id,
          user_id=current_user
      )

      db.merge(db_transaction)  # merge instead of add to handle updates
      db.commit()

      logger.info(f"Transaction {transaction_id} created/updated by user {current_user}")
      return StatusResponse(status="ok")
  except Exception as e:
      logger.error(f"Error creating transaction: {str(e)}")
      db.rollback()
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail="Error processing transaction"
      )

@router.get("/transaction/{transaction_id}", response_model=TransactionResponse)
@cache(expire=300)  # Cache for 5 minutes
async def get_transaction(
  transaction_id: int,
  db: Session = Depends(get_db),
  current_user: int = Depends(get_current_user)
):
  transaction = db.query(Transaction).filter(
      Transaction.id == transaction_id,
      Transaction.user_id == current_user
  ).first()

  if not transaction:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="Transaction not found"
      )

  return transaction

@router.get("/types/{transaction_type}", response_model=List[int])
@cache(expire=300)
async def get_transactions_by_type(
  transaction_type: str,
  db: Session = Depends(get_db),
  current_user: int = Depends(get_current_user)
):
  """
  Get all transaction IDs of a specific type.
  Returns a list of transaction IDs.
  """
  try:
      transactions = db.query(Transaction.id).filter(
          Transaction.type == transaction_type,
          Transaction.user_id == current_user
      ).all()

      # Extract IDs from the query result
      transaction_ids = [t.id for t in transactions]

      logger.info(f"Retrieved {len(transaction_ids)} transactions of type {transaction_type}")
      return transaction_ids
  except Exception as e:
      logger.error(f"Error retrieving transactions by type: {str(e)}")
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail="Error retrieving transactions"
      )

@router.get("/sum/{transaction_id}", response_model=SumResponse)
@cache(expire=300)
async def get_transaction_sum(
  transaction_id: int,
  db: Session = Depends(get_db),
  current_user: int = Depends(get_current_user)
):
  """
  Get the sum of the specified transaction and all its child transactions.
  Returns the total sum of amounts.
  """
  try:
      # First, verify the transaction exists and belongs to the user
      transaction = db.query(Transaction).filter(
          Transaction.id == transaction_id,
          Transaction.user_id == current_user
      ).first()

      if not transaction:
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND,
              detail="Transaction not found"
          )

      # Recursive CTE to get all child transactions
      recursive_query = """
      WITH RECURSIVE transaction_tree AS (
          -- Base case: the initial transaction
          SELECT id, amount, parent_id, user_id
          FROM transactions
          WHERE id = :transaction_id AND user_id = :user_id

          UNION ALL

          -- Recursive case: all child transactions
          SELECT t.id, t.amount, t.parent_id, t.user_id
          FROM transactions t
          INNER JOIN transaction_tree tt ON t.parent_id = tt.id
          WHERE t.user_id = :user_id
      )
      SELECT COALESCE(SUM(amount), 0) as total_sum
      FROM transaction_tree;
      """

      result = db.execute(
          recursive_query,
          {"transaction_id": transaction_id, "user_id": current_user}
      ).scalar()

      logger.info(f"Calculated sum for transaction {transaction_id}: {result}")
      return SumResponse(sum=result)
  except Exception as e:
      logger.error(f"Error calculating transaction sum: {str(e)}")
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail="Error calculating sum"
      )