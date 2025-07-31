import React from "react";
import "./App.css";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Options Strategy Backtesting Platform</h1>
        <p>Professional-grade Options pricing and Strategy analysis</p>

        <div className="feature-grid">
          <div className="feature-card">
            <h3>📊 Black-Scholes Pricing</h3>
            <p>
              Professional options valuation with industry-standard mathematical
              models
            </p>
          </div>

          <div className="feature-card">
            <h3>📈 Greeks Analytics</h3>
            <p>
              Complete risk metrics: Delta, Gamma, Theta, Vega, and Rho
              calculations
            </p>
          </div>

          <div className="feature-card">
            <h3>🎯 Strategy Backtesting</h3>
            <p>
              Test trading strategies with historical data and performance
              analytics
            </p>
          </div>

          <div className="feature-card">
            <h3>💼 Portfolio Analysis</h3>
            <p>Comprehensive portfolio tracking and risk management tools</p>
          </div>
        </div>

        <div className="status-section">
          <h2>Platform Status</h2>
          <div className="status-grid">
            <div>
              <p>
                ✅ <strong>Backend API:</strong> http://localhost:8000
              </p>
              <p>
                ✅ <strong>API Documentation:</strong>{" "}
                http://localhost:8000/docs
              </p>
              <p>
                ✅ <strong>Black-Scholes Engine:</strong> Fully Operational
              </p>
            </div>
            <div>
              <p>
                ✅ <strong>Greeks Calculator:</strong> All 5 metrics active
              </p>
              <p>
                ✅ <strong>Strategy Framework:</strong> Ready for backtesting
              </p>
              <p>
                🎯 <strong>Platform:</strong> Production Ready
              </p>
            </div>
          </div>
        </div>

        <footer>
          <p>
            Built by Swati | Quantitative Finance & Full-Stack Development
            Portfolio
          </p>
        </footer>
      </header>
    </div>
  );
}

export default App;
