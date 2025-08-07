# sentiment.py
import requests
from transformers import pipeline
from bs4 import BeautifulSoup
import re
import feedparser
import logging

# Optional: use transformers if available, fallback to VADER
try:
    sentiment_pipeline = pipeline("sentiment-analysis")
    USE_TRANSFORMERS = True
except:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import nltk
    nltk.download("vader_lexicon")
    vader = SentimentIntensityAnalyzer()
    USE_TRANSFORMERS = False

def clean_text(text):
    return re.sub(r'[^\w\s]', '', text).strip().lower()

def get_google_news_sentiment(ticker):
    url = f"https://news.google.com/rss/search?q={ticker}"
    feed = feedparser.parse(url)
    titles = [entry.title for entry in feed.entries[:5]]
    return analyze_sentiment(titles)

def get_youtube_sentiment(ticker):
    query = f"{ticker} stock news"
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        titles = [tag.text for tag in soup.find_all("a", {"title": True})[:5]]
        return analyze_sentiment(titles)
    except Exception as e:
        logging.warning(f"YouTube sentiment error: {e}")
        return 0.0

def analyze_sentiment(texts):
    if not texts:
        return 0.0
    if USE_TRANSFORMERS:
        results = sentiment_pipeline(texts)
        scores = [1 if r["label"] == "POSITIVE" else -1 for r in results]
    else:
        scores = []
        for text in texts:
            vs = vader.polarity_scores(text)
            scores.append(vs["compound"])
    return sum(scores) / len(scores)

def get_combined_sentiment(ticker):
    news_score = get_google_news_sentiment(ticker)
    yt_score = get_youtube_sentiment(ticker)
    return (news_score + yt_score) / 2