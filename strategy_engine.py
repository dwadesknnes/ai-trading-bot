# strategy_engine.py
# Strategy selection engine with confidence scoring and multi-timeframe analysis
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
import logging

class StrategyEngine:
    def __init__(self, enable_multi_timeframe=True):
        self.strategy_map = {}  # Optional: dynamic assignment later
        self.enable_multi_timeframe = enable_multi_timeframe
        self.timeframe_weights = {
            '1d': 0.5,    # Daily trend (highest weight)
            '4h': 0.3,    # Intermediate trend
            '1h': 0.2     # Short-term momentum
        }
        
        # Phase 2: Multi-timeframe confirmation settings
        try:
            from config import ADVANCED_FEATURES
            self.enable_confirmation = ADVANCED_FEATURES.get("ENABLE_TIMEFRAME_CONFIRMATION", True)
            self.confirm_timeframes = ADVANCED_FEATURES.get("CONFIRM_TIMEFRAMES", ["1d", "4h"])
            self.confirm_threshold = ADVANCED_FEATURES.get("CONFIRM_THRESHOLD", 0.6)
        except ImportError:
            self.enable_confirmation = True
            self.confirm_timeframes = ["1d", "4h"]
            self.confirm_threshold = 0.6

    def set_strategy(self, ticker, strategy_name):
        self.strategy_map[ticker] = strategy_name

    def get_signal(self, ticker, df):
        """Single timeframe signal generation (backwards compatible)"""
        strategy = self.strategy_map.get(ticker, "rsi")
        if strategy == "rsi":
            return self._rsi_strategy(df)
        elif strategy == "sma":
            return self._sma_crossover(df)
        elif strategy == "macd":
            return self._macd_strategy(df)
        elif strategy == "bb":
            return self._bollinger_bands(df)
        elif strategy == "momentum":
            return self._momentum(df)
        else:
            return "hold", 0.5, strategy

    def get_multi_timeframe_signal(self, ticker: str, multi_data: Dict[str, pd.DataFrame]) -> Tuple[str, float, str]:
        """
        Generate signals using multi-timeframe analysis with Phase 2 confirmation.
        
        Args:
            ticker: Asset ticker
            multi_data: Dictionary mapping timeframes to OHLCV data
        
        Returns:
            Tuple[str, float, str]: (signal, confidence, strategy)
        """
        if not self.enable_multi_timeframe or not multi_data:
            # Fallback to single timeframe if no multi-timeframe data
            primary_tf = next(iter(multi_data.values())) if multi_data else None
            if primary_tf is not None:
                return self.get_signal(ticker, primary_tf)
            return "hold", 0.5, "multi_tf"
        
        strategy = self.strategy_map.get(ticker, "rsi")
        timeframe_signals = {}
        
        # Get signals from each timeframe
        for tf, df in multi_data.items():
            if df is None or df.empty:
                continue
                
            signal, confidence, _ = self.get_signal(ticker, df)
            timeframe_signals[tf] = {
                'signal': signal,
                'confidence': confidence,
                'weight': self.timeframe_weights.get(tf, 0.1)
            }
        
        # Phase 2: Apply timeframe confirmation
        if self.enable_confirmation:
            confirmation_result = self._check_timeframe_confirmation(timeframe_signals)
            if not confirmation_result['confirmed']:
                # Log the confirmation failure
                logging.info(f"Multi-timeframe confirmation failed for {ticker}: {confirmation_result['details']}")
                return "hold", 0.5, f"multi_tf_{strategy}_unconfirmed"
        
        # Combine signals using weighted voting
        combined_signal, combined_confidence = self._combine_timeframe_signals(timeframe_signals)
        
        return combined_signal, combined_confidence, f"multi_tf_{strategy}"
    
    def _check_timeframe_confirmation(self, timeframe_signals: Dict) -> Dict:
        """
        Check if enough timeframes confirm the signal for Phase 2 confirmation.
        
        Args:
            timeframe_signals: Dictionary of timeframe signals
        
        Returns:
            Dict: Confirmation result with details
        """
        available_confirm_tfs = [tf for tf in self.confirm_timeframes if tf in timeframe_signals]
        
        if len(available_confirm_tfs) < 2:
            return {
                'confirmed': True,  # Not enough timeframes for confirmation, allow trade
                'details': f"Insufficient confirmation timeframes: {available_confirm_tfs}"
            }
        
        # Count agreement between confirmation timeframes
        signals = [timeframe_signals[tf]['signal'] for tf in available_confirm_tfs]
        signal_counts = {'buy': 0, 'sell': 0, 'hold': 0}
        
        for signal in signals:
            signal_counts[signal] += 1
        
        total_signals = len(signals)
        max_agreement = max(signal_counts.values())
        agreement_ratio = max_agreement / total_signals
        
        confirmed = agreement_ratio >= self.confirm_threshold
        
        return {
            'confirmed': confirmed,
            'agreement_ratio': agreement_ratio,
            'required_threshold': self.confirm_threshold,
            'signal_counts': signal_counts,
            'available_timeframes': available_confirm_tfs,
            'details': f"Agreement: {agreement_ratio:.2f}, Threshold: {self.confirm_threshold}"
        }

    def _combine_timeframe_signals(self, timeframe_signals: Dict) -> Tuple[str, float]:
        """
        Combine signals from multiple timeframes using weighted consensus.
        
        Args:
            timeframe_signals: Dictionary of timeframe signals with weights
        
        Returns:
            Tuple[str, float]: Combined signal and confidence
        """
        if not timeframe_signals:
            return "hold", 0.5
        
        signal_scores = {'buy': 0, 'sell': 0, 'hold': 0}
        total_weight = 0
        confidence_sum = 0
        
        for tf_data in timeframe_signals.values():
            signal = tf_data['signal']
            confidence = tf_data['confidence']
            weight = tf_data['weight']
            
            signal_scores[signal] += weight * confidence
            confidence_sum += confidence * weight
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            for signal in signal_scores:
                signal_scores[signal] /= total_weight
            confidence_sum /= total_weight
        
        # Determine final signal
        final_signal = max(signal_scores, key=signal_scores.get)
        final_confidence = min(1.0, confidence_sum)
        
        # Add consensus bonus - if multiple timeframes agree, increase confidence
        max_score = signal_scores[final_signal]
        consensus_bonus = 0.1 if max_score > 0.6 else 0  # Bonus if strong agreement
        final_confidence = min(1.0, final_confidence + consensus_bonus)
        
        return final_signal, final_confidence

    def _rsi_strategy(self, df):
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.dropna()
        if rsi.empty:
            return "hold", 0.5, "rsi"
        try:
            last_rsi = float(rsi.iloc[-1].item()) # force to scalar safely
        except:
            return "hold", 0.5, "rsi"
        if last_rsi < 30:
            return "buy", 0.8, "rsi"
        elif last_rsi > 70:
            return "sell", 0.8, "rsi"
        else:
            return "hold", 0.5, "rsi"

    def _sma_crossover(self, df):
        sma_short = df["Close"].rolling(10).mean()
        sma_long = df["Close"].rolling(30).mean()
        if sma_short.iloc[-2] < sma_long.iloc[-2] and sma_short.iloc[-1] > sma_long.iloc[-1]:
            return "buy", 0.75, "sma"
        elif sma_short.iloc[-2] > sma_long.iloc[-2] and sma_short.iloc[-1] < sma_long.iloc[-1]:
            return "sell", 0.75, "sma"
        else:
            return "hold", 0.5, "sma"

    def _macd_strategy(self, df):
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
            return "buy", 0.7, "macd"
        elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
            return "sell", 0.7, "macd"
        else:
            return "hold", 0.5, "macd"

    def _bollinger_bands(self, df):
        ma20 = df["Close"].rolling(20).mean()
        std = df["Close"].rolling(20).std()
        upper = ma20 + 2 * std
        lower = ma20 - 2 * std
        close = df["Close"].iloc[-1]
        if close < lower.iloc[-1]:
            return "buy", 0.6, "bb"
        elif close > upper.iloc[-1]:
            return "sell", 0.6, "bb"
        else:
            return "hold", 0.5, "bb"

    def _momentum(self, df):
        change = df["Close"].pct_change(periods=10)
        if change.iloc[-1] > 0.02:
            return "buy", 0.65, "momentum"
        elif change.iloc[-1] < -0.02:
            return "sell", 0.65, "momentum"
        else:
            return "hold", 0.5, "momentum"

