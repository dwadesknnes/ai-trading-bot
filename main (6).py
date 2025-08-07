import os
import pandas as pd
import warnings
import concurrent.futures
warnings.filterwarnings("ignore")
from data import fetch_data
from strategy_engine import StrategyEngine
from sentiment import get_combined_sentiment as get_sentiment_score
from risk import RiskManager, evaluate_performance
from memory_module import Memory
from trade_log import TradeLog
from portfolio import Portfolio
from execution import place_order_kraken
from trade_reasoning_logger import TradeReasoningLogger
from alpha_ranking import calc_asset_alpha
import matplotlib.pyplot as plt

# --- ASSET DISCOVERY ---
try:
    from screener import get_top_stocks, get_top_crypto
    stocks = get_top_stocks(limit=5)
    cryptos = get_top_crypto(limit=5)
    if not stocks:
        stocks = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]
    if not cryptos:
        cryptos = ["BTC/USDT", "ETH/USDT"]
    assets_list = [[t, 'stock'] for t in stocks] + [[c, 'crypto'] for c in cryptos]
except Exception:
    assets_list = []
    assets_list += [[t, "stock"] for t in ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]]
    assets_list += [[c, "crypto"] for c in ["BTC/USDT", "ETH/USDT"]]

# --- FILTER OUT UNAVAILABLE CRYPTO MARKETS ---
import ccxt
kraken = ccxt.kraken()
try:
    kraken_markets = kraken.load_markets()
except Exception:
    kraken_markets = {}

filtered_assets = []
for ticker, mtype in assets_list:
    if mtype == "stock":
        filtered_assets.append([ticker, mtype])
    elif mtype == "crypto" and ticker in kraken_markets:
        filtered_assets.append([ticker, mtype])
assets_list = filtered_assets

if not assets_list:
    print("No assets found. Using defaults.")
    assets_list = [
        ["AAPL", "stock"],
        ["MSFT", "stock"],
        ["BTC/USDT", "crypto"],
        ["ETH/USDT", "crypto"]
    ]

assets = {"stocks": [], "crypto": []}
for ticker, mtype in assets_list:
    if mtype == "stock":
        assets["stocks"].append(ticker)
    elif mtype == "crypto":
        assets["crypto"].append(ticker)

MODE = "LIVE"
STARTING_CAPITAL = 10000
strategy_engine = StrategyEngine()
risk_manager = RiskManager()
memory = Memory()
trade_logger = TradeLog()
portfolio = Portfolio(STARTING_CAPITAL)
trade_reasoning_logger = TradeReasoningLogger()

print(f"MODE: {MODE} | Starting capital: ${STARTING_CAPITAL:.2f}")
print(f"Auto-selected stocks: {assets['stocks']}")
print(f"Auto-selected cryptos: {assets['crypto']}")

def fetch_data_parallel(ticker, market_type):
    return fetch_data(ticker, interval="1d", market_type=market_type)

data_results = {}
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {executor.submit(fetch_data_parallel, ticker, mtype): (ticker, mtype) for ticker, mtype in assets_list}
    for future in concurrent.futures.as_completed(futures):
        ticker, mtype = futures[future]
        try:
            df = future.result()
            data_results[(ticker, mtype)] = df
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

# --- DYNAMIC STRATEGY SWITCHING ---
def select_best_strategy(ticker, memory):
    strategies = ["rsi", "sma", "macd", "bb", "momentum"]
    best_ratio = -1
    best_strategy = "rsi"
    for strat in strategies:
        stats = memory.get_stats(ticker, strat)
        wins, losses = stats["wins"], stats["losses"]
        total = wins + losses
        if total == 0:
            continue
        ratio = wins / total
        if ratio > best_ratio:
            best_ratio = ratio
            best_strategy = strat
    return best_strategy

# --- ALPHA RANKING ---
trade_logger.save_csv("trades.csv")
if os.path.exists("trades.csv") and os.path.getsize("trades.csv") > 0:
    df_trades = pd.read_csv("trades.csv")
    best_assets = calc_asset_alpha(df_trades)
    if best_assets:
        assets_list = [a for a in assets_list if a[0] in best_assets[:5]]
        print(f"Alpha-ranked assets: {[a[0] for a in assets_list]}")
    else:
        print("No alpha data yet, trading all discovered assets.")
else:
    print("No trades yet, trading all discovered assets.")

