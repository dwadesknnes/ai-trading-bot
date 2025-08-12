# config.py
# Global settings for the AI Trading Bot with advanced features

# Basic Configuration
MODE = "live"  # Options: 'live' or 'backtest'
BASE_CAPITAL = 10000  # Starting capital for risk allocation

# Data Sources
STOCK_DATA_SOURCE = "yfinance"
CRYPTO_DATA_SOURCE = "binance"

# Advanced Features Configuration
ADVANCED_FEATURES = {
    # Multi-timeframe analysis
    "ENABLE_MULTI_TIMEFRAME": True,
    "DEFAULT_TIMEFRAMES": {
        "stock": ["1d", "1h"],        # Limited for free tier
        "crypto": ["1d", "4h", "1h"]  # More granular for crypto
    },
    "TIMEFRAME_WEIGHTS": {
        "1d": 0.5,   # Daily trend (highest weight)
        "4h": 0.3,   # Intermediate trend  
        "1h": 0.2    # Short-term momentum
    },
    
    # Phase 2: Multi-timeframe confirmation
    "CONFIRM_TIMEFRAMES": ["1d", "4h"],  # Timeframes that must confirm signal
    "CONFIRM_THRESHOLD": 0.6,            # Minimum agreement percentage (0.0-1.0)
    "ENABLE_TIMEFRAME_CONFIRMATION": True,
    
    # Kelly criterion position sizing
    "ENABLE_KELLY_CRITERION": True,
    "KELLY_LOOKBACK_PERIODS": 50,
    "KELLY_MAX_FRACTION": 0.25,  # Cap at 25% for safety
    "KELLY_MIN_SAMPLE_SIZE": 10,
    "KELLY_CAP": 0.25,           # Phase 2: Maximum Kelly fraction cap
    
    # Phase 2: Correlation cap for position management
    "ENABLE_CORRELATION_CAP": True,
    "MAX_POSITION_CORR": 0.7,    # Maximum correlation between positions
    "CORRELATION_LOOKBACK": 30,   # Days to look back for correlation calculation
    
    # Enhanced sentiment analysis
    "ENABLE_ENHANCED_SENTIMENT": True,
    "SENTIMENT_CACHE_HOURS": 1,
    "SENTIMENT_SOURCE_WEIGHTS": {
        "news": 0.4,
        "social": 0.3,
        "technical": 0.2,
        "market": 0.1
    },
    
    # Phase 2: Shadow mode (no actual trades)
    "ENABLE_SHADOW_MODE": False,  # Set to True to disable actual trading
    
    # Risk management
    "ENABLE_ADAPTIVE_RISK": True,
    "CONFIDENCE_ADJUSTMENT": 0.1,  # Sentiment confidence boost
}

# Risk Management Defaults
RISK_DEFAULTS = {
    "MAX_ALLOCATION_PCT_STOCK": 0.05,
    "MAX_ALLOCATION_PCT_CRYPTO": 0.03,
    "DEFAULT_STOP_PCT_STOCK": 0.02,
    "DEFAULT_TAKE_PROFIT_PCT_STOCK": 0.04,
    "DEFAULT_STOP_PCT_CRYPTO": 0.03,
    "DEFAULT_TAKE_PROFIT_PCT_CRYPTO": 0.06,
}

# Performance Tracking
PERFORMANCE_CONFIG = {
    "ENABLE_DETAILED_LOGGING": True,
    "LOG_TRADE_REASONING": True,
    "TRACK_STRATEGY_PERFORMANCE": True,
    "ALPHA_RANKING_ENABLED": True,
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    "ENABLE_REALTIME_UPDATES": True,
    "UPDATE_INTERVAL_SECONDS": 30,
    "SHOW_ADVANCED_METRICS": True,
    "ENABLE_NOTIFICATIONS": False,
}
