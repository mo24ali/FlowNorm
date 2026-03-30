from sqlalchemy import Column, String, Float, Date, Boolean, JSON, Integer, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"
    id = Column(String, primary_key=True)
    institution_id = Column(String)
    account_type = Column(String)
    balance = Column(Float)
    currency = Column(String)
    status = Column(String, default="active")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"))
    amount = Column(Float)
    currency = Column(String)
    date = Column(Date)
    description = Column(String)
    normalized_category = Column(String)
    is_anomaly = Column(Boolean, default=False)
    anomalies = Column(JSON) # List of anomaly strings
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class IngestionTask(Base):
    __tablename__ = "ingestion_tasks"
    id = Column(String, primary_key=True)
    status = Column(String, default="pending") # pending, processing, completed, failed
    source = Column(String)
    retry_count = Column(Integer, default=0)
    error_log = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)
