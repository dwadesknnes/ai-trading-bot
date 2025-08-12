# AI Trading Bot 🤖📈

An advanced AI-powered trading bot that can teach itself and learn from trades. Features autonomous learning strategies, multi-timeframe analysis, Kelly criterion position sizing, enhanced sentiment analysis, and Phase 2 advanced risk management for both crypto and stock trading.

## 🚀 Phase 2 (Alpha-v2) Advanced Features

### Multi-Timeframe Confirmation System
- **Configurable timeframe agreement** - Requires agreement between 2+ timeframes for trades
- **CONFIRM_TIMEFRAMES** - Set which timeframes must confirm signals (default: ["1d", "4h"])
- **CONFIRM_THRESHOLD** - Minimum agreement percentage (default: 0.6 = 60%)
- **Smart fallback logic** - Gracefully handles insufficient confirmation data
- **Detailed logging** - All confirmation checks logged with reasoning

### Position Correlation Capping
- **Real-time correlation analysis** - Calculates correlation between candidate assets and existing positions
- **MAX_POSITION_CORR** - Maximum allowed correlation (default: 0.7)
- **CORRELATION_LOOKBACK** - Days of price history for correlation (default: 30)
- **Dynamic blocking** - Prevents over-concentration in correlated assets
- **Correlation heatmap** - Visual correlation matrix in dashboard

### Enhanced Kelly Criterion Position Sizing
- **Per-trade Kelly statistics** - Individual Kelly fractions logged for each trade
- **KELLY_CAP** - Safety cap on Kelly fractions (default: 0.25 = 25%)
- **Enhanced logging** - Win rate, avg win/loss, and sample size tracking
- **Dashboard integration** - Real-time Kelly metrics and performance visualization
- **Smart fallbacks** - Conservative defaults for insufficient data

### Advanced Sentiment Data Fusion
- **Multi-source aggregation** - Combines news, social, technical, and market sentiment
- **Configurable source weights** - Customize importance of each sentiment source
- **Quality-based weighting** - Sources weighted by data quality and recency
- **Enhanced caching** - 1-hour sentiment cache for performance
- **Detailed breakdowns** - Source-by-source sentiment analysis in dashboard

### Shadow Mode Trading
- **Risk-free testing** - Generate signals without executing actual trades
- **ENABLE_SHADOW_MODE** - Toggle between live and shadow trading
- **Complete signal logging** - All signals tracked with full reasoning
- **Hypothetical P&L** - Track shadow mode performance
- **Easy toggling** - Dashboard control for shadow mode activation

### Advanced Dashboard Analytics
- **Multi-timeframe confirmation status** - Visual confirmation indicators per asset
- **Kelly criterion metrics** - Real-time Kelly stats and historical performance
- **Correlation heatmap** - Interactive correlation matrix with color coding
- **Enhanced trade log** - Kelly fractions, correlations, and confirmation status
- **Sentiment source breakdown** - Detailed sentiment analysis per source
- **Shadow mode controls** - Toggle and monitor shadow trading
- **Downloadable logs** - Export trade data and analytics

## 📊 Core Features

### Multi-Timeframe Analysis
- **Simultaneous analysis** across multiple timeframes (1d, 4h, 1h)
- **Weighted signal combination** from different timeframes
- **Consensus-based confidence** scoring
- **Automatic timeframe alignment** for consistent analysis

### Kelly Criterion Position Sizing
- **Optimal position sizing** based on historical performance
- **Risk-adjusted allocation** using win rate and win/loss ratios
- **Fractional Kelly** implementation for safety (max 25% allocation)
- **Adaptive sizing** based on strategy performance

### Enhanced Sentiment Data Fusion
- **Multi-source sentiment** aggregation (news, social media, technical)
- **Quality-weighted fusion** algorithm
- **Sentiment confidence** scoring
- **Caching system** for performance optimization

### Advanced Risk Management
- **Kelly-adjusted** position sizing
- **Multi-timeframe** risk assessment
- **Correlation-based** position limits
- **Dynamic stop-loss** and take-profit levels
- **Performance metrics** tracking

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/dwadesknnes/ai-trading-bot.git
cd ai-trading-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp env.example .env
# Edit .env with your API keys
```

## ⚙️ Configuration

### Phase 2 Advanced Configuration
```python
# Multi-timeframe confirmation
CONFIRM_TIMEFRAMES = ["1d", "4h"]  # Timeframes that must confirm
CONFIRM_THRESHOLD = 0.6            # 60% agreement required
ENABLE_TIMEFRAME_CONFIRMATION = True

# Correlation capping
MAX_POSITION_CORR = 0.7           # Max 70% correlation
CORRELATION_LOOKBACK = 30         # 30 days of price history
ENABLE_CORRELATION_CAP = True

# Kelly criterion enhancements
KELLY_CAP = 0.25                  # Maximum 25% Kelly allocation
ENABLE_KELLY_CRITERION = True

# Shadow mode
ENABLE_SHADOW_MODE = False        # Set True for signal-only mode
```

### Environment Variables
```bash
# Kraken API (for crypto trading)
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_SECRET=your_kraken_secret

# Questrade API (for stock trading)
QUESTRADE_REFRESH_TOKEN=your_questrade_refresh_token
QUESTRADE_ACCOUNT_ID=your_questrade_account_id
```

## 🏃‍♂️ Running the Bot

### Live Trading
```bash
python main.py
```

### Shadow Mode (Signals Only)
```bash
# Edit config.py: ENABLE_SHADOW_MODE = True
python main.py
```

### Backtesting
```bash
python backtester.py
```

### Advanced Dashboard
```bash
cd dashboard
npm install
npm run dev
```

### Running Tests
```bash
python test_advanced_features.py
```

## 📈 Phase 2 Usage Examples

### Multi-Timeframe Confirmation
```python
from strategy_engine import StrategyEngine

