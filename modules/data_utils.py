import os
import pandas as pd
import json
from modules.config import DATA_CSV, ROLLING_WINDOW_MINUTES

def persist_row(row, csv_path=DATA_CSV):
    df = pd.DataFrame([row])
    if not os.path.exists(csv_path):
        df.to_csv(csv_path, index=False)
    else:
        df.to_csv(csv_path, mode="a", header=False, index=False)

def load_data(csv_path=DATA_CSV):
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    df = pd.read_csv(csv_path, parse_dates=["created_utc"])
    df = df.sort_values("created_utc")
    return df

def aggregate_sentiment(df, window_minutes=ROLLING_WINDOW_MINUTES):
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["created_utc"] = pd.to_datetime(df["created_utc"])
    df.set_index("created_utc", inplace=True)
    res = df["sentiment_compound"].resample(f"{window_minutes}min").agg(["mean","count"])
    res = res.rename(columns={"mean":"sentiment_mean","count":"message_count"})
    res = res.reset_index()
    return res
