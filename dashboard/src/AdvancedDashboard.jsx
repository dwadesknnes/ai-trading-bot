import React, { useState, useEffect } from 'react';
import './AdvancedDashboard.css';

const AdvancedDashboard = () => {
  const [portfolioData, setPortfolioData] = useState(null);
  const [kellyMetrics, setKellyMetrics] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [multiTimeframeSignals, setMultiTimeframeSignals] = useState(null);
  const [tradeHistory, setTradeHistory] = useState([]);
  // Phase 2: New state for advanced analytics
  const [correlationMatrix, setCorrelationMatrix] = useState(null);
  const [confirmationStatus, setConfirmationStatus] = useState(null);
  const [shadowModeEnabled, setShadowModeEnabled] = useState(false);

  // Simulated data loading (in real implementation, fetch from backend)
  useEffect(() => {
    // Simulate portfolio data
    setPortfolioData({
      totalValue: 12450.50,
      dailyChange: 245.30,
      dailyChangePercent: 2.01,
      cash: 8234.50,
      positions: [
        { symbol: 'AAPL', value: 2156.00, change: 1.5 },
        { symbol: 'BTC/USDT', value: 2060.00, change: 3.2 }
      ]
    });

    // Simulate Kelly metrics
    setKellyMetrics({
      kellyFraction: 0.125,
      winRate: 0.64,
      avgWin: 2.3,
      avgLoss: 1.8,
      winLossRatio: 1.28,
      sampleSize: 45
    });

    // Simulate sentiment data
    setSentimentData({
      AAPL: {
        combined: 0.35,
        sources: {
          news: { score: 0.4, quality: 0.8 },
          social: { score: 0.2, quality: 0.6 },
          technical: { score: 0.5, quality: 0.9 }
        }
      },
      'BTC/USDT': {
        combined: -0.15,
        sources: {
          news: { score: -0.2, quality: 0.7 },
          social: { score: -0.3, quality: 0.5 },
          technical: { score: 0.1, quality: 0.8 }
        }
      }
    });

    // Simulate multi-timeframe signals
    setMultiTimeframeSignals({
      AAPL: {
        '1d': { signal: 'buy', confidence: 0.7 },
        '4h': { signal: 'buy', confidence: 0.6 },
        '1h': { signal: 'hold', confidence: 0.5 },
        combined: { signal: 'buy', confidence: 0.75 }
      },
      'BTC/USDT': {
        '1d': { signal: 'sell', confidence: 0.8 },
        '4h': { signal: 'sell', confidence: 0.7 },
        '1h': { signal: 'sell', confidence: 0.6 },
        combined: { signal: 'sell', confidence: 0.82 }
      }
    });

    // Simulate recent trades with Phase 2 data
    setTradeHistory([
      { 
        date: '2024-01-15', 
        symbol: 'AAPL', 
        action: 'BUY', 
        quantity: 10, 
        price: 185.50, 
        pnl: 0,
        kellyFraction: 0.12,
        maxCorrelation: 0.45,
        confirmationStatus: 'CONFIRMED'
      },
      { 
        date: '2024-01-14', 
        symbol: 'BTC/USDT', 
        action: 'SELL', 
        quantity: 0.05, 
        price: 42300, 
        pnl: 156.50,
        kellyFraction: 0.08,
        maxCorrelation: 0.23,
        confirmationStatus: 'CONFIRMED'
      },
      { 
        date: '2024-01-13', 
        symbol: 'MSFT', 
        action: 'BLOCKED', 
        quantity: 0, 
        price: 378.20, 
        pnl: 0,
        kellyFraction: 0.15,
        maxCorrelation: 0.78,
        confirmationStatus: 'CORRELATION_BLOCKED'
      }
    ]);

    // Phase 2: Simulate correlation matrix
    setCorrelationMatrix({
      assets: ['AAPL', 'MSFT', 'GOOGL', 'BTC/USDT'],
      matrix: [
        [1.00, 0.45, 0.52, 0.12],
        [0.45, 1.00, 0.78, 0.08],
        [0.52, 0.78, 1.00, 0.15],
        [0.12, 0.08, 0.15, 1.00]
      ]
    });

    // Phase 2: Simulate confirmation status
    setConfirmationStatus({
      AAPL: {
        confirmed: true,
        agreementRatio: 0.75,
        threshold: 0.6,
        timeframes: ['1d', '4h'],
        details: 'Strong agreement across timeframes'
      },
      'BTC/USDT': {
        confirmed: false,
        agreementRatio: 0.50,
        threshold: 0.6,
        timeframes: ['1d', '4h', '1h'],
        details: 'Conflicting signals between timeframes'
      }
    });
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'buy': return '#00ff88';
      case 'sell': return '#ff4444';
      default: return '#888888';
    }
  };

  const getSentimentColor = (score) => {
    if (score > 0.2) return '#00ff88';
    if (score < -0.2) return '#ff4444';
    return '#ffaa00';
  };

  return (
    <div className="advanced-dashboard">
      <header className="dashboard-header">
        <h1>🤖 AI Trading Bot - Advanced Dashboard</h1>
        <div className="status-indicator online">● LIVE</div>
      </header>

      <div className="dashboard-grid">
        {/* Portfolio Overview */}
        <div className="card portfolio-card">
          <h2>📈 Portfolio Overview</h2>
          {portfolioData && (
            <>
              <div className="portfolio-value">
                <span className="value">{formatCurrency(portfolioData.totalValue)}</span>
                <span className={`change ${portfolioData.dailyChange >= 0 ? 'positive' : 'negative'}`}>
                  {portfolioData.dailyChange >= 0 ? '+' : ''}
                  {formatCurrency(portfolioData.dailyChange)} 
                  ({portfolioData.dailyChangePercent >= 0 ? '+' : ''}{portfolioData.dailyChangePercent}%)
                </span>
              </div>
              <div className="cash-balance">
                Cash: {formatCurrency(portfolioData.cash)}
              </div>
              <div className="positions">
                {portfolioData.positions.map((pos, idx) => (
                  <div key={idx} className="position">
                    <span className="symbol">{pos.symbol}</span>
                    <span className="position-value">{formatCurrency(pos.value)}</span>
                    <span className={`position-change ${pos.change >= 0 ? 'positive' : 'negative'}`}>
                      {pos.change >= 0 ? '+' : ''}{pos.change}%
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Kelly Criterion Metrics */}
        <div className="card kelly-card">
          <h2>🎯 Kelly Criterion Metrics</h2>
          {kellyMetrics && (
            <div className="kelly-metrics">
              <div className="metric">
                <span className="label">Kelly Fraction:</span>
                <span className="value">{(kellyMetrics.kellyFraction * 100).toFixed(1)}%</span>
              </div>
              <div className="metric">
                <span className="label">Win Rate:</span>
                <span className="value">{(kellyMetrics.winRate * 100).toFixed(1)}%</span>
              </div>
              <div className="metric">
                <span className="label">Win/Loss Ratio:</span>
                <span className="value">{kellyMetrics.winLossRatio.toFixed(2)}</span>
              </div>
              <div className="metric">
                <span className="label">Avg Win:</span>
                <span className="value">{formatCurrency(kellyMetrics.avgWin)}</span>
              </div>
              <div className="metric">
                <span className="label">Avg Loss:</span>
                <span className="value">{formatCurrency(kellyMetrics.avgLoss)}</span>
              </div>
              <div className="metric">
                <span className="label">Sample Size:</span>
                <span className="value">{kellyMetrics.sampleSize} trades</span>
              </div>
            </div>
          )}
        </div>

        {/* Multi-Timeframe Signals */}
        <div className="card signals-card">
          <h2>⏰ Multi-Timeframe Signals</h2>
          {multiTimeframeSignals && (
            <div className="signals-grid">
              {Object.entries(multiTimeframeSignals).map(([symbol, signals]) => (
                <div key={symbol} className="signal-group">
                  <h3>{symbol}</h3>
                  <div className="timeframe-signals">
                    {['1d', '4h', '1h'].map(tf => (
                      <div key={tf} className="timeframe-signal">
                        <span className="timeframe">{tf}:</span>
                        <span 
                          className="signal"
                          style={{ color: getSignalColor(signals[tf]?.signal) }}
                        >
                          {signals[tf]?.signal?.toUpperCase()}
                        </span>
                        <span className="confidence">
                          {(signals[tf]?.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))}
                    <div className="combined-signal">
                      <strong>Combined: </strong>
                      <span 
                        style={{ color: getSignalColor(signals.combined?.signal) }}
                      >
                        {signals.combined?.signal?.toUpperCase()}
                      </span>
                      <span className="confidence">
                        ({(signals.combined?.confidence * 100).toFixed(0)}%)
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Enhanced Sentiment Analysis */}
        <div className="card sentiment-card">
          <h2>🧠 Enhanced Sentiment Analysis</h2>
          {sentimentData && (
            <div className="sentiment-grid">
              {Object.entries(sentimentData).map(([symbol, data]) => (
                <div key={symbol} className="sentiment-group">
                  <h3>{symbol}</h3>
                  <div className="combined-sentiment">
                    <span className="label">Combined:</span>
                    <span 
                      className="score"
                      style={{ color: getSentimentColor(data.combined) }}
                    >
                      {data.combined.toFixed(2)}
                    </span>
                  </div>
                  <div className="sentiment-sources">
                    {Object.entries(data.sources).map(([source, sourceData]) => (
                      <div key={source} className="source">
                        <span className="source-name">{source}:</span>
                        <span 
                          className="source-score"
                          style={{ color: getSentimentColor(sourceData.score) }}
                        >
                          {sourceData.score.toFixed(2)}
                        </span>
                        <span className="quality">
                          (Q: {(sourceData.quality * 100).toFixed(0)}%)
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Trades - Enhanced with Phase 2 data */}
        <div className="card trades-card">
          <h2>📋 Recent Trades</h2>
          <div className="trades-table">
            <div className="table-header">
              <span>Date</span>
              <span>Symbol</span>
              <span>Action</span>
              <span>Qty</span>
              <span>Price</span>
              <span>Kelly%</span>
              <span>Corr</span>
              <span>Status</span>
            </div>
            {tradeHistory.map((trade, idx) => (
              <div key={idx} className="table-row">
                <span>{trade.date}</span>
                <span>{trade.symbol}</span>
                <span className={`action ${trade.action.toLowerCase()}`}>
                  {trade.action}
                </span>
                <span>{trade.quantity}</span>
                <span>{formatCurrency(trade.price)}</span>
                <span className="kelly-data">
                  {trade.kellyFraction ? `${(trade.kellyFraction * 100).toFixed(1)}%` : '-'}
                </span>
                <span className={`correlation ${trade.maxCorrelation > 0.7 ? 'high' : trade.maxCorrelation > 0.5 ? 'medium' : 'low'}`}>
                  {trade.maxCorrelation ? trade.maxCorrelation.toFixed(2) : '-'}
                </span>
                <span className={`status ${trade.confirmationStatus.toLowerCase().replace('_', '-')}`}>
                  {trade.confirmationStatus}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Phase 2: Correlation Heatmap */}
        <div className="card correlation-card">
          <h2>🔗 Position Correlation Matrix</h2>
          {correlationMatrix && (
            <div className="correlation-matrix">
              <div className="matrix-grid">
                <div className="matrix-header">
                  <span></span>
                  {correlationMatrix.assets.map(asset => (
                    <span key={asset} className="asset-label">{asset}</span>
                  ))}
                </div>
                {correlationMatrix.matrix.map((row, i) => (
                  <div key={i} className="matrix-row">
                    <span className="asset-label">{correlationMatrix.assets[i]}</span>
                    {row.map((corr, j) => (
                      <span 
                        key={j} 
                        className={`correlation-cell ${
                          corr > 0.7 ? 'high-corr' : 
                          corr > 0.4 ? 'medium-corr' : 
                          'low-corr'
                        }`}
                        title={`Correlation: ${corr.toFixed(3)}`}
                      >
                        {corr.toFixed(2)}
                      </span>
                    ))}
                  </div>
                ))}
              </div>
              <div className="correlation-legend">
                <span className="legend-item">
                  <span className="legend-color high-corr"></span>
                  High (&gt;0.7)
                </span>
                <span className="legend-item">
                  <span className="legend-color medium-corr"></span>
                  Medium (0.4-0.7)
                </span>
                <span className="legend-item">
                  <span className="legend-color low-corr"></span>
                  Low (&lt;0.4)
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Phase 2: Multi-Timeframe Confirmation Status */}
        <div className="card confirmation-card">
          <h2>✅ Timeframe Confirmation Status</h2>
          {confirmationStatus && (
            <div className="confirmation-grid">
              {Object.entries(confirmationStatus).map(([symbol, status]) => (
                <div key={symbol} className="confirmation-item">
                  <div className="confirmation-header">
                    <span className="symbol">{symbol}</span>
                    <span className={`status-badge ${status.confirmed ? 'confirmed' : 'unconfirmed'}`}>
                      {status.confirmed ? '✅ CONFIRMED' : '❌ UNCONFIRMED'}
                    </span>
                  </div>
                  <div className="confirmation-details">
                    <div className="agreement-bar">
                      <div className="bar-container">
                        <div 
                          className="agreement-fill"
                          style={{ 
                            width: `${status.agreementRatio * 100}%`,
                            backgroundColor: status.confirmed ? '#00ff88' : '#ff4444'
                          }}
                        ></div>
                      </div>
                      <span className="agreement-text">
                        {(status.agreementRatio * 100).toFixed(1)}% / {(status.threshold * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="timeframes">
                      Timeframes: {status.timeframes.join(', ')}
                    </div>
                    <div className="details-text">{status.details}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Phase 2: Shadow Mode Control */}
        <div className="card shadow-mode-card">
          <h2>🔮 Shadow Mode</h2>
          <div className="shadow-mode-controls">
            <div className="toggle-container">
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={shadowModeEnabled}
                  onChange={(e) => setShadowModeEnabled(e.target.checked)}
                />
                <span className="slider"></span>
              </label>
              <span className="toggle-label">
                {shadowModeEnabled ? 'Shadow Mode ON' : 'Live Trading ON'}
              </span>
            </div>
            <div className="shadow-mode-description">
              {shadowModeEnabled ? 
                '🔮 Trading signals will be logged but no actual trades will be executed.' :
                '💰 Live trading mode - signals will result in actual trades.'
              }
            </div>
            <div className="shadow-mode-stats">
              <div className="stat">
                <span className="label">Shadow Signals Today:</span>
                <span className="value">12</span>
              </div>
              <div className="stat">
                <span className="label">Hypothetical P&L:</span>
                <span className="value positive">+$145.30</span>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="card performance-card">
          <h2>📊 Performance Metrics</h2>
          <div className="performance-metrics">
            <div className="metric">
              <span className="label">Sharpe Ratio:</span>
              <span className="value">1.45</span>
            </div>
            <div className="metric">
              <span className="label">Max Drawdown:</span>
              <span className="value negative">-5.2%</span>
            </div>
            <div className="metric">
              <span className="label">Total Return:</span>
              <span className="value positive">+24.5%</span>
            </div>
            <div className="metric">
              <span className="label">Multi-TF Accuracy:</span>
              <span className="value">68.3%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedDashboard;