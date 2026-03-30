import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re
import uuid
from api.models.schemas import TransactionNormalized, Status

class FinancialNormalizer:
    """Base class for normalizing financial data."""
    
    # Common date formats to try for self-healing
    DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%Y", "%Y/%m/%d"]

    @staticmethod
    def clean_amount(val: Any) -> float:
        """Sanitizes messy amount strings like '$1,200.50'."""
        if pd.isna(val) or val == "":
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        
        # Remove currency symbols and formatting characters
        clean_val = re.sub(r"[^\d.-]", "", str(val))
        try:
            return float(clean_val)
        except ValueError:
            return 0.0

    @staticmethod
    def parse_date(date_str: Any) -> Optional[datetime]:
        """Self-healing date parser that attempts multiple common formats."""
        if pd.isna(date_str) or date_str == "":
            return None
        
        # If it's already a datetime object, return it
        if isinstance(date_str, (datetime, pd.Timestamp)):
            return date_str.to_pydatetime() if hasattr(date_str, 'to_pydatetime') else date_str

        # Try common formats
        for fmt in FinancialNormalizer.DATE_FORMATS:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        
        # If all else fails, try pandas to_datetime which is more robust
        try:
            return pd.to_datetime(date_str).to_pydatetime()
        except:
            return None

    def normalize_csv(self, df: pd.DataFrame, source_id: str) -> Tuple[List[TransactionNormalized], List[Dict]]:
        """Normalize a raw DataFrame into standard transactions."""
        normalized_data = []
        anomalies = []

        # Map messy column names to standardized ones (MVP simple mapping)
        # In a real system, this would be more dynamic (or using LLMs/Mapping engines)
        column_map = {
            'Date': 'date', 'Txn Date': 'date', 'Transaction Date': 'date', 'period': 'date',
            'Amount': 'amount', 'Value': 'amount', 'Debit/Credit': 'amount',
            'Description': 'description', 'Narrative': 'description', 'Details': 'description',
            'Category': 'normalized_category', 'Type': 'normalized_category'
        }
        
        # Renaming columns for easier processing
        df = df.rename(columns={c: column_map[c] for c in df.columns if c in column_map})

        for idx, row in df.iterrows():
            row_anomalies = []
            
            # 1. Clean Amount
            amount = self.clean_amount(row.get('amount'))
            if amount == 0.0:
                row_anomalies.append("Zero/Null amount detected")
            
            # 2. Parse Date
            dt = self.parse_date(row.get('date'))
            if not dt:
                row_anomalies.append(f"Invalid date format: {row.get('date')}")
                # Use current date as placeholder for anomaly but mark it for self-healing/manual review
                dt = datetime.now()

            # 3. Handle Missing Descriptions
            desc = str(row.get('description', 'No description')).strip()
            if not desc:
                row_anomalies.append("Missing description")
                desc = "Unknown Transaction"

            # Check if this row is an anomaly
            is_anomaly = len(row_anomalies) > 0
            
            txn = TransactionNormalized(
                id=str(uuid.uuid4()),
                account_id=source_id,
                amount=amount,
                currency="USD", # Default for MVP
                date=dt.date(),
                description=desc,
                normalized_category=row.get('normalized_category', 'Uncategorized'),
                is_anomaly=is_anomaly,
                anomalies=row_anomalies,
                raw_data=row.to_dict()
            )
            
            normalized_data.append(txn)
            if is_anomaly:
                anomalies.append(txn.model_dump())

        return normalized_data, anomalies
