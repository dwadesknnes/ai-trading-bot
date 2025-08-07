"""
Alpaca API Integration Module

This module provides functions to execute buy and sell orders using the Alpaca Trading API.
It supports both paper trading and live trading based on environment configuration.
"""

import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
ALPACA_PAPER = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'

# Determine the appropriate base URL based on trading mode
BASE_URL = (
    "https://paper-api.alpaca.markets"
    if ALPACA_PAPER
    else "https://api.alpaca.markets"
)

# Initialize Alpaca API client
if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    print("⚠️  Warning: Alpaca API credentials not found in environment variables.")
    print("Please ensure ALPACA_API_KEY and ALPACA_SECRET_KEY are set in your .env file.")
    api = None
else:
    try:
        api = tradeapi.REST(
            ALPACA_API_KEY,
            ALPACA_SECRET_KEY,
            base_url=BASE_URL,
            api_version='v2',
        )
        mode = "Paper Trading" if ALPACA_PAPER else "Live Trading"
        print(f"✅ Alpaca API initialized successfully in {mode} mode")
    except Exception as e:
        print(f"❌ Failed to initialize Alpaca API: {e}")
        api = None


def buy_stock(symbol, qty):
    """
    Place a buy order for a stock using the Alpaca API.
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL', 'TSLA')
        qty (float or int): Number of shares to buy
        
    Returns:
        Order object if successful, None if failed
    """
    if api is None:
        print("❌ Alpaca API not initialized. Cannot place buy order.")
        return None
        
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        mode = "Paper" if ALPACA_PAPER else "Live"
        print(f"✅ {mode} Buy order submitted: {qty} shares of {symbol}")
        return order
    except Exception as e:
        print(f"❌ Error submitting buy order for {symbol}: {e}")
        return None


def sell_stock(symbol, qty):
    """
    Place a sell order for a stock using the Alpaca API.
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL', 'TSLA')
        qty (float or int): Number of shares to sell
        
    Returns:
        Order object if successful, None if failed
    """
    if api is None:
        print("❌ Alpaca API not initialized. Cannot place sell order.")
        return None
        
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
        mode = "Paper" if ALPACA_PAPER else "Live"
        print(f"✅ {mode} Sell order submitted: {qty} shares of {symbol}")
        return order
    except Exception as e:
        print(f"❌ Error submitting sell order for {symbol}: {e}")
        return None


def get_account_info():
    """
    Get account information from Alpaca API.
    
    Returns:
        Account object if successful, None if failed
    """
    if api is None:
        print("❌ Alpaca API not initialized. Cannot get account info.")
        return None
        
    try:
        account = api.get_account()
        return account
    except Exception as e:
        print(f"❌ Error getting account info: {e}")
        return None


def get_positions():
    """
    Get current positions from Alpaca API.
    
    Returns:
        List of positions if successful, empty list if failed
    """
    if api is None:
        print("❌ Alpaca API not initialized. Cannot get positions.")
        return []
        
    try:
        positions = api.list_positions()
        return positions
    except Exception as e:
        print(f"❌ Error getting positions: {e}")
        return []
