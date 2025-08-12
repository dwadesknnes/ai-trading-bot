import os
import pandas as pd
import warnings
import concurrent.futures
warnings.filterwarnings("ignore")
from data import fetch_data, fetch_multi_timeframe_data, align_timeframes
from strategy_engine import StrategyEngine
from sentiment import get_combined_sentiment as get_sentiment_score
from risk import RiskManager, evaluate_performance
from memory_module import Memory
from trade_log import TradeLog
from portfolio import Portfolio
from execution import place_order_kraken
from questrade_execution import place_order_questrade
from trade_reasoning_logger import TradeReasoningLogger
from alpha_ranking import calc_asset_alpha
import matplotlib.pyplot as plt

if __name__ == "main.py":
    print("🚀 Starting AI Trading Bot...")
    main.py()

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

# Load advanced features configuration
from config import ADVANCED_FEATURES, RISK_DEFAULTS

ENABLE_MULTI_TIMEFRAME = ADVANCED_FEATURES.get("ENABLE_MULTI_TIMEFRAME", True)
ENABLE_KELLY_CRITERION = ADVANCED_FEATURES.get("ENABLE_KELLY_CRITERION", True)
ENABLE_SHADOW_MODE = ADVANCED_FEATURES.get("ENABLE_SHADOW_MODE", False)  # Phase 2: Shadow mode

print(f"🔧 Advanced features: Multi-TF={ENABLE_MULTI_TIMEFRAME}, Kelly={ENABLE_KELLY_CRITERION}, Shadow={ENABLE_SHADOW_MODE}")

strategy_engine = StrategyEngine(enable_multi_timeframe=ENABLE_MULTI_TIMEFRAME)
risk_manager = RiskManager(
    enable_kelly_criterion=ENABLE_KELLY_CRITERION,
    **RISK_DEFAULTS
)
memory = Memory()
trade_logger = TradeLog()
portfolio = Portfolio(STARTING_CAPITAL)
trade_reasoning_logger = TradeReasoningLogger()

print(f"MODE: {MODE} | Starting capital: ${STARTING_CAPITAL:.2f}")
print(f"Auto-selected stocks: {assets['stocks']}")
print(f"Auto-selected cryptos: {assets['crypto']}")

