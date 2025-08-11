import os
from questrade_api import Questrade

# Questrade API requires a refresh token and account ID
QUESTRADE_REFRESH_TOKEN = os.getenv('QUESTRADE_REFRESH_TOKEN')
QUESTRADE_ACCOUNT_ID = os.getenv('QUESTRADE_ACCOUNT_ID')

def get_questrade_client():
    """Initialize and return Questrade client."""
    if not QUESTRADE_REFRESH_TOKEN:
        raise ValueError("QUESTRADE_REFRESH_TOKEN environment variable not set")
    
    return Questrade(refresh_token=QUESTRADE_REFRESH_TOKEN)

def buy_stock(symbol, qty):
    """Place a buy order for a stock."""
    try:
        qt = get_questrade_client()
        
        if not QUESTRADE_ACCOUNT_ID:
            raise ValueError("QUESTRADE_ACCOUNT_ID environment variable not set")
        
        # Get symbol ID first
        symbols = qt.symbols_search(prefix=symbol)
        if not symbols['symbols']:
            print(f"Symbol {symbol} not found")
            return None
        
        symbol_id = symbols['symbols'][0]['symbolId']
        
        # Create market buy order
        order_data = {
            'accountNumber': QUESTRADE_ACCOUNT_ID,
            'symbolId': symbol_id,
            'quantity': qty,
            'orderType': 'Market',
            'action': 'Buy',
            'primaryRoute': 'AUTO',
            'secondaryRoute': 'AUTO'
        }
        
        # Note: Questrade API doesn't have direct order submission in the current package
        # This is a placeholder structure - actual implementation would need order submission endpoint
        print(f"Buy order prepared for: {symbol} qty: {qty}")
        print(f"Order data: {order_data}")
        
        # For now, return a mock order response
        return {
            'id': f'mock_order_{symbol}_{qty}',
            'symbol': symbol,
            'qty': qty,
            'side': 'buy',
            'status': 'prepared'
        }
        
    except Exception as e:
        print(f"Error submitting buy order: {e}")
        return None

def sell_stock(symbol, qty):
    """Place a sell order for a stock."""
    try:
        qt = get_questrade_client()
        
        if not QUESTRADE_ACCOUNT_ID:
            raise ValueError("QUESTRADE_ACCOUNT_ID environment variable not set")
        
        # Get symbol ID first
        symbols = qt.symbols_search(prefix=symbol)
        if not symbols['symbols']:
            print(f"Symbol {symbol} not found")
            return None
        
        symbol_id = symbols['symbols'][0]['symbolId']
        
        # Create market sell order
        order_data = {
            'accountNumber': QUESTRADE_ACCOUNT_ID,
            'symbolId': symbol_id,
            'quantity': qty,
            'orderType': 'Market',
            'action': 'Sell',
            'primaryRoute': 'AUTO',
            'secondaryRoute': 'AUTO'
        }
        
        # Note: Questrade API doesn't have direct order submission in the current package
        # This is a placeholder structure - actual implementation would need order submission endpoint
        print(f"Sell order prepared for: {symbol} qty: {qty}")
        print(f"Order data: {order_data}")
        
        # For now, return a mock order response
        return {
            'id': f'mock_order_{symbol}_{qty}',
            'symbol': symbol,
            'qty': qty,
            'side': 'sell',
            'status': 'prepared'
        }
        
    except Exception as e:
        print(f"Error submitting sell order: {e}")
        return None

def place_order_questrade(symbol, side, qty, trade_logger=None):
    """
    Place an order using Questrade API.
    
    Args:
        symbol (str): Stock symbol (e.g., "AAPL")
        side (str): "buy" or "sell"
        qty (int): Quantity of shares
        trade_logger: Optional trade logger instance
        
    Returns:
        dict: Order response or None if failed
    """
    try:
        if side.lower() == 'buy':
            order = buy_stock(symbol, qty)
        elif side.lower() == 'sell':
            order = sell_stock(symbol, qty)
        else:
            print(f"Invalid side: {side}. Must be 'buy' or 'sell'")
            return None
        
        if order and trade_logger:
            trade_logger.log_trade(
                symbol=symbol,
                action=side.upper(),
                qty=qty,
                # Add other required fields as needed by your trade logger
            )
        
        return order
        
    except Exception as e:
        print(f"Error placing Questrade order: {e}")
        return None