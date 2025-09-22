import praw
from datetime import datetime
import threading
import queue
from modules.config import load_config, TRACK_KEYWORDS, TRACK_SUBREDDITS

cfg = load_config()

reddit = praw.Reddit(
    client_id=cfg["client_id"],
    client_secret=cfg["client_secret"],
    user_agent=cfg["user_agent"],
    username=cfg.get("username") or None,
    password=cfg.get("password") or None,
)

q = queue.Queue()

def reddit_listener(keywords=TRACK_KEYWORDS, subreddits=TRACK_SUBREDDITS):
    subreddit_str = "+".join(subreddits)
    sub = reddit.subreddit(subreddit_str)
    try:
        for submission in sub.stream.submissions(skip_existing=True):
            text = (submission.title or "") + "\n\n" + (submission.selftext or "")
            if any(k.lower() in text.lower() for k in keywords):
                item = {
                    "id": submission.id,
                    "type": "submission",
                    "subreddit": submission.subreddit.display_name,
                    "author": str(submission.author),
                    "text": text,
                    "created_utc": datetime.utcfromtimestamp(submission.created_utc),
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "permalink": "https://reddit.com" + submission.permalink,
                }
                q.put(item)
    except Exception as e:
        print("Submission stream error:", e)

def reddit_comment_listener(keywords=TRACK_KEYWORDS, subreddits=TRACK_SUBREDDITS):
    subreddit_str = "+".join(subreddits)
    sub = reddit.subreddit(subreddit_str)
    try:
        for comment in sub.stream.comments(skip_existing=True):
            text = comment.body or ""
            if any(k.lower() in text.lower() for k in keywords):
                item = {
                    "id": comment.id,
                    "type": "comment",
                    "subreddit": comment.subreddit.display_name,
                    "author": str(comment.author),
                    "text": text,
                    "created_utc": datetime.utcfromtimestamp(comment.created_utc),
                    "score": comment.score,
                    "permalink": "https://reddit.com" + comment.permalink,
                }
                q.put(item)
    except Exception as e:
        print("Comment stream error:", e)

def start_background(listen=True):
    threads = []
    if listen:
        t1 = threading.Thread(target=reddit_listener, daemon=True)
        t2 = threading.Thread(target=reddit_comment_listener, daemon=True)
        threads += [t1, t2]
        t1.start(); t2.start()
    return threads, q
