import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json

nltk.download("vader_lexicon")
vader = SentimentIntensityAnalyzer()

def compute_sentiment(text):
    s = vader.polarity_scores(text)
    return s
