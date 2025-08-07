import yfinance as yf
import ccxt
import pandas as pd
import os

kraken = ccxt.kraken({
    'apiKey': os.getenv('KRAKEN_API_KEY'),
    'secret': os.getenv('KRAKEN_SECRET'),
    'enableRateLimit': True
})

def fetch_data(ticker, interval="1d", market_type="stock"):
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
