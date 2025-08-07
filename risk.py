# risk.py
# Modular risk management engine

from config import BASE_CAPITAL
import numpy as np

class RiskManager:
    def __init__(
        self,
        max_allocation_pct_stock=0.05,
        max_allocation_pct_crypto=0.03,
        default_stop_pct_stock=0.02,
        default_take_profit_pct_stock=0.04,
        default_stop_pct_crypto=0.03,
        default_take_profit_pct_crypto=0.06
    ):
        self.max_allocation_pct_stock = max_allocation_pct_stock
        self.max_allocation_pct_crypto = max_allocation_pct_crypto
        self.default_stop_pct_stock = default_stop_pct_stock
        self.default_take_profit_pct_stock = default_take_profit_pct_stock
        self.default_stop_pct_crypto = default_stop_pct_crypto
        self.default_take_profit_pct_crypto = default_take_profit_pct_crypto

    def get_risk_params(self, balance, price, confidence, market_type="stock"):
        confidence = min(max(confidence, 0), 1)

        if market_type == "stock":
            max_alloc = self.max_allocation_pct_stock * balance
            stop_pct = self.default_stop_pct_stock * (1 - 0.5 * confidence)
            take_profit_pct = self.default_take_profit_pct_stock * (1 + 0.5 * confidence)
        elif market_type == "crypto":
            max_alloc = self.max_allocation_pct_crypto * balance
            stop_pct = self.default_stop_pct_crypto * (1 - 0.5 * confidence)
            take_profit_pct = self.default_take_profit_pct_crypto * (1 + 0.5 * confidence)
        else:
            raise ValueError("market_type must be 'stock' or 'crypto'")

        allocation = max_alloc * (0.5 + 0.5 * confidence)
        size = int(allocation // price) if price > 0 else 0
        stop_loss = round(price * (1 - stop_pct), 4)
        take_profit = round(price * (1 + take_profit_pct), 4)

        return {
            "size": size,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "allocation": allocation,
            "stop_pct": stop_pct,
            "take_profit_pct": take_profit_pct
        }

def evaluate_performance(df_trades):
    """
    Evaluate performance metrics based on the trade log dataframe.
    """
    returns = df_trades['pnl'].values
    if len(returns) == 0:
        return {"sharpe": 0, "max_drawdown": 0}
    returns = np.array(returns)
    sharpe = np.sqrt(252) * returns.mean() / (returns.std() + 1e-9)  # daily Sharpe
    cumulative = np.cumsum(returns)
    drawdown = np.maximum.accumulate(cumulative) - cumulative
    max_dd = drawdown.max() if len(drawdown) > 0 else 0
    return {"sharpe": sharpe, "max_drawdown": max_dd}
