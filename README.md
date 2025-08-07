# AI Trading Bot with Alpaca Integration

An AI-powered trading bot that uses machine learning to make automated trading decisions. This bot features integration with the Alpaca Trading API for both paper and live trading of stocks.

## Features

- 🤖 AI-powered trading strategies using multiple indicators (RSI, SMA, MACD, Bollinger Bands, Momentum)
- 📊 Dynamic strategy switching based on performance
- 🎯 Risk management with position sizing and stop-loss/take-profit
- 📈 Real-time market data integration
- 💹 Alpaca API integration for paper and live trading
- 📰 Sentiment analysis integration
- 🧠 Memory module for strategy performance tracking
- 📋 Comprehensive trade logging and reasoning

## Prerequisites

- Python 3.8 or higher
- Alpaca Trading Account (free paper trading account available)

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/dwadesknnes/ai-trading-bot.git
cd ai-trading-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Alpaca Account

1. **Create an Alpaca Account:**
   - Go to [Alpaca Markets](https://alpaca.markets/)
   - Sign up for a free account
   - Verify your email and complete account setup

2. **Get Your API Keys:**
   - Log into your Alpaca dashboard
   - Navigate to "Paper Trading" section
   - Click on "View" next to "Your API Keys"
   - Copy your API Key ID and Secret Key

### 4. Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   cp env.example .env
   ```

2. **Edit the .env file with your credentials:**
   ```bash
   # Required: Alpaca API Configuration
   ALPACA_API_KEY=your_actual_api_key_here
   ALPACA_SECRET_KEY=your_actual_secret_key_here
   ALPACA_PAPER=true
   ```

   **Important Notes:**
   - Replace `your_actual_api_key_here` with your real Alpaca API Key ID
   - Replace `your_actual_secret_key_here` with your real Alpaca Secret Key
   - Keep `ALPACA_PAPER=true` for paper trading (recommended for testing)

### 5. Run the Trading Bot

```bash
python main.py
```

## Trading Modes

### Paper Trading (Recommended for Testing)

Paper trading allows you to test the bot with simulated money without risk.

**Configuration:**
```bash
ALPACA_PAPER=true
```

**Benefits:**
- ✅ No financial risk
- ✅ Real market data
- ✅ Test strategies safely
- ✅ Learn how the bot works

### Live Trading (Real Money)

⚠️ **WARNING: Live trading involves real money and real risk. Only use after thorough testing in paper mode.**

**Configuration:**
```bash
ALPACA_PAPER=false
```

**Requirements:**
- Funded Alpaca account
- Thorough testing in paper mode
- Understanding of risks involved

## Switching Between Paper and Live Trading

To switch between modes, simply update your `.env` file:

```bash
# For Paper Trading (Safe)
ALPACA_PAPER=true

# For Live Trading (Real Money - Use with Caution)
ALPACA_PAPER=false
```

**No other changes needed** - restart the bot after changing the setting.

## Understanding the Bot's Strategy

The bot uses multiple technical analysis strategies:

1. **RSI (Relative Strength Index)** - Identifies overbought/oversold conditions
2. **SMA (Simple Moving Average)** - Trend following strategy
3. **MACD** - Momentum and trend change detection
4. **Bollinger Bands** - Volatility-based signals
5. **Momentum** - Price momentum analysis

The bot automatically selects the best-performing strategy for each asset based on historical performance.

## Configuration Options

### Risk Management

The bot includes built-in risk management:
- Position sizing based on portfolio percentage
- Stop-loss and take-profit levels
- Maximum allocation limits

### Asset Selection

By default, the bot trades:
- **Stocks:** AAPL, MSFT, GOOG, AMZN, TSLA
- **Crypto:** BTC/USDT, ETH/USDT (via Kraken - optional)

## Monitoring Your Bot

### Trade Logs

The bot generates several log files:
- `trades.csv` - All executed trades
- `trade_reasoning.csv` - Decision reasoning for each trade
- Performance charts and metrics

### Real-time Output

The bot provides real-time console output showing:
- Current market analysis
- Trading signals and confidence levels
- Executed trades
- Portfolio performance

## Safety Features

### Built-in Safeguards

1. **Environment Validation** - Checks for required API keys
2. **Error Handling** - Graceful handling of API failures
3. **Position Limits** - Prevents over-allocation
4. **Paper Trading Default** - Defaults to safe paper trading mode

### Best Practices

1. **Start with Paper Trading** - Always test thoroughly before live trading
2. **Monitor Regularly** - Check bot performance and logs regularly
3. **Set Reasonable Limits** - Don't risk more than you can afford to lose
4. **Understand the Strategy** - Review the bot's logic and parameters

## Troubleshooting

### Common Issues

**1. "Alpaca API credentials not found"**
```
Solution: Check your .env file exists and contains valid ALPACA_API_KEY and ALPACA_SECRET_KEY
```

**2. "Failed to initialize Alpaca API"**
```
Solution: Verify your API keys are correct and your Alpaca account is active
```

**3. "No data for [symbol]"**
```
Solution: Normal for some symbols during off-market hours or holidays
```

### Getting Help

1. Check the console output for detailed error messages
2. Review the trade reasoning logs for decision explanations
3. Verify your .env file configuration
4. Ensure your Alpaca account is active and funded (for live trading)

## API Rate Limits

Alpaca has rate limits for API calls:
- Paper Trading: Higher limits, suitable for testing
- Live Trading: Standard limits, adequate for normal bot operation

The bot includes rate limiting protection to prevent API limit violations.

## Disclaimer

**Important Risk Warning:**

- This software is for educational and research purposes
- Trading involves substantial risk of loss
- Past performance does not guarantee future results
- Never invest more than you can afford to lose
- The authors are not responsible for any financial losses
- Always test thoroughly in paper mode before live trading

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the console output and log files
3. Ensure your environment is properly configured
4. Test with paper trading first

## License

This project is open source and available under the MIT License.
