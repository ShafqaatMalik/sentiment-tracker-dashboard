import os
import json

CONFIG_PATH = "config.json"
DATA_CSV = "reddit_sentiment.csv"

TRACK_KEYWORDS = ["Tesla", "TSLA", "Apple", "AAPL", "iPhone", "PlayStation"]
TRACK_SUBREDDITS = [
    "stocks", "investing", "wallstreetbets", "technology", "gadgets",
    "news", "worldnews", "politics", "gaming", "sports", "music", "movies", "science", "health", "education", "travel", "food", "memes", "funny", "AskReddit", "dataisbeautiful", "CryptoCurrency", "MachineLearning", "ArtificialIntelligence", "GPT3", "GPT4", "OpenAI", "Python", "learnprogramming", "programming", "Space", "TeslaMotors", "apple", "Google", "Nvidia", "Netflix", "Bitcoin", "Ethereum", "Solana", "Cardano", "Dogecoin", "Meta", "Facebook", "ElonMusk", "AAPL", "TSLA", "MSFT", "AMZN", "NVDA", "NFLX", "GOOGL", "META"
]
REDDIT_STREAM_POLL = 5
ROLLING_WINDOW_MINUTES = 60

def load_config(path=CONFIG_PATH):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {
        "client_id": os.getenv("REDDIT_CLIENT_ID"),
        "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
        "user_agent": os.getenv("REDDIT_USER_AGENT"),
    }
