import pandas as pd

class TradeReasoningLogger:
    def __init__(self):
        self.logs = []
    def log_reason(self, date, ticker, action, strategy, signal, sentiment, market_regime, confidence, notes=""):
        self.logs.append({
            "date": date,
            "ticker": ticker,
            "action": action,
            "strategy": strategy,
            "signal": signal,
            "sentiment": sentiment,
            "market_regime": market_regime,
            "confidence": confidence,
            "notes": notes
        })
    def save_csv(self, filename="trade_reasoning.csv"):
        pd.DataFrame(self.logs).to_csv(filename, index=False)
    def show(self, n=10):
        pd.DataFrame(self.logs).tail(n)