# execution.py
# Handles order execution logic for Kraken exchange using CCXT

import ccxt
import os

# Initialize Kraken exchange
kraken = ccxt.kraken({
    'apiKey': os.getenv('KRAKEN_API_KEY'),
    'secret': os.getenv('KRAKEN_SECRET'),
    'enableRateLimit': True
})

def place_order_kraken(symbol, side, amount, price=None, trade_logger=None, order_type="market"):
    """
    Executes a trade on Kraken.
    
    Params:
        symbol (str): e.g. "BTC/USDT"
        side (str): "buy" or "sell"
        amount (float): amount to trade
        price (float): limit price (optional)
        trade_logger: TradeLog instance for logging trades
        order_type (str): "market" or "limit"
    
    Returns:
        dict: order response or None if failed
    """
    # If you want to log a trade, you must have the trade_logger and the required args.
    # You must call this from main.py, so details like strategy/confidence/pnl must be passed from there.

    try:
        if order_type == "market":
            order = kraken.create_market_order(symbol, side, amount)
        elif order_type == "limit" and price:
            order = kraken.create_limit_order(symbol, side, amount, price)
        else:
            print("[Execution] Invalid order type or missing price.")
            return None

        print(f"[Execution] Order placed: {order['id']} | {side.upper()} {amount} {symbol}")
        
        # Trade logger example usage (main.py should call this with all needed info)
        # If you want to log here, you must pass all the arguments, e.g.:
        # trade_logger.log_trade(date, symbol, side.upper(), amount, price, strategy, confidence, pnl)
        # trade_logger.save_csv("trade_log.csv")
        
        return order

    except Exception as e:
        print(f"[Execution Error] {e}")
        return None
