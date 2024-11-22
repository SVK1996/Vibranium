# app/models/transaction.py
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from ..database import Base

class Transaction(Base):
  __tablename__ = "transactions"

  id = Column(Integer, primary_key=True)
  amount = Column(Float, nullable=False)
  type = Column(String, nullable=False)
  parent_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

  # Indexes for better performance
  __table_args__ = (
      Index('idx_transaction_type', 'type'),
      Index('idx_transaction_parent_id', 'parent_id'),
      Index('idx_transaction_user_id', 'user_id'),
  )

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True)
  email = Column(String, unique=True, index=True, nullable=False)
  hashed_password = Column(String, nullable=False)
  is_active = Column(Boolean, default=True)