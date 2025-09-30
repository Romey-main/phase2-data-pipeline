import schedule, time
from app.db import init_db
from app.market_data import fetch_market_data
from app.news_sentiment import fetch_reddit_sentiment
from app.filings import fetch_filings

def job():
    fetch_market_data()
    fetch_reddit_sentiment()
    fetch_filings()
    print("Pipeline run complete.")

if __name__ == "__main__":
    init_db()
    schedule.every(4).hours.do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)
