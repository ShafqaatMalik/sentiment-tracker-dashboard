from modules.sentiment import compute_sentiment

def test_compute_sentiment_positive():
    result = compute_sentiment("I love this!")
    assert result['compound'] > 0

def test_compute_sentiment_negative():
    result = compute_sentiment("I hate this!")
    assert result['compound'] < 0

def test_compute_sentiment_neutral():
    result = compute_sentiment("This is a table.")
    assert abs(result['compound']) < 0.1
