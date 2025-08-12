# sentiment.py
# Enhanced sentiment analysis with multi-source data fusion
import requests
from transformers import pipeline
from bs4 import BeautifulSoup
import re
import feedparser
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Optional: use transformers if available, fallback to VADER
try:
    sentiment_pipeline = pipeline("sentiment-analysis")
    USE_TRANSFORMERS = True
except:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import nltk
    nltk.download("vader_lexicon", quiet=True)
    vader = SentimentIntensityAnalyzer()
    USE_TRANSFORMERS = False

class SentimentAnalyzer:
    """Enhanced sentiment analyzer with multi-source data fusion."""
    
    def __init__(self, enable_cache=True):
        self.enable_cache = enable_cache
        self.cache = {}
        self.cache_expiry = timedelta(hours=1)  # Cache for 1 hour
        
        # Weights for different sentiment sources
        self.source_weights = {
            'news': 0.4,
            'social': 0.3,
            'technical': 0.2,
            'market': 0.1
        }
        
        # Quality scoring weights
        self.quality_factors = {
            'recency': 0.3,      # How recent the data is
            'volume': 0.3,       # Volume of mentions
            'reliability': 0.2,   # Source reliability
            'consensus': 0.2      # Agreement between sources
        }

    def get_combined_sentiment(self, ticker: str) -> float:
        """
        Get combined sentiment score using enhanced data fusion.
        
        Args:
            ticker: Asset ticker symbol
            
        Returns:
            float: Combined sentiment score (-1 to 1)
        """
        # Check cache first
        cache_key = f"{ticker}_sentiment"
        if self.enable_cache and cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < self.cache_expiry:
                return cached_data['score']
        
        # Gather sentiment from multiple sources
        sentiment_sources = {}
        
        # News sentiment
        try:
            news_sentiment = self._get_news_sentiment(ticker)
            if news_sentiment is not None:
                sentiment_sources['news'] = news_sentiment
        except Exception as e:
            logging.warning(f"News sentiment error for {ticker}: {e}")
        
        # Social media sentiment (YouTube as proxy)
        try:
            social_sentiment = self._get_social_sentiment(ticker)
            if social_sentiment is not None:
                sentiment_sources['social'] = social_sentiment
        except Exception as e:
            logging.warning(f"Social sentiment error for {ticker}: {e}")
        
        # Technical sentiment (momentum-based)
        try:
            technical_sentiment = self._get_technical_sentiment(ticker)
            if technical_sentiment is not None:
                sentiment_sources['technical'] = technical_sentiment
        except Exception as e:
            logging.warning(f"Technical sentiment error for {ticker}: {e}")
        
        # Combine using weighted fusion
        combined_score = self._fuse_sentiment_sources(sentiment_sources)
        
        # Cache result
        if self.enable_cache:
            self.cache[cache_key] = {
                'score': combined_score,
                'timestamp': datetime.now(),
                'sources': sentiment_sources
            }
        
        return combined_score

    def _fuse_sentiment_sources(self, sources: Dict[str, Dict]) -> float:
        """
        Fuse sentiment from multiple sources using weighted combination.
        
        Args:
            sources: Dictionary of sentiment sources with scores and metadata
            
        Returns:
            float: Fused sentiment score
        """
        if not sources:
            return 0.0
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for source_name, source_data in sources.items():
            if isinstance(source_data, dict):
                score = source_data.get('score', 0.0)
                quality = source_data.get('quality', 1.0)
            else:
                # Backwards compatibility for simple float scores
                score = source_data
                quality = 1.0
            
            weight = self.source_weights.get(source_name, 0.1) * quality
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        return 0.0

    def _get_news_sentiment(self, ticker: str) -> Optional[Dict]:
        """Get sentiment from news sources with quality scoring."""
        news_data = get_google_news_sentiment(ticker)
        
        if news_data is None:
            return None
        
        # Calculate quality score based on recency and volume
        quality_score = min(1.0, 0.7 + 0.3 * min(1.0, len(news_data.get('titles', [])) / 5))
        
        return {
            'score': news_data.get('score', 0.0),
            'quality': quality_score,
            'count': len(news_data.get('titles', [])),
            'source': 'google_news'
        }

    def _get_social_sentiment(self, ticker: str) -> Optional[Dict]:
        """Get sentiment from social media sources."""
        social_score = get_youtube_sentiment(ticker)
        
        if social_score is None:
            return None
        
        # Social media gets lower quality score due to noise
        quality_score = 0.6
        
        return {
            'score': social_score,
            'quality': quality_score,
            'source': 'youtube'
        }

    def _get_technical_sentiment(self, ticker: str) -> Optional[Dict]:
        """Generate technical sentiment based on price momentum."""
        try:
            # This is a placeholder - in real implementation, 
            # you'd fetch recent price data and calculate momentum
            
            # For now, return neutral with medium quality
            return {
                'score': 0.0,
                'quality': 0.8,
                'source': 'technical_momentum'
            }
        except Exception:
            return None

    def get_sentiment_breakdown(self, ticker: str) -> Dict:
        """Get detailed sentiment breakdown for analysis."""
        cache_key = f"{ticker}_sentiment"
        
        if self.enable_cache and cache_key in self.cache:
            cached_data = self.cache[cache_key]
            return {
                'combined_score': cached_data['score'],
                'sources': cached_data.get('sources', {}),
                'timestamp': cached_data['timestamp'],
                'cache_hit': True
            }
        
        # If not cached, run analysis
        score = self.get_combined_sentiment(ticker)
        
        return {
            'combined_score': score,
            'sources': self.cache.get(cache_key, {}).get('sources', {}),
            'timestamp': datetime.now(),
            'cache_hit': False
        }

