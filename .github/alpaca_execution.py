import os
from alpaca_trade_api.rest import REST, TimeFrame

def place_order_alpaca(symbol, side, qty, trade_logger=None):
    api = REST(
        os.getenv("ALPACA_API_KEY"),
        os.getenv("ALPACA_API_SECRET"),
        base_url='https://paper-api.alpaca.markets'  # Use paper trading endpoint
    )
    order = api.submit_order(
        symbol=symbol,
        qty=qty,
        side=side,  # 'buy' or 'sell'
        type='market',
        time_in_force='gtc'
    )
    print(f"Alpaca order placed: {side} {qty} shares of {symbol} (order id: {order.id})")
    if trade_logger:
        trade_logger.log_trade(
            # Fill in with your actual trade logger params
            symbol=symbol,
            action=side.upper(),
            qty=qty,
            # ... (more fields as needed)
        )
    return order
