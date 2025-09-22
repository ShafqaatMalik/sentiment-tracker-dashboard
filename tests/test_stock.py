from modules.stock import get_stock_series

def test_get_stock_series_default():
    df = get_stock_series()
    assert df is not None
    assert hasattr(df, 'shape')
