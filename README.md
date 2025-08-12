# AI Trading Bot 🤖📈

An advanced AI-powered trading bot that can teach itself and learn from trades. Features autonomous learning strategies, multi-timeframe analysis, Kelly criterion position sizing, and enhanced sentiment analysis for both crypto and stock trading.

## 🚀 New Advanced Features

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
- **Dynamic stop-loss** and take-profit levels
- **Performance metrics** tracking

## 📊 Features

### Core Trading Engine
- **Dynamic strategy switching** based on performance
- **Real-time sentiment analysis** using transformers/VADER
- **Risk management** with position sizing and stop-losses
- **Memory system** for strategy performance tracking
- **Alpha ranking** of assets based on historical performance

### Supported Strategies
- RSI (Relative Strength Index)
- SMA Crossover (Simple Moving Average)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Momentum-based strategies

### Markets Supported
- **Stocks** via Yahoo Finance (yfinance)
- **Cryptocurrencies** via Kraken API (ccxt)

### Execution Platforms
- **Kraken** for cryptocurrency trading
- **Questrade** for stock trading
- **Simulation mode** for backtesting

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

### Environment Variables
```bash
# Kraken API (for crypto trading)
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_SECRET=your_kraken_secret

# Questrade API (for stock trading)
QUESTRADE_REFRESH_TOKEN=your_questrade_refresh_token
QUESTRADE_ACCOUNT_ID=your_questrade_account_id
```

### Feature Flags (in main.py)
```python
ENABLE_MULTI_TIMEFRAME = True   # Enable multi-timeframe analysis
ENABLE_KELLY_CRITERION = True   # Enable Kelly criterion position sizing
```

## 🏃‍♂️ Running the Bot

### Live Trading
```bash
python main.py
```

### Backtesting
```bash
python backtester.py
```

### Dashboard
```bash
cd dashboard
npm install
npm run dev
```

### Running Tests
```bash
python test_advanced_features.py
```

## 📈 Advanced Usage Examples

### Multi-Timeframe Analysis
```python
from data import fetch_multi_timeframe_data, align_timeframes
from strategy_engine import StrategyEngine

# Fetch multi-timeframe data
multi_data = fetch_multi_timeframe_data('AAPL', ['1d', '4h', '1h'])
aligned_data = align_timeframes(multi_data)

# Analyze with multi-timeframe strategy
engine = StrategyEngine(enable_multi_timeframe=True)
signal, confidence, strategy = engine.get_multi_timeframe_signal('AAPL', aligned_data)
```

### Kelly Criterion Position Sizing
```python
from risk import RiskManager
import pandas as pd

# Load trade history
trade_history = pd.read_csv('trades.csv')

# Calculate Kelly-optimized position size
risk_manager = RiskManager(enable_kelly_criterion=True)
params = risk_manager.get_risk_params(
    balance=10000,
    price=100,
    confidence=0.8,
    market_type='stock',
    trade_history=trade_history
)

print(f"Kelly fraction: {params['kelly_fraction']:.3f}")
print(f"Recommended size: {params['size']} shares")
```

### Enhanced Sentiment Analysis
```python
from sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer()
sentiment_score = analyzer.get_combined_sentiment('AAPL')
breakdown = analyzer.get_sentiment_breakdown('AAPL')

print(f"Combined sentiment: {sentiment_score:.3f}")
print(f"Source breakdown: {breakdown['sources']}")
```

## 🧪 Testing

The bot includes comprehensive test coverage for all advanced features:

```bash
# Run all tests
python test_advanced_features.py

# Test specific features
python -m unittest test_advanced_features.TestKellyCriterion
python -m unittest test_advanced_features.TestMultiTimeframeStrategy
python -m unittest test_advanced_features.TestSentimentFusion
```

## 📊 Performance Metrics

The bot tracks various performance metrics:

- **Sharpe Ratio** - Risk-adjusted returns
- **Maximum Drawdown** - Largest portfolio decline
- **Win Rate** - Percentage of profitable trades
- **Kelly Fraction** - Optimal position sizing
- **Multi-timeframe Consensus** - Agreement across timeframes
- **Sentiment Confidence** - Quality of sentiment signals

## 🔧 Architecture

### Modular Design
- **data.py** - Multi-timeframe data fetching and alignment
- **strategy_engine.py** - Multi-timeframe strategy analysis
- **risk.py** - Kelly criterion and advanced risk management
- **sentiment.py** - Enhanced sentiment data fusion
- **portfolio.py** - Portfolio management and tracking
- **execution.py** - Trade execution logic

### Backwards Compatibility
All new features are designed to be backwards compatible:
- Multi-timeframe analysis falls back to single timeframe
- Kelly criterion can be disabled for traditional position sizing
- Enhanced sentiment maintains original API

## 📝 Trade Logging

The bot maintains detailed logs:

- **trades.csv** - All executed trades with performance data
- **trade_reasoning.csv** - Detailed reasoning for each trading decision
- **performance.csv** - Historical performance metrics

## 🎛️ Dashboard Features

The React-based dashboard provides:
- Real-time portfolio performance
- Multi-timeframe signal visualization
- Kelly criterion metrics
- Sentiment analysis breakdown
- Historical trade performance

## ⚠️ Risk Disclaimer

This trading bot is for educational and research purposes. Past performance does not guarantee future results. Always:

- Test thoroughly in simulation mode
- Start with small position sizes
- Monitor performance closely
- Use proper risk management
- Never invest more than you can afford to lose

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
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

**Happy Trading! 🚀**
