import requests
from bs4 import BeautifulSoup
import random

def get_top_stocks(limit=5):
    """
    Scrapes Yahoo Finance top gainers and returns top stock tickers.
    """
    url = "https://finance.yahoo.com/gainers"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    tickers = []

    for row in soup.find_all("tr", class_="simpTblRow"):
        cols = row.find_all("td")
        if len(cols) > 1:
            ticker = cols[0].text.strip()
            tickers.append(ticker)
        if len(tickers) >= limit:
            break

    return tickers

def get_top_crypto(limit=5):
    """
    Uses CoinGecko API to get top trending crypto pairs.
    """
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    data = response.json()
    tickers = []

    for item in data["coins"][:limit]:
        symbol = item["item"]["symbol"].upper()
        if symbol != "USD":
            tickers.append(f"{symbol}/USDT")

    return tickers

def get_top_assets(stock_limit=5, crypto_limit=5):
    stocks = get_top_stocks(stock_limit)
    cryptos = get_top_crypto(crypto_limit)
    return stocks + cryptos
