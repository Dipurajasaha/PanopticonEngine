from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="Viewer") # roles: Admin, Analyst, Viewer
    
    records = relationship("FinanceRecord", back_populates="owner")



class FinanceRecord(Base):
    __tablename__ = "finance_records"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    record_type = Column(String, nullable=False) # 'Income' or 'Expense'
    category = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False) # soft delete flag
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="records")
    transaction_analysis = relationship("TransactionAnalysis", back_populates="record", uselist=False)



class TransactionAnalysis(Base):
    __tablename__ = "transaction_analysis"
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("finance_records.id"))
    
    predicted_category = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, nullable=True)

    record = relationship("FinanceRecord", back_populates="transaction_analysis")