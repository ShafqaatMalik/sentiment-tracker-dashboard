import pytest
from modules.data_utils import load_data, aggregate_sentiment

def test_load_data():
    df = load_data()
    assert df is not None
    assert hasattr(df, 'shape')

def test_aggregate_sentiment_empty():
    import pandas as pd
    df = pd.DataFrame()
    agg = aggregate_sentiment(df)
    assert agg.empty
