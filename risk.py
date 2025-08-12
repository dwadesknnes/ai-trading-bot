# risk.py
# Modular risk management engine with Kelly criterion position sizing and correlation capping

from config import BASE_CAPITAL
import numpy as np
import pandas as pd
import yfinance as yf
import logging
from typing import Optional, Dict, Any

class RiskManager:
    def __init__(
        self,
        max_allocation_pct_stock=0.05,
        max_allocation_pct_crypto=0.03,
        default_stop_pct_stock=0.02,
        default_take_profit_pct_stock=0.04,
        default_stop_pct_crypto=0.03,
        default_take_profit_pct_crypto=0.06,
        enable_kelly_criterion=True
    ):
        self.max_allocation_pct_stock = max_allocation_pct_stock
        self.max_allocation_pct_crypto = max_allocation_pct_crypto
        self.default_stop_pct_stock = default_stop_pct_stock
        self.default_take_profit_pct_stock = default_take_profit_pct_stock
        self.default_stop_pct_crypto = default_stop_pct_crypto
        self.default_take_profit_pct_crypto = default_take_profit_pct_crypto
        self.enable_kelly_criterion = enable_kelly_criterion
        
        # Phase 2: Correlation capping settings
        try:
            from config import ADVANCED_FEATURES
            self.enable_correlation_cap = ADVANCED_FEATURES.get("ENABLE_CORRELATION_CAP", True)
            self.max_position_corr = ADVANCED_FEATURES.get("MAX_POSITION_CORR", 0.7)
            self.correlation_lookback = ADVANCED_FEATURES.get("CORRELATION_LOOKBACK", 30)
        except ImportError:
            self.enable_correlation_cap = True
            self.max_position_corr = 0.7
            self.correlation_lookback = 30

    def get_risk_params(self, balance, price, confidence, market_type="stock", trade_history=None, current_positions=None, candidate_ticker=None):
        """
        Get risk parameters including position sizing using Kelly criterion if enabled.
        
        Args:
            balance: Available balance
            price: Current asset price
            confidence: Signal confidence (0-1)
            market_type: 'stock' or 'crypto'
            trade_history: DataFrame of historical trades for Kelly calculation
            current_positions: Dictionary of current positions for correlation check
            candidate_ticker: Ticker being considered for new position
        
        Returns:
            Dict with risk parameters including position size
        """
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

        # Phase 2: Check correlation cap before allowing trade
        correlation_check = self._check_correlation_cap(candidate_ticker, current_positions, market_type)
        if not correlation_check['allowed']:
            logging.info(f"Trade blocked due to correlation cap: {correlation_check['reason']}")
            return {
                "size": 0,
                "stop_loss": 0,
                "take_profit": 0,
                "allocation": 0,
                "stop_pct": stop_pct,
                "take_profit_pct": take_profit_pct,
                "kelly_fraction": None,
                "correlation_blocked": True,
                "correlation_details": correlation_check
            }

        # Calculate base allocation
        base_allocation = max_alloc * (0.5 + 0.5 * confidence)
        
        # Apply Kelly criterion if enabled and trade history is available
        kelly_fraction = None
        if self.enable_kelly_criterion and trade_history is not None:
            kelly_fraction = self.calculate_kelly_criterion(trade_history)
            kelly_allocation = balance * kelly_fraction
            
            # Use the more conservative of Kelly and traditional allocation
            allocation = min(base_allocation, kelly_allocation, max_alloc)
        else:
            allocation = base_allocation

        size = int(allocation // price) if price > 0 else 0
        stop_loss = round(price * (1 - stop_pct), 4)
        take_profit = round(price * (1 + take_profit_pct), 4)

        return {
            "size": size,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "allocation": allocation,
            "stop_pct": stop_pct,
            "take_profit_pct": take_profit_pct,
            "kelly_fraction": kelly_fraction,
            "correlation_blocked": False,
            "correlation_details": correlation_check
        }

    def calculate_kelly_criterion(self, trade_history: pd.DataFrame, lookback_periods: int = 50) -> float:
        """
        Calculate Kelly criterion fraction for optimal position sizing.
        
        Kelly Fraction = (bp - q) / b
        where:
        - b = odds received on the wager (profit/loss ratio)
        - p = probability of winning
        - q = probability of losing (1-p)
        
        Args:
            trade_history: DataFrame with columns ['pnl', 'action'] or similar
            lookback_periods: Number of recent trades to consider
        
        Returns:
            float: Kelly fraction (0-1, capped for safety)
        """
        if trade_history is None or trade_history.empty:
            return 0.1  # Conservative default

        # Get recent trades
        recent_trades = trade_history.tail(lookback_periods)
        
        if len(recent_trades) < 10:  # Need minimum sample size
            return 0.05  # Very conservative for small sample
        
        # Calculate win rate and average win/loss
        winning_trades = recent_trades[recent_trades['pnl'] > 0]
        losing_trades = recent_trades[recent_trades['pnl'] < 0]
        
        if len(losing_trades) == 0:  # No losses yet
            return 0.1  # Conservative despite perfect record
        
        win_rate = len(winning_trades) / len(recent_trades)
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 1
        
        # Calculate Kelly fraction
        if avg_loss > 0:
            win_loss_ratio = avg_win / avg_loss
            kelly_fraction = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        else:
            kelly_fraction = 0.1
        
        # Apply safety constraints
        kelly_fraction = max(0, kelly_fraction)  # No negative bets
        kelly_fraction = min(0.25, kelly_fraction)  # Cap at 25% for safety (fractional Kelly)
        
        return kelly_fraction

    def get_kelly_metrics(self, trade_history: pd.DataFrame) -> Dict[str, Any]:
        """
        Get Kelly criterion metrics for analysis and reporting.
        
        Args:
            trade_history: DataFrame of historical trades
        
        Returns:
            Dict with Kelly metrics
        """
        if trade_history is None or trade_history.empty:
            return {
                "kelly_fraction": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "win_loss_ratio": 0,
                "sample_size": 0
            }
        
        winning_trades = trade_history[trade_history['pnl'] > 0]
        losing_trades = trade_history[trade_history['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(trade_history) if len(trade_history) > 0 else 0
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        kelly_fraction = self.calculate_kelly_criterion(trade_history)
        
        return {
            "kelly_fraction": kelly_fraction,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "win_loss_ratio": win_loss_ratio,
            "sample_size": len(trade_history)
        }
    
    def _check_correlation_cap(self, candidate_ticker: str, current_positions: Optional[Dict], market_type: str) -> Dict:
        """
        Check if adding the candidate ticker would violate correlation limits.
        
        Args:
            candidate_ticker: Ticker being considered for new position
            current_positions: Dictionary of current positions {ticker: position_info}
            market_type: 'stock' or 'crypto'
        
        Returns:
            Dict: Correlation check result
        """
        if not self.enable_correlation_cap or not current_positions or not candidate_ticker:
            return {"allowed": True, "reason": "No correlation check needed"}
        
        try:
            # Get tickers of current positions
            position_tickers = list(current_positions.keys())
            
            if not position_tickers:
                return {"allowed": True, "reason": "No existing positions"}
            
            # Calculate correlations
            correlations = self._calculate_position_correlations(candidate_ticker, position_tickers, market_type)
            
            # Check if any correlation exceeds threshold
            max_correlation = max(correlations.values()) if correlations else 0
            
            if max_correlation > self.max_position_corr:
                return {
                    "allowed": False,
                    "reason": f"Max correlation {max_correlation:.3f} exceeds limit {self.max_position_corr}",
                    "correlations": correlations,
                    "max_correlation": max_correlation
                }
            
            return {
                "allowed": True,
                "reason": f"Correlations within limits (max: {max_correlation:.3f})",
                "correlations": correlations,
                "max_correlation": max_correlation
            }
            
        except Exception as e:
            logging.warning(f"Correlation check failed for {candidate_ticker}: {e}")
            return {"allowed": True, "reason": f"Correlation check error: {e}"}
    
    def _calculate_position_correlations(self, candidate_ticker: str, position_tickers: list, market_type: str) -> Dict[str, float]:
        """
        Calculate correlations between candidate ticker and existing positions.
        
        Args:
            candidate_ticker: New ticker to check
            position_tickers: List of existing position tickers
            market_type: Market type for data fetching
        
        Returns:
            Dict mapping position ticker to correlation coefficient
        """
        correlations = {}
        
        try:
            # Fetch price data for candidate ticker
            if market_type == "stock":
                candidate_data = yf.download(candidate_ticker, period=f"{self.correlation_lookback}d", progress=False)
                if candidate_data.empty:
                    return correlations
                candidate_prices = candidate_data['Close']
            else:
                # For crypto, use simplified correlation (could be enhanced with ccxt)
                logging.info(f"Crypto correlation calculation simplified for {candidate_ticker}")
                return correlations
            
            for position_ticker in position_tickers:
                try:
                    if market_type == "stock":
                        position_data = yf.download(position_ticker, period=f"{self.correlation_lookback}d", progress=False)
                        if position_data.empty:
                            continue
                        position_prices = position_data['Close']
                        
                        # Align data and calculate correlation
                        aligned_data = pd.concat([candidate_prices, position_prices], axis=1, keys=[candidate_ticker, position_ticker])
                        aligned_data = aligned_data.dropna()
                        
                        if len(aligned_data) > 5:  # Need minimum data points
                            correlation = aligned_data[candidate_ticker].corr(aligned_data[position_ticker])
                            if not pd.isna(correlation):
                                correlations[position_ticker] = abs(correlation)  # Use absolute correlation
                                
                except Exception as e:
                    logging.warning(f"Failed to calculate correlation with {position_ticker}: {e}")
                    continue
                    
        except Exception as e:
            logging.warning(f"Failed to fetch candidate data for {candidate_ticker}: {e}")
        
        return correlations

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
