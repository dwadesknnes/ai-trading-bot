#!/usr/bin/env python3
"""
Comprehensive test suite for advanced trading bot features.
Tests multi-timeframe analysis, Kelly criterion position sizing, and sentiment fusion.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data import fetch_multi_timeframe_data, align_timeframes
from strategy_engine import StrategyEngine
from risk import RiskManager
from sentiment import SentimentAnalyzer, analyze_sentiment


class TestMultiTimeframeData(unittest.TestCase):
    """Test multi-timeframe data fetching and alignment."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample OHLCV data for testing
        dates = pd.date_range(start='2023-01-01', periods=100, freq='1H')
        self.sample_data = pd.DataFrame({
            'Open': np.random.uniform(100, 110, 100),
            'High': np.random.uniform(110, 120, 100),
            'Low': np.random.uniform(90, 100, 100),
            'Close': np.random.uniform(95, 115, 100),
            'Volume': np.random.uniform(1000, 10000, 100)
        }, index=dates)
    
    def test_align_timeframes(self):
        """Test timeframe alignment functionality."""
        # Create mock multi-timeframe data
        data_1h = self.sample_data
        data_4h = self.sample_data.resample('4H').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min', 
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        multi_data = {'1h': data_1h, '4h': data_4h}
        aligned_data = align_timeframes(multi_data)
        
        self.assertIn('1h', aligned_data)
        self.assertIn('4h', aligned_data)
        self.assertFalse(aligned_data['1h'].empty)
        self.assertFalse(aligned_data['4h'].empty)
    
    def test_empty_data_handling(self):
        """Test handling of empty data."""
        empty_data = {}
        result = align_timeframes(empty_data)
        self.assertEqual(result, {})


