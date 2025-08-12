import yfinance as yf
import ccxt
import pandas as pd
import os
from typing import Dict, List, Optional

kraken = ccxt.kraken({
    'apiKey': os.getenv('KRAKEN_API_KEY'),
    'secret': os.getenv('KRAKEN_SECRET'),
    'enableRateLimit': True
})

def fetch_data(ticker, interval="1d", market_type="stock"):
    """
    Fetch single timeframe data for a ticker.
    
    Args:
        ticker: Stock symbol or crypto pair
        interval: Time interval (1d, 1h, etc.)
        market_type: 'stock' or 'crypto'
    
    Returns:
        pandas.DataFrame: OHLCV data
    """
    if market_type == "stock":
        df = yf.download(ticker, period="7d", interval=interval, progress=False)
        if df.empty:
            return None
        return df
    elif market_type == "crypto":
        # Use Kraken for crypto OHLCV
        try:
            ohlcv = kraken.fetch_ohlcv(ticker, timeframe=interval)
            if not ohlcv:
                return None
            df = pd.DataFrame(ohlcv, columns=["timestamp", "Open", "High", "Low", "Close", "Volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            print(f"Failed to fetch crypto data for {ticker}: {e}")
            return None
    else:
        print(f"Unknown market type: {market_type}")
        return None

def fetch_multi_timeframe_data(ticker: str, timeframes: List[str] = None, market_type: str = "stock") -> Dict[str, pd.DataFrame]:
    """
    Fetch multiple timeframe data for enhanced analysis.
    
    Args:
        ticker: Stock symbol or crypto pair
        timeframes: List of timeframes to fetch (default: ['1d', '1h', '15m'])
        market_type: 'stock' or 'crypto'
    
    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping timeframes to OHLCV data
    """
    if timeframes is None:
        if market_type == "stock":
            timeframes = ['1d', '1h']  # Stocks have limited intraday data on free tier
        else:
            timeframes = ['1d', '4h', '1h']  # Crypto supports more granular data
    
    data = {}
    for tf in timeframes:
        try:
            df = fetch_data(ticker, interval=tf, market_type=market_type)
            if df is not None and not df.empty:
                data[tf] = df
            else:
                print(f"Warning: No data available for {ticker} on {tf} timeframe")
        except Exception as e:
            print(f"Error fetching {ticker} data for timeframe {tf}: {e}")
    
    return data

def align_timeframes(data: Dict[str, pd.DataFrame], method: str = "forward_fill") -> Dict[str, pd.DataFrame]:
    """
    Align multiple timeframe data to ensure consistent timestamps for analysis.
    
    Args:
        data: Dictionary of timeframe data
        method: Alignment method ('forward_fill', 'interpolate')
    
    Returns:
        Dict[str, pd.DataFrame]: Aligned timeframe data
    """
    if not data:
        return data
    
    # Find the timeframe with the most recent data as reference
    reference_tf = max(data.keys(), key=lambda x: len(data[x]))
    reference_times = data[reference_tf].index
    
    aligned_data = {}
    for tf, df in data.items():
        if method == "forward_fill":
            # Reindex and forward fill missing values
            aligned_df = df.reindex(reference_times, method='ffill')
        elif method == "interpolate":
            # Use interpolation for missing values
            aligned_df = df.reindex(reference_times).interpolate()
        else:
            aligned_df = df
        
        aligned_data[tf] = aligned_df.dropna()
    
    return aligned_data
