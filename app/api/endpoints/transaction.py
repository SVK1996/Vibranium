# app/api/endpoints/transaction.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi_cache.decorator import cache
from loguru import logger
from app.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionTypeResponse, SumResponse, StatusResponse
from app.core.auth import get_current_active_user
from sqlalchemy import text

router = APIRouter()

@router.put("/transaction/{transaction_id}", response_model=StatusResponse)
async def create_transaction(
  transaction_id: int,
  transaction: TransactionCreate,
  db: Session = Depends(get_db),
  current_user: int = Depends(get_current_active_user)
):
  try:
        # Log incoming data
        logger.debug(f"Creating transaction with ID: {transaction_id}")
        logger.debug(f"Transaction data: {transaction.dict()}")

        
        existing_transaction = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()
        if existing_transaction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transaction with id {transaction_id} already exists"
            )

        # Validate parent_id if provided
        if transaction.parent_id:
            parent = db.query(Transaction).filter(
                Transaction.transaction_id == transaction.parent_id,
                Transaction.user_id == current_user.id
            ).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent transaction not found"
                )
        
        if check_circular_reference(db, transaction_id, transaction.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transaction {transaction_id} cannot reference itself as parent"
            )

        db_transaction = Transaction(
            transaction_id=transaction_id,
            amount=transaction.amount,
            type=transaction.type,
            parent_id=transaction.parent_id,
            user_id=current_user.id
        )

        # Log the transaction object
        logger.debug(f"Created transaction object: {db_transaction.__dict__}")

        db.add(db_transaction)  
        db.commit()

        logger.info(f"Transaction {transaction_id} created/updated by user {current_user.id}")
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
  current_user: int = Depends(get_current_active_user)
):
  transaction = db.query(Transaction).filter(
      Transaction.transaction_id == transaction_id,
      Transaction.user_id == current_user.id
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
  current_user: int = Depends(get_current_active_user)
):
  """
  Get all transaction IDs of a specific type.
  Returns a list of transaction IDs.
  """
  try:
      transactions = db.query(Transaction.transaction_id).filter(
          Transaction.type == transaction_type,
          Transaction.user_id == current_user.id
      ).all()

      # Extract IDs from the query result
      transaction_ids = [t.transaction_id for t in transactions]

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
  current_user: int = Depends(get_current_active_user)
):
  """
  Get the sum of the specified transaction and all its child transactions.
  Returns the total sum of amounts.
  """
  try:
      # First, verify the transaction exists and belongs to the user
      transaction = db.query(Transaction).filter(
          Transaction.transaction_id == transaction_id,
          Transaction.user_id == current_user.id
      ).first()

      if not transaction:
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND,
              detail="Transaction not found"
          )

      # Recursive CTE to get all child transactions
      recursive_query = text("""
      WITH RECURSIVE transaction_tree AS (
          -- Base case: the initial transaction
          SELECT transaction_id, amount, parent_id, user_id
          FROM transactions
          WHERE transaction_id = :transaction_id AND user_id = :user_id

          UNION ALL

          -- Recursive case: all child transactions
          SELECT t.transaction_id, t.amount, t.parent_id, t.user_id
          FROM transactions t
          INNER JOIN transaction_tree tt ON t.parent_id = tt.transaction_id
          WHERE t.user_id = :user_id
      )
      SELECT COALESCE(SUM(amount), 0) as total_sum
      FROM transaction_tree;
      """)

      result = db.execute(
          recursive_query,
          {"transaction_id": transaction_id, "user_id": current_user.id}
      ).scalar()

      if result is None:
          raise HTTPException(
              status_code=404,
              detail="Transaction not found"
          )

      logger.info(f"Calculated sum for transaction {transaction_id}: {result}")
      return SumResponse(sum=result)
  except Exception as e:
      logger.error(f"Error calculating transaction sum: {str(e)}")
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail="Error calculating sum"
      )

def check_circular_reference(db: Session, transaction_id: int, parent_id: int) -> bool:
  """Check if adding this parent would create a circular reference"""
  current = parent_id
  while current is not None:
      if current == transaction_id:
          return True
      parent = db.query(Transaction).filter(
          Transaction.transaction_id == current
      ).first()
      current = parent.parent_id if parent else None
  return False