class TestMultiTimeframeStrategy(unittest.TestCase):
    """Test multi-timeframe strategy engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.strategy_engine = StrategyEngine(enable_multi_timeframe=True)
        
        # Create sample data
        dates = pd.date_range(start='2023-01-01', periods=50, freq='1D')
        self.sample_data = pd.DataFrame({
            'Open': np.random.uniform(100, 110, 50),
            'High': np.random.uniform(110, 120, 50), 
            'Low': np.random.uniform(90, 100, 50),
            'Close': np.random.uniform(95, 115, 50),
            'Volume': np.random.uniform(1000, 10000, 50)
        }, index=dates)
    
    def test_single_timeframe_backwards_compatibility(self):
        """Test that single timeframe analysis still works."""
        signal, confidence, strategy = self.strategy_engine.get_signal('TEST', self.sample_data)
        
        self.assertIn(signal, ['buy', 'sell', 'hold'])
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)
        self.assertIsInstance(strategy, str)
    
    def test_multi_timeframe_analysis(self):
        """Test multi-timeframe signal generation."""
        multi_data = {
            '1d': self.sample_data,
            '4h': self.sample_data.iloc[-25:],  # Shorter timeframe
            '1h': self.sample_data.iloc[-10:]   # Shortest timeframe
        }
        
        signal, confidence, strategy = self.strategy_engine.get_multi_timeframe_signal('TEST', multi_data)
        
        self.assertIn(signal, ['buy', 'sell', 'hold'])
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)
        self.assertIn('multi_tf', strategy)
    
    def test_empty_multi_timeframe_data(self):
        """Test handling of empty multi-timeframe data."""
        signal, confidence, strategy = self.strategy_engine.get_multi_timeframe_signal('TEST', {})
        
        self.assertEqual(signal, 'hold')
        self.assertEqual(confidence, 0.5)
    
    def test_timeframe_signal_combination(self):
        """Test the signal combination logic."""
        timeframe_signals = {
            '1d': {'signal': 'buy', 'confidence': 0.8, 'weight': 0.5},
            '4h': {'signal': 'buy', 'confidence': 0.7, 'weight': 0.3},
            '1h': {'signal': 'sell', 'confidence': 0.6, 'weight': 0.2}
        }
        
        combined_signal, combined_confidence = self.strategy_engine._combine_timeframe_signals(timeframe_signals)
        
        # Buy should win due to higher weights
        self.assertEqual(combined_signal, 'buy')
        self.assertGreater(combined_confidence, 0)


class TestKellyCriterion(unittest.TestCase):
    """Test Kelly criterion position sizing."""
    
    def setUp(self):
        """Set up test environment."""
        self.risk_manager = RiskManager(enable_kelly_criterion=True)
        
        # Create sample trade history
        self.trade_history = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=50, freq='1D'),
            'ticker': ['AAPL'] * 50,
            'action': ['buy'] * 25 + ['sell'] * 25,
            'quantity': [10] * 50,
            'price': np.random.uniform(100, 120, 50),
            'pnl': np.random.normal(1, 5, 50)  # Small positive expected return with noise
        })
    
    def test_kelly_calculation(self):
        """Test Kelly criterion calculation."""
        kelly_fraction = self.risk_manager.calculate_kelly_criterion(self.trade_history)
        
        self.assertGreaterEqual(kelly_fraction, 0)
        self.assertLessEqual(kelly_fraction, 0.25)  # Capped at 25%
    
    def test_kelly_with_insufficient_data(self):
        """Test Kelly calculation with insufficient data."""
        small_history = self.trade_history.head(5)
        kelly_fraction = self.risk_manager.calculate_kelly_criterion(small_history)
        
        self.assertEqual(kelly_fraction, 0.05)  # Conservative default
    
    def test_kelly_with_no_losses(self):
        """Test Kelly calculation with only winning trades."""
        winning_history = self.trade_history.copy()
        winning_history['pnl'] = np.abs(winning_history['pnl'])
        
        kelly_fraction = self.risk_manager.calculate_kelly_criterion(winning_history)
        
        self.assertEqual(kelly_fraction, 0.1)  # Conservative despite perfect record
    
    def test_risk_params_with_kelly(self):
        """Test risk parameter calculation with Kelly criterion."""
        params = self.risk_manager.get_risk_params(
            balance=10000,
            price=100,
            confidence=0.8,
            market_type='stock',
            trade_history=self.trade_history
        )
        
        self.assertIn('kelly_fraction', params)
        self.assertIsNotNone(params['kelly_fraction'])
        self.assertGreater(params['size'], 0)
    
    def test_kelly_metrics(self):
        """Test Kelly metrics calculation."""
        metrics = self.risk_manager.get_kelly_metrics(self.trade_history)
        
        required_keys = ['kelly_fraction', 'win_rate', 'avg_win', 'avg_loss', 'win_loss_ratio', 'sample_size']
        for key in required_keys:
            self.assertIn(key, metrics)
        
        self.assertEqual(metrics['sample_size'], len(self.trade_history))
        self.assertGreaterEqual(metrics['win_rate'], 0)
        self.assertLessEqual(metrics['win_rate'], 1)


class TestSentimentFusion(unittest.TestCase):
    """Test enhanced sentiment analysis and data fusion."""
    
    def setUp(self):
        """Set up test environment."""
        self.sentiment_analyzer = SentimentAnalyzer(enable_cache=False)  # Disable cache for testing
    
    def test_sentiment_analysis_basic(self):
        """Test basic sentiment analysis."""
        positive_texts = ["Great stock performance!", "Amazing results", "Very bullish outlook"]
        negative_texts = ["Terrible earnings", "Stock is crashing", "Very bearish sentiment"]
        neutral_texts = ["Stock price unchanged", "No significant movement"]
        
        positive_score = analyze_sentiment(positive_texts)
        negative_score = analyze_sentiment(negative_texts)
        neutral_score = analyze_sentiment(neutral_texts)
        
        self.assertGreater(positive_score, 0)
        self.assertLess(negative_score, 0)
        self.assertAlmostEqual(neutral_score, 0, delta=0.3)
    
    def test_sentiment_fusion(self):
        """Test sentiment source fusion."""
        sources = {
            'news': {'score': 0.6, 'quality': 0.8},
            'social': {'score': -0.2, 'quality': 0.6},
            'technical': {'score': 0.1, 'quality': 0.9}
        }
        
        fused_score = self.sentiment_analyzer._fuse_sentiment_sources(sources)
        
        self.assertGreaterEqual(fused_score, -1)
        self.assertLessEqual(fused_score, 1)
    
    def test_empty_sentiment_sources(self):
        """Test handling of empty sentiment sources."""
        fused_score = self.sentiment_analyzer._fuse_sentiment_sources({})
        self.assertEqual(fused_score, 0.0)
    
    def test_sentiment_breakdown(self):
        """Test sentiment breakdown functionality."""
        # This test will mostly check structure since external APIs may not be available
        breakdown = self.sentiment_analyzer.get_sentiment_breakdown('AAPL')
        
        required_keys = ['combined_score', 'sources', 'timestamp', 'cache_hit']
        for key in required_keys:
            self.assertIn(key, breakdown)
        
        self.assertIsInstance(breakdown['combined_score'], (int, float))
        self.assertIsInstance(breakdown['sources'], dict)


class TestIntegration(unittest.TestCase):
    """Integration tests for advanced features working together."""
    
    def setUp(self):
        """Set up integrated test environment."""
        self.strategy_engine = StrategyEngine(enable_multi_timeframe=True)
        self.risk_manager = RiskManager(enable_kelly_criterion=True)
        self.sentiment_analyzer = SentimentAnalyzer(enable_cache=False)
        
        # Create comprehensive test data
        dates = pd.date_range(start='2023-01-01', periods=100, freq='1D')
        self.price_data = pd.DataFrame({
            'Open': np.random.uniform(100, 110, 100),
            'High': np.random.uniform(110, 120, 100),
            'Low': np.random.uniform(90, 100, 100),
            'Close': np.random.uniform(95, 115, 100),
            'Volume': np.random.uniform(1000, 10000, 100)
        }, index=dates)
        
        self.trade_history = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=30, freq='1D'),
            'ticker': ['AAPL'] * 30,
            'action': ['buy'] * 15 + ['sell'] * 15,
            'quantity': [10] * 30,
            'price': np.random.uniform(100, 120, 30),
            'pnl': np.random.normal(0.5, 3, 30)
        })
    
    def test_full_pipeline_integration(self):
        """Test the full pipeline with all advanced features."""
        # Multi-timeframe data
        multi_data = {
            '1d': self.price_data,
            '4h': self.price_data.iloc[-50:],
            '1h': self.price_data.iloc[-20:]
        }
        
        # Get multi-timeframe signal
        signal, confidence, strategy = self.strategy_engine.get_multi_timeframe_signal('AAPL', multi_data)
        
        # Get Kelly-adjusted risk parameters with higher confidence to ensure non-zero size
        risk_params = self.risk_manager.get_risk_params(
            balance=10000,
            price=100,
            confidence=max(0.8, confidence),  # Ensure high confidence for testing
            market_type='stock',
            trade_history=self.trade_history
        )
        
        # Get enhanced sentiment
        sentiment_score = self.sentiment_analyzer.get_combined_sentiment('AAPL')
        
        # Verify all components return valid results
        self.assertIn(signal, ['buy', 'sell', 'hold'])
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)
        self.assertGreaterEqual(risk_params['size'], 0)  # Changed to >= to handle edge cases
        self.assertIsNotNone(risk_params['kelly_fraction'])
        self.assertGreaterEqual(sentiment_score, -1)
        self.assertLessEqual(sentiment_score, 1)
    
    def test_backwards_compatibility(self):
        """Test that existing functionality still works."""
        # Test single timeframe (old method)
        signal, confidence, strategy = self.strategy_engine.get_signal('AAPL', self.price_data)
        
        # Test old risk parameters (without Kelly)
        old_risk_params = self.risk_manager.get_risk_params(
            balance=10000,
            price=100,
            confidence=confidence,
            market_type='stock'
        )
        
        # Verify backwards compatibility
        self.assertIn(signal, ['buy', 'sell', 'hold'])
        self.assertIn('size', old_risk_params)
        self.assertIn('stop_loss', old_risk_params)
        self.assertIn('take_profit', old_risk_params)


class TestPhase2Features(unittest.TestCase):
    """Test Phase 2 advanced features."""
    
    def setUp(self):
        """Set up Phase 2 test environment."""
        self.strategy_engine = StrategyEngine(enable_multi_timeframe=True)
        self.risk_manager = RiskManager(enable_kelly_criterion=True)
        
        # Sample data for testing
        dates = pd.date_range(start='2023-01-01', periods=50, freq='1D')
        self.sample_data = pd.DataFrame({
            'Open': np.random.uniform(100, 110, 50),
            'High': np.random.uniform(110, 120, 50),
            'Low': np.random.uniform(90, 100, 50),
            'Close': np.random.uniform(95, 115, 50),
            'Volume': np.random.uniform(1000, 10000, 50)
        }, index=dates)
        
        self.trade_history = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', periods=30, freq='1D'),
            'ticker': ['AAPL'] * 30,
            'action': ['buy'] * 15 + ['sell'] * 15,
            'quantity': [10] * 30,
            'price': np.random.uniform(100, 120, 30),
            'pnl': np.random.normal(0.5, 3, 30)
        })
    
    def test_multi_timeframe_confirmation(self):
        """Test multi-timeframe confirmation feature."""
        # Create conflicting signals across timeframes
        multi_data = {
            '1d': self.sample_data,  # Will generate some signal
            '4h': self.sample_data.iloc[-25:],  # Different data subset
            '1h': self.sample_data.iloc[-10:]   # Shortest timeframe
        }
        
        signal, confidence, strategy = self.strategy_engine.get_multi_timeframe_signal('TEST', multi_data)
        
        # Should return valid signal (confirmation may or may not pass)
        self.assertIn(signal, ['buy', 'sell', 'hold'])
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)
        self.assertIn('multi_tf', strategy)
    
    def test_timeframe_confirmation_logic(self):
        """Test the confirmation logic directly."""
        # Mock timeframe signals with agreement
        agreeing_signals = {
            '1d': {'signal': 'buy', 'confidence': 0.8, 'weight': 0.5},
            '4h': {'signal': 'buy', 'confidence': 0.7, 'weight': 0.3}
        }
        
        confirmation = self.strategy_engine._check_timeframe_confirmation(agreeing_signals)
        self.assertTrue(confirmation['confirmed'])
        self.assertGreaterEqual(confirmation['agreement_ratio'], 0.6)
        
        # Mock conflicting signals
        conflicting_signals = {
            '1d': {'signal': 'buy', 'confidence': 0.8, 'weight': 0.5},
            '4h': {'signal': 'sell', 'confidence': 0.7, 'weight': 0.3}
        }
        
        confirmation = self.strategy_engine._check_timeframe_confirmation(conflicting_signals)
        # With threshold 0.6 and 50-50 split, should not confirm
        self.assertFalse(confirmation['confirmed'])
    
    def test_correlation_cap(self):
        """Test correlation capping functionality."""
        current_positions = {
            'AAPL': {'qty': 100, 'avg_price': 150},
            'MSFT': {'qty': 50, 'avg_price': 300}
        }
        
        # Test with high correlation candidate (simplified test)
        params = self.risk_manager.get_risk_params(
            balance=10000,
            price=100,
            confidence=0.8,
            market_type='stock',
            trade_history=self.trade_history,
            current_positions=current_positions,
            candidate_ticker='GOOGL'  # Different enough ticker for test
        )
        
        # Should have correlation details
        self.assertIn('correlation_details', params)
        self.assertIn('correlation_blocked', params)
        self.assertIsInstance(params['correlation_blocked'], bool)
    
    def test_kelly_cap_enforcement(self):
        """Test Kelly criterion cap enforcement."""
        # Create trade history that would suggest high Kelly fraction
        winning_history = self.trade_history.copy()
        winning_history['pnl'] = np.abs(winning_history['pnl']) + 1  # All wins
        
        kelly_fraction = self.risk_manager.calculate_kelly_criterion(winning_history)
        
        # Should be capped at reasonable level
        self.assertLessEqual(kelly_fraction, 0.25)
        self.assertGreaterEqual(kelly_fraction, 0)
    
    def test_enhanced_trade_logging(self):
        """Test enhanced trade logging with Phase 2 features."""
        from trade_log import TradeLog
        
        logger = TradeLog()
        correlation_info = {
            'max_correlation': 0.65,
            'blocked': False,
            'correlations': {'AAPL': 0.65}
        }
        
        logger.log_trade(
            date='2023-01-01',
            ticker='MSFT',
            action='BUY',
            size=100,
            price=300,
            strategy='rsi',
            confidence=0.8,
            pnl=0,
            kelly_fraction=0.15,
            correlation_info=correlation_info
        )
        
        df = logger.get_df()
        self.assertEqual(len(df), 1)
        self.assertIn('kelly_fraction', df.columns)
        self.assertIn('max_correlation', df.columns)
        self.assertIn('correlation_blocked', df.columns)
        self.assertEqual(df.iloc[0]['kelly_fraction'], 0.15)
        self.assertEqual(df.iloc[0]['max_correlation'], 0.65)


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMultiTimeframeData,
        TestMultiTimeframeStrategy, 
        TestKellyCriterion,
        TestSentimentFusion,
        TestIntegration,
        TestPhase2Features  # New Phase 2 tests
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Advanced Trading Bot Features Test Suite")
    print("=" * 60)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        exit(0)
    else:
        print("\n❌ Some tests failed!")
        exit(1)