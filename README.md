
# Reddit Sentiment Tracker
A modular social media sentiment tracking app for Reddit, featuring real-time and historical sentiment analysis, interactive dashboards, and stock correlation.

## Demo Video
Watch a demo of the Sentiment Tracking Dashboard:
[Click here to watch the demo on Google Drive](https://drive.google.com/file/d/1bVjBr8trSxjwI4f4FDGCJsPhwwCLzNlh/view?usp=sharing)

## Features
- Fetches posts and comments using the Reddit API
- Links sentiment trends with stock data
- Sentiment scoring using VADER
- Interactive Streamlit dashboard - visualizes sentiment and market movement 

## Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure Reddit API credentials in `config.json`
4. Run: `streamlit run sentiment_tracker.py`

## Configuration
- Edit `config.json` for Reddit API keys and settings
- Update tracked keywords/subreddits in `modules/config.py`

## Usage
- Use the dashboard to start live streams, fetch historical data, and analyze sentiment trends

## Troubleshooting
- Ensure all dependencies in `requirements.txt` are installed
- Check API credentials in `config.json`

## Testing
To run all tests:
```bash
pytest tests

```
Or, if you encounter import errors:
```bash
python -m pytest tests

```
This will automatically discover and run all tests in the `tests/` directory.