# Create global instance for backwards compatibility
sentiment_analyzer = SentimentAnalyzer()

def clean_text(text):
    """Clean and normalize text for sentiment analysis."""
    return re.sub(r'[^\w\s]', '', text).strip().lower()

def get_google_news_sentiment(ticker):
    """
    Get sentiment from Google News with enhanced data extraction.
    
    Returns:
        Dict with score and metadata, or None if error
    """
    try:
        url = f"https://news.google.com/rss/search?q={ticker}"
        feed = feedparser.parse(url)
        titles = [entry.title for entry in feed.entries[:10]]  # Get more articles
        
        if not titles:
            return None
        
        sentiment_score = analyze_sentiment(titles)
        
        return {
            'score': sentiment_score,
            'titles': titles,
            'count': len(titles),
            'source_url': url
        }
    except Exception as e:
        logging.warning(f"Google News sentiment error: {e}")
        return None

def get_youtube_sentiment(ticker):
    """Get sentiment from YouTube video titles."""
    query = f"{ticker} stock news"
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        titles = [tag.text for tag in soup.find_all("a", {"title": True})[:5]]
        return analyze_sentiment(titles)
    except Exception as e:
        logging.warning(f"YouTube sentiment error: {e}")
        return 0.0

def analyze_sentiment(texts: List[str]) -> float:
    """
    Analyze sentiment of text list using available NLP model.
    
    Args:
        texts: List of text strings to analyze
        
    Returns:
        float: Average sentiment score (-1 to 1)
    """
    global USE_TRANSFORMERS
    
    if not texts:
        return 0.0
    
    scores = []
    
    if USE_TRANSFORMERS:
        try:
            results = sentiment_pipeline(texts)
            for result in results:
                # Convert to -1 to 1 scale
                score = 1.0 if result["label"] == "POSITIVE" else -1.0
                # Weight by confidence
                score *= result.get("score", 1.0)
                scores.append(score)
        except Exception as e:
            logging.warning(f"Transformer sentiment error: {e}")
            # Fallback to VADER
            USE_TRANSFORMERS = False
    
    if not USE_TRANSFORMERS:
        try:
            for text in texts:
                vs = vader.polarity_scores(text)
                scores.append(vs["compound"])
        except Exception as e:
            logging.warning(f"VADER sentiment error: {e}")
            return 0.0
    
    return sum(scores) / len(scores) if scores else 0.0

def get_combined_sentiment(ticker: str) -> float:
    """
    Backwards compatible function for getting combined sentiment.
    
    Args:
        ticker: Asset ticker symbol
        
    Returns:
        float: Combined sentiment score (-1 to 1)
    """
    return sentiment_analyzer.get_combined_sentiment(ticker)