for ticker, market_type in assets_list:
    print(f"\n--- {ticker} ({market_type}) ---")
    df = data_results.get((ticker, market_type), None)
    if df is None or not hasattr(df, "empty") or df.empty:
        print(f"No data for {ticker}")
        trade_reasoning_logger.log_reason(
            date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            ticker=ticker,
            action="SKIP",
            strategy="N/A",
            signal="N/A",
            sentiment="N/A",
            market_regime="N/A",
            confidence=0.0,
            notes="No data or unavailable market"
        )
        continue

    # --- Dynamic strategy selection ---
    chosen_strategy = select_best_strategy(ticker, memory)
    strategy_engine.set_strategy(ticker, chosen_strategy)
    signal, confidence, strategy = strategy_engine.get_signal(ticker, df)
    sentiment = get_sentiment_score(ticker)
    adj_confidence = min(1.0, confidence + 0.1 * sentiment)

    # --- Regime detection (simple version) ---
    price = float(df['Close'].iloc[-1])
    regime = "bull" if price > df['Close'].mean() else "bear"
    print(f"Signal: {signal.upper()} | Strategy: {strategy} | Confidence: {confidence:.2f}")
    print(f"Sentiment: {sentiment:.2f} | Adj. Confidence: {adj_confidence:.2f} | Regime: {regime}", end=" ")

    if signal == "hold":
        print("→ HOLD")
        trade_reasoning_logger.log_reason(
            date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            ticker=ticker,
            action="HOLD",
            strategy=strategy,
            signal=signal,
            sentiment=sentiment,
            market_regime=regime,
            confidence=adj_confidence,
            notes="Signal is hold, no trade executed"
        )
        continue

    params = risk_manager.get_risk_params(portfolio.capital, price, adj_confidence, market_type)
    position_size = params["size"]
    stop_loss = params["stop_loss"]
    take_profit = params["take_profit"]

    allocated = portfolio.allocate(ticker, position_size, price)
    if allocated == 0:
        print("→ Allocation too small to execute trade.")
        trade_reasoning_logger.log_reason(
            date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            ticker=ticker,
            action="SKIP",
            strategy=strategy,
            signal=signal,
            sentiment=sentiment,
            market_regime=regime,
            confidence=adj_confidence,
            notes="Position size too small"
        )
        continue

    print(f"→ {signal.upper()} {allocated:.0f} units @{price:.2f} | Stop: {stop_loss:.2f} | Target: {take_profit:.2f}")

    if MODE == "LIVE" and market_type == "crypto" and allocated > 0:
        if not os.getenv("KRAKEN_API_KEY") or not os.getenv("KRAKEN_SECRET"):
            print("⚠️ Kraken API keys not set. Crypto trade will not execute.")
            trade_reasoning_logger.log_reason(
                date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                ticker=ticker,
                action="SKIP",
                strategy=strategy,
                signal=signal,
                sentiment=sentiment,
                market_regime=regime,
                confidence=adj_confidence,
                notes="Missing Kraken API keys"
            )
        else:
            place_order_kraken(ticker, signal, allocated, price, trade_logger)
            trade_reasoning_logger.log_reason(
                date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                ticker=ticker,
                action=signal.upper(),
                strategy=strategy,
                signal=signal,
                sentiment=sentiment,
                market_regime=regime,
                confidence=adj_confidence,
                notes="Executed on Kraken"
            )
    else:
        trade_reasoning_logger.log_reason(
            date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            ticker=ticker,
            action=signal.upper(),
            strategy=strategy,
            signal=signal,
            sentiment=sentiment,
            market_regime=regime,
            confidence=adj_confidence,
            notes="Simulated execution"
        )

    portfolio.execute_trade(ticker, signal, price, allocated)
    memory.record_result(ticker, strategy, "win")
    trade_logger.log_trade(
        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        ticker,
        signal.upper(),
        allocated,
        price,
        strategy,
        adj_confidence,
        0
    )

    stats = memory.get_stats(ticker, strategy)
    print(f"Strategy memory: {stats['wins']} wins / {stats['losses']} losses")

final_portfolio_value = portfolio.capital
for ticker, market_type in assets_list:
    df = data_results.get((ticker, market_type), None)
    if df is not None and not df.empty:
        price = float(df["Close"].iloc[-1])
        final_portfolio_value += portfolio.get_value({ticker: price})

print(f"\nFINAL capital: ${portfolio.capital:.2f} | FINAL portfolio value: ${final_portfolio_value - portfolio.capital:.2f} | TOTAL: ${final_portfolio_value:.2f}")

portfolio.plot_equity_curve()

trade_logger.save_csv("trades.csv")
trade_reasoning_logger.save_csv("trade_reasoning.csv")
if os.path.exists("trades.csv") and os.path.getsize("trades.csv") > 0:
    df_trades = pd.read_csv("trades.csv")
    if not df_trades.empty:
        print(df_trades)
        metrics = evaluate_performance(df_trades)
    else:
        print("No trades were executed. trades.csv is empty.")
else:
    print("No trades were executed. trades.csv is empty.")