def fetch_data_parallel(ticker, market_type):
    """Fetch data with multi-timeframe support if enabled."""
    if ENABLE_MULTI_TIMEFRAME:
        return fetch_multi_timeframe_data(ticker, market_type=market_type)
    else:
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
    data = data_results.get((ticker, market_type), None)
    
    # Handle both single timeframe and multi-timeframe data
    if ENABLE_MULTI_TIMEFRAME:
        if data is None or not data:
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
                notes="No multi-timeframe data available"
            )
            continue
        
        # Align timeframes for consistent analysis
        aligned_data = align_timeframes(data)
        
        # Use primary timeframe for regime detection
        primary_df = next(iter(aligned_data.values())) if aligned_data else None
    else:
        # Single timeframe mode (backwards compatible)
        if data is None or not hasattr(data, "empty") or data.empty:
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
        primary_df = data
        aligned_data = {'1d': data}  # Wrap for consistency

    # --- Dynamic strategy selection ---
    chosen_strategy = select_best_strategy(ticker, memory)
    strategy_engine.set_strategy(ticker, chosen_strategy)
    
    # Get signal using appropriate method
    if ENABLE_MULTI_TIMEFRAME and len(aligned_data) > 1:
        signal, confidence, strategy = strategy_engine.get_multi_timeframe_signal(ticker, aligned_data)
        print(f"Multi-timeframe analysis: {list(aligned_data.keys())}")
    else:
        signal, confidence, strategy = strategy_engine.get_signal(ticker, primary_df)
    
    sentiment = get_sentiment_score(ticker)
    adj_confidence = min(1.0, confidence + 0.1 * sentiment)

    # --- Regime detection (simple version) ---
    price = float(primary_df['Close'].iloc[-1])
    regime = "bull" if price > primary_df['Close'].mean() else "bear"
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

    # Load trade history for Kelly criterion if enabled
    trade_history = None
    if ENABLE_KELLY_CRITERION:
        try:
            if os.path.exists("trades.csv") and os.path.getsize("trades.csv") > 0:
                trade_history = pd.read_csv("trades.csv")
        except Exception as e:
            print(f"Warning: Could not load trade history for Kelly criterion: {e}")

    # Phase 2: Get current positions for correlation check
    current_positions = portfolio.get_positions()

    params = risk_manager.get_risk_params(
        portfolio.capital, 
        price, 
        adj_confidence, 
        market_type,
        trade_history=trade_history,
        current_positions=current_positions,
        candidate_ticker=ticker
    )
    
    # Phase 2: Check if trade was blocked by correlation cap
    if params.get("correlation_blocked", False):
        correlation_details = params.get("correlation_details", {})
        print(f"→ BLOCKED by correlation cap: {correlation_details.get('reason', 'Unknown')}")
        trade_reasoning_logger.log_reason(
            date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            ticker=ticker,
            action="BLOCKED",
            strategy=strategy,
            signal=signal,
            sentiment=sentiment,
            market_regime=regime,
            confidence=adj_confidence,
            notes=f"Correlation blocked: {correlation_details.get('reason', 'Unknown')}"
        )
        continue
    
    position_size = params["size"]
    stop_loss = params["stop_loss"]
    take_profit = params["take_profit"]
    
    # Display Kelly information if available
    if params.get("kelly_fraction") is not None:
        print(f"Kelly fraction: {params['kelly_fraction']:.3f}")
    
    # Display correlation information if available
    correlation_details = params.get("correlation_details", {})
    if correlation_details.get("correlations"):
        max_corr = correlation_details.get("max_correlation", 0)
        print(f"Max correlation: {max_corr:.3f} (limit: {risk_manager.max_position_corr})")

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
    
    # Phase 2: Shadow mode check
    if ENABLE_SHADOW_MODE:
        print("🔮 SHADOW MODE: Signal logged but no actual trade executed")
        trade_reasoning_logger.log_reason(
            date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            ticker=ticker,
            action=f"SHADOW_{signal.upper()}",
            strategy=strategy,
            signal=signal,
            sentiment=sentiment,
            market_regime=regime,
            confidence=adj_confidence,
            notes="Shadow mode - signal only, no execution"
        )
        # Still update portfolio for simulation tracking
        portfolio.execute_trade(ticker, signal, price, allocated)
        memory.record_result(ticker, strategy, "win")  # Assume positive for shadow mode
        trade_logger.log_trade(
            pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            ticker,
            f"SHADOW_{signal.upper()}",
            allocated,
            price,
            strategy,
            adj_confidence,
            0,  # No actual PnL in shadow mode
            kelly_fraction=params.get("kelly_fraction"),
            correlation_info=params.get("correlation_details")
        )
        continue

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
    elif MODE == "LIVE" and market_type == "stock" and allocated > 0:
        if not os.getenv("QUESTRADE_REFRESH_TOKEN") or not os.getenv("QUESTRADE_ACCOUNT_ID"):
            print("⚠️ Questrade API credentials not set. Stock trade will not execute.")
            trade_reasoning_logger.log_reason(
                date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                ticker=ticker,
                action="SKIP",
                strategy=strategy,
                signal=signal,
                sentiment=sentiment,
                market_regime=regime,
                confidence=adj_confidence,
                notes="Missing Questrade API credentials"
            )
        else:
            place_order_questrade(ticker, signal, int(allocated), trade_logger)
            trade_reasoning_logger.log_reason(
                date=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                ticker=ticker,
                action=signal.upper(),
                strategy=strategy,
                signal=signal,
                sentiment=sentiment,
                market_regime=regime,
                confidence=adj_confidence,
                notes="Executed on Questrade"
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
    
    # Phase 2: Enhanced trade logging with Kelly and correlation info
    trade_logger.log_trade(
        pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        ticker,
        signal.upper(),
        allocated,
        price,
        strategy,
        adj_confidence,
        0,  # PnL will be calculated later
        kelly_fraction=params.get("kelly_fraction"),
        correlation_info=params.get("correlation_details")
    )

    stats = memory.get_stats(ticker, strategy)
    print(f"Strategy memory: {stats['wins']} wins / {stats['losses']} losses")

final_portfolio_value = portfolio.capital
for ticker, market_type in assets_list:
    data = data_results.get((ticker, market_type), None)
    
    # Handle both single and multi-timeframe data for final valuation
    if ENABLE_MULTI_TIMEFRAME:
        if data and isinstance(data, dict):
            # Multi-timeframe data - use primary timeframe
            primary_df = next(iter(data.values())) if data else None
        else:
            primary_df = data
    else:
        primary_df = data
    
    if primary_df is not None and not primary_df.empty:
        price = float(primary_df["Close"].iloc[-1])
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

print("✅ Finished running AI Trading Bot.")