# Enable confirmation with custom settings
engine = StrategyEngine(enable_multi_timeframe=True)
engine.confirm_timeframes = ["1d", "4h"]
engine.confirm_threshold = 0.75  # 75% agreement required

signal, confidence, strategy = engine.get_multi_timeframe_signal('AAPL', multi_data)
print(f"Signal: {signal}, Confirmed: {'✅' if 'unconfirmed' not in strategy else '❌'}")
```

### Correlation Analysis
```python
from risk import RiskManager

risk_manager = RiskManager(enable_correlation_cap=True)
current_positions = {"AAPL": {"qty": 100}, "MSFT": {"qty": 50}}

params = risk_manager.get_risk_params(
    balance=10000,
    price=300,
    confidence=0.8,
    market_type='stock',
    current_positions=current_positions,
    candidate_ticker='GOOGL'
)

if params['correlation_blocked']:
    print(f"Trade blocked: {params['correlation_details']['reason']}")
else:
    print(f"Trade allowed, max correlation: {params['correlation_details']['max_correlation']}")
```

### Enhanced Kelly Statistics
```python
from risk import RiskManager
import pandas as pd

trade_history = pd.read_csv('trades.csv')
risk_manager = RiskManager(enable_kelly_criterion=True)

kelly_metrics = risk_manager.get_kelly_metrics(trade_history)
print(f"Kelly fraction: {kelly_metrics['kelly_fraction']:.3f}")
print(f"Win rate: {kelly_metrics['win_rate']:.2%}")
print(f"Win/Loss ratio: {kelly_metrics['win_loss_ratio']:.2f}")
```

### Shadow Mode Trading
```python
# In config.py
ADVANCED_FEATURES = {
    "ENABLE_SHADOW_MODE": True,  # Enable shadow mode
    # ... other settings
}

# Run normally - all signals will be logged but no trades executed
python main.py
```

## 🧪 Testing Phase 2 Features

```bash
# Run comprehensive test suite
python test_advanced_features.py

# Test specific Phase 2 features
python -m unittest test_advanced_features.TestPhase2Features.test_multi_timeframe_confirmation
python -m unittest test_advanced_features.TestPhase2Features.test_correlation_cap
python -m unittest test_advanced_features.TestPhase2Features.test_enhanced_trade_logging
```

## 📊 Dashboard Features

### Phase 2 Analytics
- **Correlation Heatmap** - Interactive correlation matrix with color coding
- **Confirmation Status** - Real-time multi-timeframe agreement indicators
- **Enhanced Trade Log** - Kelly fractions, correlations, and block reasons
- **Shadow Mode Controls** - Toggle and monitor shadow trading
- **Kelly Metrics** - Real-time Kelly statistics and performance tracking

### Core Analytics
- Real-time portfolio performance
- Multi-timeframe signal visualization
- Sentiment analysis breakdown
- Historical trade performance
- Risk management metrics

## 🔧 Architecture

### Phase 2 Enhancements
- **Enhanced Strategy Engine** - Multi-timeframe confirmation logic
- **Advanced Risk Manager** - Correlation analysis and Kelly enhancements
- **Improved Trade Logger** - Phase 2 metrics tracking
- **Upgraded Dashboard** - Advanced analytics and controls

### Modular Design
- **data.py** - Multi-timeframe data fetching and alignment
- **strategy_engine.py** - Multi-timeframe strategy analysis with confirmation
- **risk.py** - Kelly criterion and correlation-based risk management
- **sentiment.py** - Enhanced sentiment data fusion
- **portfolio.py** - Portfolio management and tracking
- **execution.py** - Trade execution logic
- **trade_log.py** - Enhanced logging with Phase 2 metrics

### Backwards Compatibility
All Phase 2 features are designed to be backwards compatible:
- Multi-timeframe confirmation can be disabled
- Correlation capping gracefully handles missing data
- Kelly criterion falls back to traditional sizing
- Shadow mode maintains all existing functionality

## 📝 Trade Logging

### Phase 2 Enhanced Logs
- **trades.csv** - All trades with Kelly fractions and correlation data
- **trade_reasoning.csv** - Detailed reasoning including confirmation status
- **performance.csv** - Historical performance with Phase 2 metrics

### Log Format Examples
```csv
date,ticker,action,size,price,strategy,confidence,pnl,kelly_fraction,max_correlation,correlation_blocked
2024-01-15,AAPL,BUY,100,185.50,multi_tf_rsi,0.82,0,0.125,0.45,False
2024-01-14,MSFT,BLOCKED,0,300.00,multi_tf_sma,0.75,0,0.15,0.78,True
```

## ⚠️ Risk Disclaimer

This trading bot is for educational and research purposes. Phase 2 features provide additional risk management but do not guarantee profits. Always:

- Test thoroughly in shadow mode before live trading
- Start with small position sizes
- Monitor correlation limits and Kelly fractions
- Use proper risk management
- Never invest more than you can afford to lose

## 🤝 Contributing

Phase 2 contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests (including Phase 2 test suite)
4. Update documentation
5. Submit a pull request

## 📄 License

This project is open source. See the LICENSE file for details.

## 🔗 Links

- [Kraken API Documentation](https://docs.kraken.com/rest/)
- [Questrade API Documentation](https://www.questrade.com/api)
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [CCXT Documentation](https://ccxt.readthedocs.io/)

---

**Happy Trading with Phase 2 Alpha-v2! 🚀**
