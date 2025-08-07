# strategy_engine.py
# Strategy selection engine with confidence scoring
import pandas as pd

class StrategyEngine:
    def __init__(self):
        self.strategy_map = {}  # Optional: dynamic assignment later

    def set_strategy(self, ticker, strategy_name):
        self.strategy_map[ticker] = strategy_name

    def get_signal(self, ticker, df):
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

