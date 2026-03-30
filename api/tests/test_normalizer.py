import pytest
import pandas as pd
from api.core.normalizer import FinancialNormalizer

@pytest.fixture
def normalizer():
    return FinancialNormalizer()

def test_clean_amount(normalizer):
    assert normalizer.clean_amount("$1,200.50") == 1200.50
    assert normalizer.clean_amount("- 45.00") == -45.00
    assert normalizer.clean_amount("1,000.00") == 1000.00
    assert normalizer.clean_amount(None) == 0.0

def test_parse_date(normalizer):
    # Test common formats
    assert normalizer.parse_date("2023-10-01").year == 2023
    assert normalizer.parse_date("02/10/2023").day == 2
    assert normalizer.parse_date("15-Oct-2023").month == 10
    # Invalid date should return None (allowing for anomaly flagging)
    assert normalizer.parse_date("invalid-date") is None

def test_normalize_csv(normalizer):
    data = {
        'Date': ['2023-10-01', 'invalid'],
        'Amount': ['$15.50', ''],
        'Description': ['Coffee', 'No Category']
    }
    df = pd.DataFrame(data)
    txns, anomalies = normalizer.normalize_csv(df, "test-source")
    
    assert len(txns) == 2
    assert txns[0].amount == 15.50
    assert txns[0].is_anomaly is False
    
    # Second row has multiple issues: invalid date and empty amount
    assert txns[1].is_anomaly is True
    assert "Invalid date format" in txns[1].anomalies[0]
    assert len(anomalies) == 1
