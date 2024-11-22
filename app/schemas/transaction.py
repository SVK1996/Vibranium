# app/schemas/transaction.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

ValErr = 'Amount must be positive'

class TransactionBase(BaseModel):
  amount: float = Field(..., gt=0)
  type: str = Field(..., min_length=1, max_length=50)
  parent_id: Optional[int] = None

  @validator('amount')
  def validate_amount(cls, v):
      if v <= 0:
          raise ValueError(ValErr)
      return v

class TransactionCreate(TransactionBase):
  pass

class TransactionResponse(TransactionBase):
  id: int
  created_at: datetime
  user_id: int

  class Config:
      orm_mode = True

class StatusResponse(BaseModel):
  status: str

class SumResponse(BaseModel):
  sum: float

class TransactionTypeResponse(BaseModel):
  transaction_ids: List[int]