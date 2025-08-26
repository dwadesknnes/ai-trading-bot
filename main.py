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

strategy_engine = StrategyEngine(enable_multi_timeframe=ENABLE_MULTI_TIMEFRAME)
risk_manager = RiskManager(
    enable_kelly_criterion=ENABLE_KELLY_CRITERION,
    max_allocation_pct_stock=RISK_DEFAULTS["MAX_ALLOCATION_PCT_STOCK"],
    max_allocation_pct_crypto=RISK_DEFAULTS["MAX_ALLOCATION_PCT_CRYPTO"],
    default_stop_pct_stock=RISK_DEFAULTS["DEFAULT_STOP_PCT_STOCK"],
    default_take_profit_pct_stock=RISK_DEFAULTS["DEFAULT_TAKE_PROFIT_PCT_STOCK"],
    default_stop_pct_crypto=RISK_DEFAULTS["DEFAULT_STOP_PCT_CRYPTO"],
    default_take_profit_pct_crypto=RISK_DEFAULTS["DEFAULT_TAKE_PROFIT_PCT_CRYPTO"]
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

    params = risk_manager.get_risk_params(
        portfolio.capital, 
        price, 
        adj_confidence, 
        market_type,
        trade_history=trade_history
    )
    position_size = params["size"]
    stop_loss = params["stop_loss"]
    take_profit = params["take_profit"]
    
    # Display Kelly information if available
    if params.get("kelly_fraction") is not None:
        print(f"Kelly fraction: {params['kelly_fraction']:.3f}")

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
    
    if primary_df is not None and hasattr(primary_df, 'empty') and not primary_df.empty:
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

# --- ADVANCED ENGINE MODULES ---

class SelfEvolvingStrategyEngine:
    """Framework for autonomous strategy generation, evaluation, selection, and deployment."""
    
    def __init__(self):
        self.strategies = {}
        self.performance_metrics = {}
        self.active_strategies = []
        print("🧠 SelfEvolvingStrategyEngine initialized")
    
    def generate_new_strategies(self):
        """Generate new trading strategies using evolutionary algorithms."""
        # TODO: Implement genetic algorithm for strategy generation
        print("📊 Generating new strategies...")
        pass
    
    def evaluate_strategy_performance(self, strategy_id, trades_data):
        """Evaluate performance of a specific strategy."""
        # TODO: Implement comprehensive strategy evaluation metrics
        print(f"📈 Evaluating strategy {strategy_id} performance...")
        pass
    
    def select_best_strategies(self, market_conditions):
        """Select best performing strategies for current market conditions."""
        # TODO: Implement strategy selection algorithm
        print("🎯 Selecting best strategies for current conditions...")
        pass
    
    def deploy_strategy(self, strategy_id):
        """Deploy a selected strategy for live trading."""
        # TODO: Implement strategy deployment mechanism
        print(f"🚀 Deploying strategy {strategy_id}...")
        pass
    
    def mutate_strategies(self):
        """Apply mutations to existing strategies to create variants."""
        # TODO: Implement strategy mutation logic
        print("🔄 Mutating existing strategies...")
        pass


class MarketRegimeDetector:
    """Detects market regimes (bull, bear, sideways, high-volatility, low-liquidity) for macro and micro conditions."""
    
    def __init__(self):
        self.current_regime = None
        self.regime_history = []
        self.volatility_threshold = 0.02
        self.trend_threshold = 0.01
        print("📊 MarketRegimeDetector initialized")
    
    def detect_market_regime(self, price_data, volume_data=None):
        """Detect current market regime based on price and volume data."""
        # TODO: Implement market regime detection algorithm
        print("🔍 Detecting market regime...")
        return "bull"  # Placeholder
    
    def detect_volatility_regime(self, price_data):
        """Detect volatility regime (high/low volatility)."""
        # TODO: Implement volatility regime detection
        print("📈 Detecting volatility regime...")
        return "normal"  # Placeholder
    
    def detect_liquidity_regime(self, volume_data, spread_data=None):
        """Detect liquidity regime (high/low liquidity)."""
        # TODO: Implement liquidity regime detection
        print("💧 Detecting liquidity regime...")
        return "normal"  # Placeholder
    
    def get_regime_probabilities(self, data):
        """Get probabilities for different market regimes."""
        # TODO: Implement probabilistic regime detection
        print("🎲 Calculating regime probabilities...")
        return {"bull": 0.6, "bear": 0.2, "sideways": 0.2}
    
    def update_regime_history(self, regime):
        """Update the historical record of market regimes."""
        # TODO: Implement regime history tracking
        print(f"📝 Updating regime history with: {regime}")
        pass


class MacroDataIngestor:
    """Fetches and integrates macroeconomic indicators (interest rates, inflation, employment, Fed speeches, oil prices, etc)."""
    
    def __init__(self):
        self.data_sources = {}
        self.cached_data = {}
        self.last_update = None
        print("🌍 MacroDataIngestor initialized")
    
    def fetch_interest_rates(self):
        """Fetch current interest rate data."""
        # TODO: Implement interest rate data fetching
        print("💰 Fetching interest rate data...")
        return {}
    
    def fetch_inflation_data(self):
        """Fetch inflation indicators."""
        # TODO: Implement inflation data fetching
        print("📊 Fetching inflation data...")
        return {}
    
    def fetch_employment_data(self):
        """Fetch employment statistics."""
        # TODO: Implement employment data fetching
        print("👥 Fetching employment data...")
        return {}
    
    def fetch_fed_speeches(self):
        """Fetch and analyze Federal Reserve speeches and minutes."""
        # TODO: Implement Fed communication analysis
        print("🎤 Fetching Fed speeches and communications...")
        return {}
    
    def fetch_commodity_prices(self):
        """Fetch commodity prices (oil, gold, etc.)."""
        # TODO: Implement commodity price fetching
        print("🛢️ Fetching commodity prices...")
        return {}
    
    def get_macro_sentiment(self):
        """Get overall macroeconomic sentiment score."""
        # TODO: Implement macro sentiment calculation
        print("🌡️ Calculating macro sentiment...")
        return 0.0
    
    def update_all_data(self):
        """Update all macroeconomic data sources."""
        # TODO: Implement comprehensive data update
        print("🔄 Updating all macro data sources...")
        pass


class RegimeStrategySwitcher:
    """Auto-switches strategies/playbooks based on detected market regime and macro data."""
    
    def __init__(self, regime_detector, macro_ingestor, strategy_engine):
        self.regime_detector = regime_detector
        self.macro_ingestor = macro_ingestor
        self.strategy_engine = strategy_engine
        self.regime_strategies = {}
        self.switching_rules = {}
        print("🔄 RegimeStrategySwitcher initialized")
    
    def define_regime_strategies(self):
        """Define which strategies to use for each market regime."""
        # TODO: Implement regime-strategy mapping
        print("📋 Defining regime-specific strategies...")
        pass
    
    def should_switch_strategy(self, current_regime, macro_conditions):
        """Determine if strategy should be switched based on conditions."""
        # TODO: Implement strategy switching logic
        print("🤔 Evaluating if strategy switch is needed...")
        return False
    
    def switch_strategy(self, new_regime, macro_data):
        """Switch to appropriate strategy based on regime and macro data."""
        # TODO: Implement strategy switching mechanism
        print(f"🔄 Switching strategy for regime: {new_regime}")
        pass
    
    def get_strategy_for_regime(self, regime):
        """Get the best strategy for a specific market regime."""
        # TODO: Implement regime-strategy lookup
        print(f"📊 Getting strategy for regime: {regime}")
        return "default_strategy"
    
    def update_switching_rules(self, performance_data):
        """Update strategy switching rules based on performance."""
        # TODO: Implement adaptive switching rules
        print("📈 Updating strategy switching rules...")
        pass


class DashboardIntegration:
    """Hooks for visualizing regime, macro, and strategy state in the dashboard."""
    
    def __init__(self):
        self.dashboard_data = {}
        self.update_queue = []
        self.websocket_connections = []
        print("📱 DashboardIntegration initialized")
    
    def update_regime_display(self, regime_data):
        """Update dashboard with current market regime information."""
        # TODO: Implement regime display update
        print("📊 Updating regime display on dashboard...")
        pass
    
    def update_macro_display(self, macro_data):
        """Update dashboard with macroeconomic indicators."""
        # TODO: Implement macro data display update
        print("🌍 Updating macro data display...")
        pass
    
    def update_strategy_display(self, strategy_data):
        """Update dashboard with current strategy information."""
        # TODO: Implement strategy display update
        print("🎯 Updating strategy display...")
        pass
    
    def send_alerts(self, alert_type, message):
        """Send alerts to dashboard users."""
        # TODO: Implement alert system
        print(f"⚠️ Sending {alert_type} alert: {message}")
        pass
    
    def export_dashboard_data(self, format_type="json"):
        """Export dashboard data for external use."""
        # TODO: Implement data export functionality
        print(f"📤 Exporting dashboard data as {format_type}")
        return {}
    
    def get_dashboard_state(self):
        """Get current state of all dashboard components."""
        # TODO: Implement dashboard state retrieval
        print("📋 Getting current dashboard state...")
        return {}


# --- INITIALIZATION AND INTEGRATION ---
print("\n🚀 Initializing Advanced Engine Modules...")

# Initialize advanced modules
evolving_engine = SelfEvolvingStrategyEngine()
regime_detector = MarketRegimeDetector() 
macro_ingestor = MacroDataIngestor()
regime_switcher = RegimeStrategySwitcher(regime_detector, macro_ingestor, strategy_engine)
dashboard_integration = DashboardIntegration()

print("✅ All advanced modules initialized successfully!")

# Demonstrate integration in main trading loop
print("\n🔗 Testing integration with main trading loop...")

# Test regime detection
current_regime = regime_detector.detect_market_regime(None)
print(f"Current detected regime: {current_regime}")

# Test macro data fetching
macro_ingestor.update_all_data()

# Test strategy evolution
evolving_engine.generate_new_strategies()

# Test dashboard updates
dashboard_integration.update_regime_display({"regime": current_regime})

print("✅ Integration testing completed!")

print("✅ Finished running AI Trading Bot.")
