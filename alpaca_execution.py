import os
import alpaca_trade_api as tradeapi

ALPACA_API_KEY = os.getenv('ALPACA_API_KEY')
ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
ALPACA_PAPER = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'

BASE_URL = (
    "https://paper-api.alpaca.markets"
    if ALPACA_PAPER
    else "https://api.alpaca.markets"
)

api = tradeapi.REST(
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
    base_url=BASE_URL,
    api_version='v2',
)

def buy_stock(symbol, qty):
    """Place a buy order for a stock."""
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        print(f"Buy order submitted: {order}")
        return order
    except Exception as e:
        print(f"Error submitting buy order: {e}")
        return None

def sell_stock(symbol, qty):
    """Place a sell order for a stock."""
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
        print(f"Sell order submitted: {order}")
        return order
    except Exception as e:
        print(f"Error submitting sell order: {e}")
        return None
