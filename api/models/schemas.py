from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, List, Dict, Any
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ANOMALY = "anomaly"

class TransactionBase(BaseModel):
    amount: float
    currency: str = Field(..., min_length=3, max_length=3)
    date: date
    description: str
    normalized_category: Optional[str] = "Uncategorized"
    
    @field_validator('amount')
    def validate_amount(cls, v):
        if not isinstance(v, (int, float)):
             raise ValueError('Must be numeric')
        return round(float(v), 2)

class TransactionNormalized(TransactionBase):
    id: Optional[str] = None
    account_id: str
    raw_data: Optional[Dict[str, Any]] = None
    is_anomaly: bool = False
    anomalies: List[str] = []

class AccountNormalized(BaseModel):
    id: str
    institution_id: str
    account_type: str
    balance: float
    currency: str
    status: str = "active"

class IngestionTask(BaseModel):
    id: str
    status: Status = Status.PENDING
    source: str
    retry_count: int = 0
    error_log: Optional[str] = None
    created_at: date
