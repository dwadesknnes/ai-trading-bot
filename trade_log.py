# trade_log.py
# Collects and saves detailed trade logs for analysis

import pandas as pd

class TradeLog:
    def __init__(self):
        self.trades = []

    def log_trade(self, date, ticker, action, size, price, strategy, confidence, pnl, kelly_fraction=None, correlation_info=None):
        """
        Enhanced trade logging with Phase 2 features.
        
        Args:
            date: Trade date
            ticker: Asset ticker
            action: Trade action (BUY/SELL/SHADOW_BUY/etc.)
            size: Position size
            price: Execution price
            strategy: Strategy used
            confidence: Signal confidence
            pnl: Profit/loss
            kelly_fraction: Kelly criterion fraction used (Phase 2)
            correlation_info: Correlation details (Phase 2)
        """
        trade_entry = {
            "date": date,
            "ticker": ticker,
            "action": action,
            "size": size,
            "price": price,
            "strategy": strategy,
            "confidence": confidence,
            "pnl": pnl,
            "kelly_fraction": kelly_fraction,
            "max_correlation": correlation_info.get("max_correlation") if correlation_info else None,
            "correlation_blocked": correlation_info.get("blocked", False) if correlation_info else False
        }
        self.trades.append(trade_entry)

    def get_df(self):
        return pd.DataFrame(self.trades)

    def save_csv(self, filename="trade_log.csv"):
        # Always write headers, even if no trades
        if self.trades:
            df = self.get_df()
            df.to_csv(filename, index=False)
        else:
            pd.DataFrame(columns=[
                "date", "ticker", "action", "size", "price", "strategy", "confidence", "pnl",
                "kelly_fraction", "max_correlation", "correlation_blocked"  # Phase 2 columns
            ]).to_csv(filename, index=False)

    def show(self, n=10):
        df = self.get_df()
        print(df.tail(n))

# --- Demo/Test ---
if __name__ == "__main__":
    log = TradeLog()
    log.log_trade("2025-07-01", "AAPL", "BUY", 10, 195.0, "rsi", 0.8, 12.5)
    log.log_trade("2025-07-02", "AAPL", "SELL", 10, 200.0, "rsi", 0.7, 50.0)
    log.show()
    log.save_csv("trade_log.csv")
