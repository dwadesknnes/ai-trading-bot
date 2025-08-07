# asset_discovery.py
import requests
import yfinance as yf
import ccxt

def get_top_stocks(limit=5):
    # Pull top stocks by volume from Yahoo Finance
    url = "https://finance.yahoo.com/most-active"
    try:
        tables = pd.read_html(url)
        most_active = tables[0]['Symbol'].head(limit).tolist()
        return [(symbol, "stock") for symbol in most_active]
    except Exception as e:
        print("Failed to fetch top stocks:", e)
        return []

def get_top_crypto(limit=5):
    # Use ccxt to pull top crypto tickers by volume
    try:
        exchange = ccxt.binance()
        markets = exchange.load_markets()
        sorted_markets = sorted(
            [(symbol, market['quoteVolume']) for symbol, market in markets.items() if '/USDT' in symbol],
            key=lambda x: x[1], reverse=True
        )
        top_symbols = [symbol for symbol, _ in sorted_markets[:limit]]
        return [(symbol, "crypto") for symbol in top_symbols]
    except Exception as e:
        print("Failed to fetch top crypto:", e)
        return []

def discover_assets():
    stocks = get_top_stocks(limit=5)
    crypto = get_top_crypto(limit=5)
    return stocks + crypto