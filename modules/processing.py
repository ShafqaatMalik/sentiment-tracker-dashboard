import time
import json
import threading
from modules.sentiment import compute_sentiment
from modules.data_utils import persist_row
from modules.reddit_client import q


def processing_loop():
    while True:
        try:
            item = q.get(timeout=1)
        except:
            time.sleep(0.5)
            continue
        try:
            full = compute_sentiment(item["text"])
            compound = full["compound"]
            row = {
                "id": item["id"],
                "type": item["type"],
                "subreddit": item["subreddit"],
                "author": item["author"],
                "text": item["text"].replace("\n"," "),
                "created_utc": item["created_utc"].isoformat(),
                "score": item.get("score",0),
                "sentiment_compound": compound,
                "sentiment_detail": json.dumps(full),
                "permalink": item.get("permalink",""),
            }
            persist_row(row)
        except Exception as e:
            print("Processing error:", e)


def start_processing():
    tproc = threading.Thread(target=processing_loop, daemon=True)
    tproc.start()
    return tproc