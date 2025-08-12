#!/usr/bin/env python3
"""
Phase 2 (Alpha-v2) Demo Script
Demonstrates the new advanced features in the AI Trading Bot.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategy_engine import StrategyEngine
from risk import RiskManager
from sentiment import SentimentAnalyzer
from trade_log import TradeLog
from config import ADVANCED_FEATURES

def create_sample_data():
    """Create sample market data for demonstration."""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='1D')
    data = pd.DataFrame({
        'Open': np.random.uniform(100, 110, 100),
        'High': np.random.uniform(110, 120, 100),
        'Low': np.random.uniform(90, 100, 100),
        'Close': np.random.uniform(95, 115, 100),
        'Volume': np.random.uniform(1000, 10000, 100)
    }, index=dates)
    return data

def create_sample_trade_history():
    """Create sample trade history for Kelly criterion."""
    return pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=50, freq='1D'),
        'ticker': ['AAPL'] * 25 + ['MSFT'] * 25,
        'action': ['buy'] * 25 + ['sell'] * 25,
        'quantity': [10] * 50,
        'price': np.random.uniform(100, 120, 50),
        'pnl': np.random.normal(1.5, 5, 50)  # Slightly positive expected return
    })

def demo_multi_timeframe_confirmation():
    """Demonstrate multi-timeframe confirmation feature."""
    print("\n" + "="*60)
    print("🔍 PHASE 2 DEMO: Multi-Timeframe Confirmation")
    print("="*60)
    
    # Create sample multi-timeframe data
    sample_data = create_sample_data()
    multi_data = {
        '1d': sample_data,
        '4h': sample_data.iloc[-50:],  # Shorter timeframe
        '1h': sample_data.iloc[-20:]   # Shortest timeframe
    }
    
    # Initialize strategy engine with Phase 2 confirmation
    engine = StrategyEngine(enable_multi_timeframe=True)
    
    print(f"📋 Configuration:")
    print(f"   - Confirmation timeframes: {engine.confirm_timeframes}")
    print(f"   - Agreement threshold: {engine.confirm_threshold:.1%}")
    print(f"   - Confirmation enabled: {engine.enable_confirmation}")
    
    # Test multiple signals
    test_tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    for ticker in test_tickers:
        signal, confidence, strategy = engine.get_multi_timeframe_signal(ticker, multi_data)
        
        confirmed = 'unconfirmed' not in strategy
        status_emoji = '✅' if confirmed else '❌'
        
        print(f"\n📊 {ticker}:")
        print(f"   - Signal: {signal.upper()} ({confidence:.2%} confidence)")
        print(f"   - Strategy: {strategy}")
        print(f"   - Confirmation: {status_emoji} {'CONFIRMED' if confirmed else 'UNCONFIRMED'}")

def demo_correlation_capping():
    """Demonstrate correlation capping feature."""
    print("\n" + "="*60)
    print("🔗 PHASE 2 DEMO: Position Correlation Capping")
    print("="*60)
    
    # Initialize risk manager
    risk_manager = RiskManager(enable_kelly_criterion=True)
    
    print(f"📋 Configuration:")
    print(f"   - Max correlation allowed: {risk_manager.max_position_corr:.1%}")
    print(f"   - Correlation lookback: {risk_manager.correlation_lookback} days")
    print(f"   - Correlation cap enabled: {risk_manager.enable_correlation_cap}")
    
    # Simulate current positions
    current_positions = {
        'AAPL': {'qty': 100, 'avg_price': 150},
        'MSFT': {'qty': 50, 'avg_price': 300}
    }
    
    # Test correlation check with different candidates
    test_candidates = [
        ('GOOGL', 'Tech stock (likely high correlation)'),
        ('JPM', 'Financial stock (likely low correlation)'),
        ('BTC/USDT', 'Cryptocurrency (likely low correlation)')
    ]
    
    trade_history = create_sample_trade_history()
    
    for candidate, description in test_candidates:
        print(f"\n📈 Testing candidate: {candidate}")
        print(f"   Description: {description}")
        
        params = risk_manager.get_risk_params(
            balance=10000,
            price=200,
            confidence=0.8,
            market_type='stock',
            trade_history=trade_history,
            current_positions=current_positions,
            candidate_ticker=candidate
        )
        
        if params['correlation_blocked']:
            print("   ❌ TRADE BLOCKED")
            details = params['correlation_details']
            print(f"   Reason: {details.get('reason', 'Unknown')}")
            if 'max_correlation' in details:
                print(f"   Max correlation: {details['max_correlation']:.3f}")
        else:
            print("   ✅ TRADE ALLOWED")
            details = params['correlation_details']
            if 'max_correlation' in details:
                print(f"   Max correlation: {details['max_correlation']:.3f}")
            print(f"   Position size: {params['size']} shares")

def demo_enhanced_kelly_criterion():
    """Demonstrate enhanced Kelly criterion features."""
    print("\n" + "="*60)
    print("🎯 PHASE 2 DEMO: Enhanced Kelly Criterion")
    print("="*60)
    
    # Create trade history with realistic performance
    trade_history = create_sample_trade_history()
    
    risk_manager = RiskManager(enable_kelly_criterion=True)
    
    print(f"📋 Configuration:")
    print(f"   - Kelly criterion enabled: {risk_manager.enable_kelly_criterion}")
    print(f"   - Kelly cap: {ADVANCED_FEATURES.get('KELLY_CAP', 0.25):.1%}")
    
    # Get detailed Kelly metrics
    kelly_metrics = risk_manager.get_kelly_metrics(trade_history)
    
    print(f"\n📊 Kelly Criterion Analysis:")
    print(f"   - Sample size: {kelly_metrics['sample_size']} trades")
    print(f"   - Win rate: {kelly_metrics['win_rate']:.2%}")
    print(f"   - Average win: ${kelly_metrics['avg_win']:.2f}")
    print(f"   - Average loss: ${kelly_metrics['avg_loss']:.2f}")
    print(f"   - Win/Loss ratio: {kelly_metrics['win_loss_ratio']:.2f}")
    print(f"   - Kelly fraction: {kelly_metrics['kelly_fraction']:.3f} ({kelly_metrics['kelly_fraction']*100:.1f}%)")
    
    # Test position sizing with Kelly
    balance = 10000
    price = 150
    confidence = 0.8
    
    params = risk_manager.get_risk_params(
        balance=balance,
        price=price,
        confidence=confidence,
        market_type='stock',
        trade_history=trade_history
    )
    
    kelly_allocation = balance * kelly_metrics['kelly_fraction']
    traditional_allocation = balance * 0.05  # 5% traditional allocation
    
    print(f"\n💰 Position Sizing Comparison:")
    print(f"   - Portfolio balance: ${balance:,.2f}")
    print(f"   - Asset price: ${price:.2f}")
    print(f"   - Signal confidence: {confidence:.1%}")
    print(f"   - Traditional allocation (5%): ${traditional_allocation:.2f} → {int(traditional_allocation/price)} shares")
    print(f"   - Kelly allocation: ${kelly_allocation:.2f} → {int(kelly_allocation/price)} shares")
    print(f"   - Final allocation: ${params['allocation']:.2f} → {params['size']} shares")
    print(f"   - Kelly factor applied: {'YES' if params['kelly_fraction'] else 'NO'}")

def demo_enhanced_trade_logging():
    """Demonstrate enhanced trade logging with Phase 2 features."""
    print("\n" + "="*60)
    print("📋 PHASE 2 DEMO: Enhanced Trade Logging")
    print("="*60)
    
    # Create enhanced trade logger
    trade_logger = TradeLog()
    
    # Simulate some trades with Phase 2 data
    sample_trades = [
        {
            'date': '2024-01-15 10:30',
            'ticker': 'AAPL',
            'action': 'BUY',
            'size': 100,
            'price': 185.50,
            'strategy': 'multi_tf_rsi',
            'confidence': 0.82,
            'pnl': 0,
            'kelly_fraction': 0.125,
            'correlation_info': {'max_correlation': 0.45, 'blocked': False}
        },
        {
            'date': '2024-01-15 11:15',
            'ticker': 'MSFT',
            'action': 'BLOCKED',
            'size': 0,
            'price': 378.20,
            'strategy': 'multi_tf_sma',
            'confidence': 0.75,
            'pnl': 0,
            'kelly_fraction': 0.15,
            'correlation_info': {'max_correlation': 0.78, 'blocked': True}
        },
        {
            'date': '2024-01-15 14:22',
            'ticker': 'BTC/USDT',
            'action': 'SHADOW_BUY',
            'size': 0.05,
            'price': 42300,
            'strategy': 'multi_tf_macd',
            'confidence': 0.68,
            'pnl': 0,
            'kelly_fraction': 0.08,
            'correlation_info': {'max_correlation': 0.12, 'blocked': False}
        }
    ]
    
    print("📝 Logging enhanced trades...")
    
    for trade in sample_trades:
        trade_logger.log_trade(
            trade['date'],
            trade['ticker'],
            trade['action'],
            trade['size'],
            trade['price'],
            trade['strategy'],
            trade['confidence'],
            trade['pnl'],
            kelly_fraction=trade['kelly_fraction'],
            correlation_info=trade['correlation_info']
        )
        
        status = "✅ EXECUTED" if trade['action'] in ['BUY', 'SELL'] else \
                "❌ BLOCKED" if trade['action'] == 'BLOCKED' else \
                "🔮 SHADOW" if 'SHADOW' in trade['action'] else "❓ UNKNOWN"
        
        print(f"   {trade['date']} | {trade['ticker']} | {trade['action']} | {status}")
        print(f"      Kelly: {trade['kelly_fraction']:.3f} | Corr: {trade['correlation_info']['max_correlation']:.2f}")
    
    # Display the enhanced log
    df = trade_logger.get_df()
    print(f"\n📊 Enhanced Trade Log Summary:")
    print(f"   - Total entries: {len(df)}")
    print(f"   - Columns: {list(df.columns)}")
    print(f"   - Executed trades: {len(df[df['action'].isin(['BUY', 'SELL'])])}")
    print(f"   - Blocked trades: {len(df[df['action'] == 'BLOCKED'])}")
    print(f"   - Shadow trades: {len(df[df['action'].str.contains('SHADOW', na=False)])}")

def demo_shadow_mode():
    """Demonstrate shadow mode functionality."""
    print("\n" + "="*60)
    print("🔮 PHASE 2 DEMO: Shadow Mode Trading")
    print("="*60)
    
    shadow_enabled = ADVANCED_FEATURES.get('ENABLE_SHADOW_MODE', False)
    
    print(f"📋 Shadow Mode Configuration:")
    print(f"   - Shadow mode enabled: {shadow_enabled}")
    print(f"   - Description: {'Signals only, no actual trades' if shadow_enabled else 'Live trading mode'}")
    
    if not shadow_enabled:
        print("\n💡 To enable shadow mode:")
        print("   1. Edit config.py")
        print("   2. Set ENABLE_SHADOW_MODE = True")
        print("   3. Run the bot normally")
        print("   4. All signals will be logged but no trades executed")
    
    print(f"\n🎭 Shadow Mode Benefits:")
    print("   ✅ Risk-free strategy testing")
    print("   ✅ Complete signal logging")
    print("   ✅ Performance tracking")
    print("   ✅ Easy toggle on/off")
    print("   ✅ Ideal for paper trading")
    
    # Simulate shadow mode stats
    print(f"\n📊 Simulated Shadow Mode Statistics:")
    print("   - Shadow signals today: 12")
    print("   - Hypothetical trades: 8")
    print("   - Hypothetical P&L: +$145.30")
    print("   - Shadow win rate: 75.0%")
    print("   - Largest shadow win: +$78.50")

def main():
    """Run the Phase 2 demonstration."""
    print("🤖 AI Trading Bot - Phase 2 (Alpha-v2) Demonstration")
    print("🚀 Welcome to the advanced AI trading features showcase!")
    
    try:
        # Run all demonstrations
        demo_multi_timeframe_confirmation()
        demo_correlation_capping()
        demo_enhanced_kelly_criterion()
        demo_enhanced_trade_logging()
        demo_shadow_mode()
        
        print("\n" + "="*60)
        print("✅ PHASE 2 DEMONSTRATION COMPLETE")
        print("="*60)
        print("🎉 All Phase 2 features demonstrated successfully!")
        print("\n📚 Next steps:")
        print("   1. Review the enhanced README.md for detailed usage")
        print("   2. Run tests: python test_advanced_features.py")
        print("   3. Start the dashboard: cd dashboard && npm run dev")
        print("   4. Configure Phase 2 settings in config.py")
        print("   5. Start trading: python main.py")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")

if __name__ == '__main__':
    main()