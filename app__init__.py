app/__init__.py
REDDIT_CLIENT_ID = "YOUR_REDDIT_CLIENT_ID"
REDDIT_CLIENT_SECRET = "YOUR_REDDIT_CLIENT_SECRET"
REDDIT_USER_AGENT = "ai_trading_bot"
EDGAR_DIR = "./edgar_filings"
TICKERS = ["AAPL", "MSFT", "TSLA"]
import sqlite3
DB_NAME = "trading_data.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                Date TEXT, Open REAL, High REAL, Low REAL, Close REAL,
                Adj_Close REAL, Volume INTEGER, Ticker TEXT)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS news_sentiment (
                post_id TEXT PRIMARY KEY, title TEXT, sentiment_score REAL)
        """)

def save_market_data(df):
    with sqlite3.connect(DB_NAME) as conn:
        df.to_sql("market_data", conn, if_exists="append", index=False)

def save_news_sentiment(post_id, title, score):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT OR IGNORE INTO news_sentiment VALUES (?, ?, ?)",
                     (post_id, title, score))
import yfinance as yf
from .db import save_market_data
from .config import TICKERS

def fetch_market_data():
    for ticker in TICKERS:
        df = yf.download(ticker, period="1mo", interval="1d")
        if df.empty: continue
        df["Ticker"] = ticker
        df.reset_index(inplace=True)
        save_market_data(df)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import praw
from .db import save_news_sentiment
from .config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

def fetch_reddit_sentiment(limit=10):
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_CLIENT_SECRET,
                         user_agent=REDDIT_USER_AGENT)
    analyzer = SentimentIntensityAnalyzer()
    for post in reddit.subreddit("stocks").hot(limit=limit):
        score = analyzer.polarity_scores(post.title)["compound"]
        save_news_sentiment(post.id, post.title, score)
from sec_edgar_downloader import Downloader
from .config import EDGAR_DIR, TICKERS

def fetch_filings(amount=1):
    dl = Downloader(EDGAR_DIR)
    for t in TICKERS:
        dl.get("10-K", t, amount=amount)
