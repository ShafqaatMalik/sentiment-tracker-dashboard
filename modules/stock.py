import yfinance as yf
from datetime import datetime, timedelta, UTC
import pandas as pd

def get_stock_series(ticker="TSLA", start=None, end=None, interval="1h"):
    if start is None:
        start = (datetime.now(UTC) - timedelta(days=7)).date()
    data = yf.download(ticker, start=start, end=end, interval=interval, progress=False, auto_adjust=False)
    if data.empty:
        return data
    data = data[["Close"]].rename(columns={"Close":"price"})
    data.index = data.index.tz_localize(None)
    data = data.reset_index()
    if 'Date' in data.columns:
        data = data.rename(columns={'Date': 'datetime'})
    elif 'index' in data.columns:
        data = data.rename(columns={'index': 'datetime'})
    elif 'Datetime' in data.columns:
        data = data.rename(columns={'Datetime': 'datetime'})
    # If already has 'datetime', do nothing
    return data

def compute_correlation(sent_series_df, stock_df):
    if sent_series_df.empty or stock_df.empty:
        return None
    try:
        # Clean and prepare sentiment data
        s = sent_series_df.copy()
        s["created_utc"] = pd.to_datetime(s["created_utc"])
        
        # Resample sentiment data to hourly
        s_indexed = s.set_index("created_utc")
        s_resampled = s_indexed["sentiment_mean"].resample("1h").mean().reset_index()
        
        # Clean and prepare stock data
        stock_clean = stock_df.copy()
        stock_clean["datetime"] = pd.to_datetime(stock_clean["datetime"])
        
        # Ensure both have clean integer indexes
        s_resampled = s_resampled.reset_index(drop=True)
        stock_clean = stock_clean.reset_index(drop=True)
        
        # Sort both dataframes by time
        s_resampled = s_resampled.sort_values("created_utc").reset_index(drop=True)
        stock_clean = stock_clean.sort_values("datetime").reset_index(drop=True)
        
        # Simple merge on nearest time
        merged_data = []
        for _, sent_row in s_resampled.iterrows():
            sent_time = sent_row["created_utc"]
            time_diffs = abs(stock_clean["datetime"] - sent_time)
            nearest_idx = time_diffs.idxmin()
            
            # Use .iloc[0] to avoid Series float conversion warning
            min_time_diff = time_diffs.loc[nearest_idx]
            if isinstance(min_time_diff, pd.Series):
                min_time_diff = min_time_diff.iloc[0]
                
            if min_time_diff <= pd.Timedelta("1h"):
                stock_row = stock_clean.iloc[nearest_idx]
                
                # Check for NaN values before converting to float
                sentiment_val = sent_row["sentiment_mean"]
                price_val = stock_row["price"]
                
                # Skip rows with NaN values
                if pd.isna(sentiment_val) or pd.isna(price_val):
                    continue
                
                merged_data.append({
                    "created_utc": sent_time,
                    "sentiment_mean": float(sentiment_val),
                    "datetime": stock_row["datetime"],
                    "price": float(price_val)
                })
        
        if not merged_data:
            return None
            
        merged = pd.DataFrame(merged_data)
        
        # Remove any remaining NaN values
        merged = merged.dropna(subset=['sentiment_mean', 'price'])
        
        if merged.empty or len(merged) < 2:
            return None
            
        # Calculate correlation only if we have valid data
        try:
            corr = merged["sentiment_mean"].corr(merged["price"])
            if pd.isna(corr):
                return None
            return corr, merged
        except Exception as corr_error:
            print(f"Correlation calculation error: {corr_error}")
            return None
        
    except Exception as e:
        print(f"Correlation error: {e}")
        return None
