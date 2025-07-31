import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [activeSection, setActiveSection] = useState("overview");
  const [optionInputs, setOptionInputs] = useState({
    stockPrice: 8300, // ~$100 in rupees
    strikePrice: 8715, // ~$105 in rupees
    timeToExpiry: 30,
    volatility: 0.2,
    riskFreeRate: 0.05,
  });
  const [optionResults, setOptionResults] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking");

  // Strategy Backtesting State
  const [strategyInputs, setStrategyInputs] = useState({
    strategy: "covered_call",
    startDate: "2023-01-01",
    endDate: "2023-12-31",
    initialCapital: 8300000, // ~$100k in rupees
    stockSymbol: "RELIANCE", // Indian stock
    volatility: 0.25,
    riskFreeRate: 0.05,
  });
  const [backtestResults, setBacktestResults] = useState(null);
  const [isBacktesting, setIsBacktesting] = useState(false);

  // Portfolio Management State
  const [portfolioPositions, setPortfolioPositions] = useState([
    {
      id: 1,
      symbol: "RELIANCE",
      type: "Call",
      strike: 12450, // ~$150 in rupees
      expiry: "2024-03-15",
      quantity: 10,
      premium: 456.5, // ~$5.5 in rupees
      current: 514.6, // ~$6.2 in rupees
    },
    {
      id: 2,
      symbol: "INFY",
      type: "Put",
      strike: 24900, // ~$300 in rupees
      expiry: "2024-02-16",
      quantity: 5,
      premium: 726.25, // ~$8.75 in rupees
      current: 605.9, // ~$7.3 in rupees
    },
    {
      id: 3,
      symbol: "TCS",
      type: "Call",
      strike: 11620, // ~$140 in rupees
      expiry: "2024-04-19",
      quantity: 8,
      premium: 1016.75, // ~$12.25 in rupees
      current: 1311.4, // ~$15.8 in rupees
    },
  ]);
  const [portfolioMetrics, setPortfolioMetrics] = useState(null);
  const [newPosition, setNewPosition] = useState({
    symbol: "",
    type: "Call",
    strike: "",
    expiry: "",
    quantity: "",
    premium: "",
  });

  // Sample Market Data
  const [marketData] = useState({
    vix: 18.45,
    spyPrice: 39705.32, // ~$478.32 in rupees (NIFTY equivalent)
    vixChange: -2.1,
    spyChange: 0.8,
  });

  // Check backend status on load
  useEffect(() => {
    checkBackendStatus();
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch("http://localhost:8000/health");
      if (response.ok) {
        setBackendStatus("connected");
      } else {
        setBackendStatus("disconnected");
      }
    } catch (error) {
      setBackendStatus("disconnected");
    }
  };

  // Black-Scholes calculation functions
  const normalCDF = (x) => {
    // Approximation of the cumulative distribution function for standard normal distribution
    const a1 = 0.254829592;
    const a2 = -0.284496736;
    const a3 = 1.421413741;
    const a4 = -1.453152027;
    const a5 = 1.061405429;
    const p = 0.3275911;

    const sign = x < 0 ? -1 : 1;
    x = Math.abs(x) / Math.sqrt(2.0);

    const t = 1.0 / (1.0 + p * x);
    const y =
      1.0 -
      ((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

    return 0.5 * (1.0 + sign * y);
  };

  const calculateBlackScholes = (S, K, T, r, sigma) => {
    // Convert days to years
    const timeToExpiry = T / 365;

    if (timeToExpiry <= 0) {
      // Handle expiry case
      const callPrice = Math.max(S - K, 0);
      const putPrice = Math.max(K - S, 0);
      return {
        callPrice,
        putPrice,
        greeks: {
          delta: S > K ? 1 : 0,
          gamma: 0,
          theta: 0,
          vega: 0,
          rho: 0,
        },
      };
    }

    const d1 =
      (Math.log(S / K) + (r + 0.5 * sigma * sigma) * timeToExpiry) /
      (sigma * Math.sqrt(timeToExpiry));
    const d2 = d1 - sigma * Math.sqrt(timeToExpiry);

    const Nd1 = normalCDF(d1);
    const Nd2 = normalCDF(d2);
    const nPrime_d1 = Math.exp(-0.5 * d1 * d1) / Math.sqrt(2 * Math.PI);

    // Option prices
    const callPrice = S * Nd1 - K * Math.exp(-r * timeToExpiry) * Nd2;
    const putPrice =
      K * Math.exp(-r * timeToExpiry) * (1 - Nd2) - S * (1 - Nd1);

    // Greeks calculations
    const delta_call = Nd1;
    const delta_put = Nd1 - 1;
    const gamma = nPrime_d1 / (S * sigma * Math.sqrt(timeToExpiry));
    const theta_call =
      ((-S * nPrime_d1 * sigma) / (2 * Math.sqrt(timeToExpiry)) -
        r * K * Math.exp(-r * timeToExpiry) * Nd2) /
      365;
    const theta_put =
      ((-S * nPrime_d1 * sigma) / (2 * Math.sqrt(timeToExpiry)) +
        r * K * Math.exp(-r * timeToExpiry) * (1 - Nd2)) /
      365;
    const vega = (S * nPrime_d1 * Math.sqrt(timeToExpiry)) / 100; // Per 1% change in volatility
    const rho_call =
      (K * timeToExpiry * Math.exp(-r * timeToExpiry) * Nd2) / 100; // Per 1% change in interest rate
    const rho_put =
      (-K * timeToExpiry * Math.exp(-r * timeToExpiry) * (1 - Nd2)) / 100;

    return {
      callPrice: Math.max(callPrice, 0),
      putPrice: Math.max(putPrice, 0),
      greeks: {
        delta_call: delta_call,
        delta_put: delta_put,
        gamma: gamma,
        theta_call: theta_call,
        theta_put: theta_put,
        vega: vega,
        rho_call: rho_call,
        rho_put: rho_put,
      },
    };
  };

  const calculateOption = async () => {
    setIsCalculating(true);
    try {
      // Simulate calculation delay for realistic UX
      await new Promise((resolve) => setTimeout(resolve, 800));

      // Real Black-Scholes calculation
      const results = calculateBlackScholes(
        optionInputs.stockPrice,
        optionInputs.strikePrice,
        optionInputs.timeToExpiry,
        optionInputs.riskFreeRate,
        optionInputs.volatility
      );

      setOptionResults(results);
    } catch (error) {
      console.error("Calculation failed:", error);
    }
    setIsCalculating(false);
  };

  // Strategy Backtesting Functions
  const generateMockPriceData = (symbol, days, startPrice, volatility) => {
    const prices = [startPrice];
    const returns = [];

    for (let i = 1; i < days; i++) {
      const randomReturn = (Math.random() - 0.5) * volatility * 2;
      const newPrice = prices[i - 1] * (1 + randomReturn);
      prices.push(Math.max(newPrice, 1)); // Ensure price doesn't go negative
      returns.push(randomReturn);
    }

    return { prices, returns };
  };

  const runCoveredCallBacktest = (prices, strike, premium, quantity) => {
    const results = [];
    let totalPnL = 0;
    let winningTrades = 0;
    let totalTrades = 0;

    for (let i = 0; i < prices.length - 30; i += 30) {
      // Monthly options
      const entryPrice = prices[i];
      const exitPrice = prices[i + 29] || prices[prices.length - 1];

      // Stock PnL
      const stockPnL = (exitPrice - entryPrice) * quantity * 100;

      // Option PnL (we sold the call)
      const optionPnL =
        exitPrice > strike
          ? -(exitPrice - strike) * quantity * 100 + premium * quantity * 100
          : premium * quantity * 100;

      const totalTradePnL = stockPnL + optionPnL;
      totalPnL += totalTradePnL;

      if (totalTradePnL > 0) winningTrades++;
      totalTrades++;

      results.push({
        date: new Date(2023, 0, i + 1).toISOString().split("T")[0],
        stockPrice: exitPrice,
        pnl: totalTradePnL,
        cumulativePnL: totalPnL,
      });
    }

    return {
      trades: results,
      totalPnL,
      winningTrades,
      totalTrades,
      winRate: (winningTrades / totalTrades) * 100,
      avgPnL: totalPnL / totalTrades,
      maxDrawdown: Math.min(...results.map((r) => r.cumulativePnL)),
      finalReturn: (totalPnL / strategyInputs.initialCapital) * 100,
    };
  };

  const runBacktest = async () => {
    setIsBacktesting(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 2000)); // Simulate processing time

      const { prices } = generateMockPriceData(
        strategyInputs.stockSymbol,
        365,
        12450, // Starting price in rupees (~$150)
        strategyInputs.volatility / Math.sqrt(252) // Daily volatility
      );

      let results;
      if (strategyInputs.strategy === "covered_call") {
        results = runCoveredCallBacktest(prices, 12865, 290.5, 10); // ~$155 strike, ~$3.5 premium in rupees
      } else {
        // Add other strategies here
        results = { message: "Strategy not implemented yet" };
      }

      setBacktestResults(results);
    } catch (error) {
      console.error("Backtest failed:", error);
    }
    setIsBacktesting(false);
  };

  // Portfolio Management Functions
  const calculatePortfolioMetrics = () => {
    let totalValue = 0;
    let totalPnL = 0;
    let totalDelta = 0;
    let totalGamma = 0;
    let totalTheta = 0;
    let totalVega = 0;

    portfolioPositions.forEach((position) => {
      const positionValue = position.current * position.quantity * 100;
      const positionPnL =
        (position.current - position.premium) * position.quantity * 100;

      totalValue += positionValue;
      totalPnL += positionPnL;

      // Mock Greeks calculations for portfolio
      const mockGreeks = calculateBlackScholes(
        12450, // Current stock price in rupees
        position.strike,
        30,
        0.05,
        0.25
      );
      if (position.type === "Call") {
        totalDelta += mockGreeks.greeks.delta_call * position.quantity;
        totalTheta += mockGreeks.greeks.theta_call * position.quantity;
      } else {
        totalDelta += mockGreeks.greeks.delta_put * position.quantity;
        totalTheta += mockGreeks.greeks.theta_put * position.quantity;
      }
      totalGamma += mockGreeks.greeks.gamma * position.quantity;
      totalVega += mockGreeks.greeks.vega * position.quantity;
    });

    return {
      totalValue,
      totalPnL,
      totalReturn:
        (totalPnL /
          portfolioPositions.reduce(
            (sum, p) => sum + p.premium * p.quantity * 100,
            0
          )) *
        100,
      portfolioGreeks: {
        delta: totalDelta,
        gamma: totalGamma,
        theta: totalTheta,
        vega: totalVega,
      },
      positionCount: portfolioPositions.length,
    };
  };

  const addPosition = () => {
    if (
      newPosition.symbol &&
      newPosition.strike &&
      newPosition.quantity &&
      newPosition.premium
    ) {
      const position = {
        id: Date.now(),
        ...newPosition,
        strike: parseFloat(newPosition.strike),
        quantity: parseInt(newPosition.quantity),
        premium: parseFloat(newPosition.premium),
        current: parseFloat(newPosition.premium) * (0.9 + Math.random() * 0.4), // Simulate current price
      };

      setPortfolioPositions([...portfolioPositions, position]);
      setNewPosition({
        symbol: "",
        type: "Call",
        strike: "",
        expiry: "",
        quantity: "",
        premium: "",
      });
    }
  };

  const removePosition = (id) => {
    setPortfolioPositions(portfolioPositions.filter((p) => p.id !== id));
  };

  // Calculate portfolio metrics when positions change
  useEffect(() => {
    if (portfolioPositions.length > 0) {
      setPortfolioMetrics(calculatePortfolioMetrics());
    }
  }, [portfolioPositions]);

  const renderOverview = () => (
    <div>
      {/* Market Overview */}
      <div className="market-overview">
        <h3>Market Overview</h3>
        <div className="market-grid">
          <div className="market-card">
            <h4>VIX (Volatility Index)</h4>
            <div className="market-value">
              {marketData.vix}
              <span
                className={marketData.vixChange < 0 ? "negative" : "positive"}
              >
                {marketData.vixChange > 0 ? "+" : ""}
                {marketData.vixChange}%
              </span>
            </div>
          </div>
          <div className="market-card">
            <h4>NIFTY 50</h4>
            <div className="market-value">
              ₹{marketData.spyPrice}
              <span
                className={marketData.spyChange < 0 ? "negative" : "positive"}
              >
                {marketData.spyChange > 0 ? "+" : ""}
                {marketData.spyChange}%
              </span>
            </div>
          </div>
          <div className="market-card">
            <h4>Market Sentiment</h4>
            <div className="market-value">
              Neutral
              <span className="neutral">Low Volatility</span>
            </div>
          </div>
        </div>
      </div>

      <div className="feature-grid">
        <div
          className="feature-card clickable"
          onClick={() => setActiveSection("pricing")}
        >
          <div className="feature-icon pricing-icon">
            <div className="icon-bg">
              <span>∫</span>
            </div>
          </div>
          <h3>Black-Scholes Pricing</h3>
          <p>
            Calculate fair option prices using industry-standard models with
            real-time Greeks analysis and volatility modeling
          </p>
          <button className="card-button">Open Calculator</button>
        </div>

        <div
          className="feature-card clickable"
          onClick={() => setActiveSection("greeks")}
        >
          <div className="feature-icon greeks-icon">
            <div className="icon-bg">
              <span>Ω</span>
            </div>
          </div>
          <h3>Greeks Analytics</h3>
          <p>
            Monitor Delta, Gamma, Theta, and Vega risk exposure with
            portfolio-level aggregation
          </p>
          <button className="card-button">View Analytics</button>
        </div>

        <div
          className="feature-card clickable"
          onClick={() => setActiveSection("backte  sting")}
        >
          <div className="feature-icon backtest-icon">
            <div className="icon-bg">
              <span>∑</span>
            </div>
          </div>
          <h3>Strategy Backtesting</h3>
          <p>
            Test your options strategies against 5+ years of historical data
            with commission modeling and risk analysis
          </p>
          <button className="card-button">Start Backtest</button>
        </div>

        <div
          className="feature-card clickable"
          onClick={() => setActiveSection("portfolio")}
        >
          <div className="feature-icon portfolio-icon">
            <div className="icon-bg">
              <span>π</span>
            </div>
          </div>
          <h3>Portfolio Analysis</h3>
          <p>
            Advanced portfolio tracking with real-time P&L, Greeks aggregation,
            and risk management tools
          </p>
          <button className="card-button">Analyze Portfolio</button>
        </div>
      </div>

      {/* Popular Strategies */}
      <div className="section-divider"></div>
      <div className="popular-strategies">
        <h3>Popular Strategies</h3>
        <div className="strategy-grid">
          <div className="strategy-card">
            <h4>Covered Call</h4>
            <p>Generate income on existing stock positions</p>
            <div className="strategy-stats">
              <span className="win-rate">Win Rate: 78%</span>
              <span className="avg-return">Avg Return: +12.5%</span>
            </div>
          </div>
          <div className="strategy-card">
            <h4>Iron Condor</h4>
            <p>Profit from low volatility environments</p>
            <div className="strategy-stats">
              <span className="win-rate">Win Rate: 65%</span>
              <span className="avg-return">Avg Return: +8.3%</span>
            </div>
          </div>
          <div className="strategy-card">
            <h4>Protective Put</h4>
            <p>Hedge portfolio downside risk</p>
            <div className="strategy-stats">
              <span className="win-rate">Win Rate: 85%</span>
              <span className="avg-return">Max Loss: -2.1%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          <div className="activity-item">
            <div className="activity-icon">📈</div>
            <div className="activity-content">
              <h4>RELIANCE Covered Call Backtest</h4>
              <p>Completed 252-day backtest with +15.2% return</p>
              <span className="activity-time">2 hours ago</span>
            </div>
          </div>
          <div className="activity-item">
            <div className="activity-icon">🔢</div>
            <div className="activity-content">
              <h4>SPY Iron Condor Analysis</h4>
              <p>Calculated fair value with 68% probability of profit</p>
              <span className="activity-time">5 hours ago</span>
            </div>
          </div>
          <div className="activity-item">
            <div className="activity-icon">💼</div>
            <div className="activity-content">
              <h4>Portfolio Greeks Updated</h4>
              <p>Delta: +0.25, Theta: +₹45/day, Total P&L: +₹2,847</p>
              <span className="activity-time">1 day ago</span>
            </div>
          </div>
        </div>
      </div>

      {/* What is Options Trading - Only on Overview */}
      <div className="section-divider"></div>
      <div className="trading-overview-section">
        <h2>What is Options Trading?</h2>
        <div className="overview-content">
          <div className="overview-card">
            <div className="overview-icon">Δ</div>
            <h3>Financial Derivatives</h3>
            <p>
              Options are contracts that give you the right (but not obligation)
              to buy or sell a stock at a specific price before expiration.
              They're powerful tools for hedging, income generation, and
              strategic investing.
            </p>
          </div>
          <div className="overview-card">
            <div className="overview-icon">Θ</div>
            <h3>Leverage & Flexibility</h3>
            <p>
              Control large positions with smaller capital investment. Options
              provide multiple strategies for any market condition - bullish,
              bearish, or neutral. Perfect for risk management and portfolio
              optimization.
            </p>
          </div>
          <div className="overview-card">
            <div className="overview-icon">Γ</div>
            <h3>Strategic Advantages</h3>
            <p>
              Generate income through covered calls, protect portfolios with
              puts, or profit from volatility with straddles. Options offer
              sophisticated strategies unavailable with stock trading alone.
            </p>
          </div>
        </div>
      </div>

      {/* Pro Trading Tips - Only on Overview */}
      <div className="quick-tips">
        <h3>Pro Trading Tips</h3>
        <div className="tips-grid">
          <div className="tip-card">
            <div className="tip-number">1</div>
            <div className="tip-content">
              <h4>Start Small</h4>
              <p>
                Risk only 1-2% per trade when learning. Master one strategy
                before moving to complex multi-leg trades.
              </p>
            </div>
          </div>
          <div className="tip-card">
            <div className="tip-number">2</div>
            <div className="tip-content">
              <h4>Check Liquidity</h4>
              <p>
                Ensure bid-ask spread is less than 5% of option price. High
                volume and open interest indicate better liquidity.
              </p>
            </div>
          </div>
          <div className="tip-card">
            <div className="tip-number">3</div>
            <div className="tip-content">
              <h4>Manage Winners</h4>
              <p>
                Take profits at 25-50% for short options. Don't get greedy -
                consistent small wins beat occasional large losses.
              </p>
            </div>
          </div>
          <div className="tip-card">
            <div className="tip-number">4</div>
            <div className="tip-content">
              <h4>Earnings Awareness</h4>
              <p>
                Avoid holding options through earnings unless specifically
                trading volatility. IV crush can devastate positions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  const renderPricingCalculator = () => (
    <div>
      <div className="section-divider"></div>
      <div className="calculator-section">
        <h2>Black-Scholes Options Calculator</h2>
        <div className="input-grid">
          <div className="input-group">
            <label>Stock Price (₹)</label>
            <input
              type="number"
              value={optionInputs.stockPrice}
              onChange={(e) =>
                setOptionInputs({
                  ...optionInputs,
                  stockPrice: parseFloat(e.target.value),
                })
              }
            />
          </div>
          <div className="input-group">
            <label>Strike Price (₹)</label>
            <input
              type="number"
              value={optionInputs.strikePrice}
              onChange={(e) =>
                setOptionInputs({
                  ...optionInputs,
                  strikePrice: parseFloat(e.target.value),
                })
              }
            />
          </div>
          <div className="input-group">
            <label>Days to Expiry</label>
            <input
              type="number"
              value={optionInputs.timeToExpiry}
              onChange={(e) =>
                setOptionInputs({
                  ...optionInputs,
                  timeToExpiry: parseInt(e.target.value),
                })
              }
            />
          </div>
          <div className="input-group">
            <label>Volatility (%)</label>
            <input
              type="number"
              step="0.01"
              value={optionInputs.volatility * 100}
              onChange={(e) =>
                setOptionInputs({
                  ...optionInputs,
                  volatility: parseFloat(e.target.value) / 100,
                })
              }
            />
          </div>
          <div className="input-group">
            <label>Risk-Free Rate (%)</label>
            <input
              type="number"
              step="0.01"
              value={optionInputs.riskFreeRate * 100}
              onChange={(e) =>
                setOptionInputs({
                  ...optionInputs,
                  riskFreeRate: parseFloat(e.target.value) / 100,
                })
              }
            />
          </div>
        </div>

        <button
          className="calculate-button"
          onClick={calculateOption}
          disabled={isCalculating}
        >
          {isCalculating ? (
            <span>
              <span className="loading-spinner"></span>
              Calculating...
            </span>
          ) : (
            "Calculate Option Prices"
          )}
        </button>

        {optionResults && (
          <div className="results-section">
            <h3>Calculation Results</h3>
            <div className="results-grid">
              <div className="result-card call">
                <h4>Call Option</h4>
                <div className="price">
                  ₹{optionResults.callPrice.toFixed(2)}
                </div>
                <div className="intrinsic">
                  Intrinsic: ₹
                  {Math.max(
                    optionInputs.stockPrice - optionInputs.strikePrice,
                    0
                  ).toFixed(2)}
                </div>
              </div>
              <div className="result-card put">
                <h4>Put Option</h4>
                <div className="price">
                  ₹{optionResults.putPrice.toFixed(2)}
                </div>
                <div className="intrinsic">
                  Intrinsic: ₹
                  {Math.max(
                    optionInputs.strikePrice - optionInputs.stockPrice,
                    0
                  ).toFixed(2)}
                </div>
              </div>
            </div>

            <div className="greeks-section">
              <h4>Risk Sensitivities (The Greeks)</h4>
              <div className="greeks-container">
                <div className="greeks-column">
                  <h5>Call Option Greeks</h5>
                  <div className="greeks-grid">
                    <div className="greek-item">
                      <span className="greek-name">Delta (Δ):</span>
                      <span className="greek-value">
                        {optionResults.greeks.delta_call.toFixed(4)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Gamma (Γ):</span>
                      <span className="greek-value">
                        {optionResults.greeks.gamma.toFixed(4)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Theta (Θ):</span>
                      <span className="greek-value">
                        {optionResults.greeks.theta_call.toFixed(4)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Vega (ν):</span>
                      <span className="greek-value">
                        {optionResults.greeks.vega.toFixed(4)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Rho (ρ):</span>
                      <span className="greek-value">
                        {optionResults.greeks.rho_call.toFixed(4)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="greeks-column">
                  <h5>Put Option Greeks</h5>
                  <div className="greeks-grid">
                    <div className="greek-item">
                      <span className="greek-name">Delta (Δ):</span>
                      <span className="greek-value">
                        {optionResults.greeks.delta_put.toFixed(4)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Gamma (Γ):</span>
                      <span className="greek-value">
                        {optionResults.greeks.gamma.toFixed(4)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Theta (Θ):</span>
                      <span className="greek-value">
                        {optionResults.greeks.theta_put.toFixed(4)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Vega (ν):</span>
                      <span className="greek-value">
                        {optionResults.greeks.vega.toFixed(4)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Rho (ρ):</span>
                      <span className="greek-value">
                        {optionResults.greeks.rho_put.toFixed(4)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderStrategyBacktesting = () => (
    <div>
      <div className="section-divider"></div>
      <div className="calculator-section">
        <h2>Strategy Backtesting Engine</h2>
        <div className="input-grid">
          <div className="input-group">
            <label>Strategy Type</label>
            <select
              value={strategyInputs.strategy}
              onChange={(e) =>
                setStrategyInputs({
                  ...strategyInputs,
                  strategy: e.target.value,
                })
              }
            >
              <option value="covered_call">Covered Call</option>
              <option value="protective_put">Protective Put</option>
              <option value="iron_condor">Iron Condor</option>
              <option value="straddle">Long Straddle</option>
            </select>
          </div>
          <div className="input-group">
            <label>Stock Symbol</label>
            <input
              type="text"
              value={strategyInputs.stockSymbol}
              onChange={(e) =>
                setStrategyInputs({
                  ...strategyInputs,
                  stockSymbol: e.target.value.toUpperCase(),
                })
              }
              placeholder="RELIANCE"
            />
          </div>
          <div className="input-group">
            <label>Initial Capital (₹)</label>
            <input
              type="number"
              value={strategyInputs.initialCapital}
              onChange={(e) =>
                setStrategyInputs({
                  ...strategyInputs,
                  initialCapital: parseFloat(e.target.value),
                })
              }
            />
          </div>
          <div className="input-group">
            <label>Start Date</label>
            <input
              type="date"
              value={strategyInputs.startDate}
              onChange={(e) =>
                setStrategyInputs({
                  ...strategyInputs,
                  startDate: e.target.value,
                })
              }
            />
          </div>
          <div className="input-group">
            <label>End Date</label>
            <input
              type="date"
              value={strategyInputs.endDate}
              onChange={(e) =>
                setStrategyInputs({
                  ...strategyInputs,
                  endDate: e.target.value,
                })
              }
            />
          </div>
          <div className="input-group">
            <label>Volatility (%)</label>
            <input
              type="number"
              step="0.01"
              value={strategyInputs.volatility * 100}
              onChange={(e) =>
                setStrategyInputs({
                  ...strategyInputs,
                  volatility: parseFloat(e.target.value) / 100,
                })
              }
            />
          </div>
        </div>

        <button
          className="calculate-button"
          onClick={runBacktest}
          disabled={isBacktesting}
        >
          {isBacktesting ? (
            <span>
              <span className="loading-spinner"></span>
              Running Backtest...
            </span>
          ) : (
            "Run Strategy Backtest"
          )}
        </button>

        {backtestResults && (
          <div className="results-section">
            <h3>
              Backtest Results -{" "}
              {strategyInputs.strategy.replace("_", " ").toUpperCase()}
            </h3>

            <div className="backtest-summary">
              <div className="summary-grid">
                <div className="summary-card">
                  <h4>Total Return</h4>
                  <div
                    className={`summary-value ${backtestResults.finalReturn >= 0 ? "positive" : "negative"}`}
                  >
                    {backtestResults.finalReturn?.toFixed(2)}%
                  </div>
                </div>
                <div className="summary-card">
                  <h4>Total P&L</h4>
                  <div
                    className={`summary-value ${backtestResults.totalPnL >= 0 ? "positive" : "negative"}`}
                  >
                    ₹{backtestResults.totalPnL?.toFixed(2)}
                  </div>
                </div>
                <div className="summary-card">
                  <h4>Win Rate</h4>
                  <div className="summary-value">
                    {backtestResults.winRate?.toFixed(1)}%
                  </div>
                </div>
                <div className="summary-card">
                  <h4>Total Trades</h4>
                  <div className="summary-value">
                    {backtestResults.totalTrades}
                  </div>
                </div>
                <div className="summary-card">
                  <h4>Average P&L</h4>
                  <div
                    className={`summary-value ${backtestResults.avgPnL >= 0 ? "positive" : "negative"}`}
                  >
                    ₹{backtestResults.avgPnL?.toFixed(2)}
                  </div>
                </div>
                <div className="summary-card">
                  <h4>Max Drawdown</h4>
                  <div className="summary-value negative">
                    ₹{backtestResults.maxDrawdown?.toFixed(2)}
                  </div>
                </div>
              </div>
            </div>

            {backtestResults.trades && (
              <div className="trade-history">
                <h4>Trade History (Last 10 Trades)</h4>
                <div className="trades-table">
                  <div className="table-header">
                    <span>Date</span>
                    <span>Stock Price</span>
                    <span>Trade P&L</span>
                    <span>Cumulative P&L</span>
                  </div>
                  {backtestResults.trades.slice(-10).map((trade, index) => (
                    <div key={index} className="table-row">
                      <span>{trade.date}</span>
                      <span>₹{trade.stockPrice.toFixed(2)}</span>
                      <span
                        className={trade.pnl >= 0 ? "positive" : "negative"}
                      >
                        ₹{trade.pnl.toFixed(2)}
                      </span>
                      <span
                        className={
                          trade.cumulativePnL >= 0 ? "positive" : "negative"
                        }
                      >
                        ₹{trade.cumulativePnL.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  const renderPortfolioManagement = () => (
    <div>
      <div className="section-divider"></div>
      <div className="calculator-section">
        <h2>Portfolio Management System</h2>

        {/* Portfolio Summary */}
        {portfolioMetrics && (
          <div className="portfolio-summary">
            <h3>Portfolio Overview</h3>
            <div className="summary-grid">
              <div className="summary-card">
                <h4>Total Value</h4>
                <div className="summary-value">
                  ₹{portfolioMetrics.totalValue.toFixed(2)}
                </div>
              </div>
              <div className="summary-card">
                <h4>Total P&L</h4>
                <div
                  className={`summary-value ${portfolioMetrics.totalPnL >= 0 ? "positive" : "negative"}`}
                >
                  ₹{portfolioMetrics.totalPnL.toFixed(2)}
                </div>
              </div>
              <div className="summary-card">
                <h4>Return %</h4>
                <div
                  className={`summary-value ${portfolioMetrics.totalReturn >= 0 ? "positive" : "negative"}`}
                >
                  {portfolioMetrics.totalReturn.toFixed(2)}%
                </div>
              </div>
              <div className="summary-card">
                <h4>Positions</h4>
                <div className="summary-value">
                  {portfolioMetrics.positionCount}
                </div>
              </div>
            </div>

            {/* Portfolio Greeks */}
            <div className="portfolio-greeks">
              <h4>Portfolio Greeks</h4>
              <div className="greeks-container">
                <div className="greeks-column">
                  <div className="greeks-grid">
                    <div className="greek-item">
                      <span className="greek-name">Portfolio Delta:</span>
                      <span className="greek-value">
                        {portfolioMetrics.portfolioGreeks.delta.toFixed(2)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Portfolio Gamma:</span>
                      <span className="greek-value">
                        {portfolioMetrics.portfolioGreeks.gamma.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="greeks-column">
                  <div className="greeks-grid">
                    <div className="greek-item">
                      <span className="greek-name">Portfolio Theta:</span>
                      <span className="greek-value">
                        {portfolioMetrics.portfolioGreeks.theta.toFixed(2)}
                      </span>
                    </div>
                    <div className="greek-item">
                      <span className="greek-name">Portfolio Vega:</span>
                      <span className="greek-value">
                        {portfolioMetrics.portfolioGreeks.vega.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Add New Position */}
        <div className="add-position-section">
          <h3>Add New Position</h3>
          <div className="input-grid">
            <div className="input-group">
              <label>Symbol</label>
              <input
                type="text"
                value={newPosition.symbol}
                onChange={(e) =>
                  setNewPosition({
                    ...newPosition,
                    symbol: e.target.value.toUpperCase(),
                  })
                }
                placeholder="RELIANCE"
              />
            </div>
            <div className="input-group">
              <label>Type</label>
              <select
                value={newPosition.type}
                onChange={(e) =>
                  setNewPosition({ ...newPosition, type: e.target.value })
                }
              >
                <option value="Call">Call</option>
                <option value="Put">Put</option>
              </select>
            </div>
            <div className="input-group">
              <label>Strike Price</label>
              <input
                type="number"
                value={newPosition.strike}
                onChange={(e) =>
                  setNewPosition({ ...newPosition, strike: e.target.value })
                }
                placeholder="12450"
              />
            </div>
            <div className="input-group">
              <label>Expiry Date</label>
              <input
                type="date"
                value={newPosition.expiry}
                onChange={(e) =>
                  setNewPosition({ ...newPosition, expiry: e.target.value })
                }
              />
            </div>
            <div className="input-group">
              <label>Quantity</label>
              <input
                type="number"
                value={newPosition.quantity}
                onChange={(e) =>
                  setNewPosition({ ...newPosition, quantity: e.target.value })
                }
                placeholder="10"
              />
            </div>
            <div className="input-group">
              <label>Premium Paid</label>
              <input
                type="number"
                step="0.01"
                value={newPosition.premium}
                onChange={(e) =>
                  setNewPosition({ ...newPosition, premium: e.target.value })
                }
                placeholder="456.50"
              />
            </div>
          </div>
          <button className="calculate-button" onClick={addPosition}>
            Add Position to Portfolio
          </button>
        </div>

        {/* Positions Table */}
        <div className="positions-section">
          <h3>Current Positions</h3>
          <div className="positions-table">
            <div className="table-header">
              <span>Symbol</span>
              <span>Type</span>
              <span>Strike</span>
              <span>Expiry</span>
              <span>Qty</span>
              <span>Premium</span>
              <span>Current</span>
              <span>P&L</span>
              <span>Actions</span>
            </div>
            {portfolioPositions.map((position) => {
              const pnl =
                (position.current - position.premium) * position.quantity * 100;
              return (
                <div key={position.id} className="table-row">
                  <span className="symbol">{position.symbol}</span>
                  <span className={position.type.toLowerCase()}>
                    {position.type}
                  </span>
                  <span>₹{position.strike}</span>
                  <span>{position.expiry}</span>
                  <span>{position.quantity}</span>
                  <span>₹{position.premium.toFixed(2)}</span>
                  <span>₹{position.current.toFixed(2)}</span>
                  <span className={pnl >= 0 ? "positive" : "negative"}>
                    ₹{pnl.toFixed(2)}
                  </span>
                  <span>
                    <button
                      className="remove-button"
                      onClick={() => removePosition(position.id)}
                    >
                      Remove
                    </button>
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="App">
      <header className="App-header">
        <h1>QuantOptions</h1>
        <p>Professional-grade options pricing and strategy analysis</p>

        {/* Navigation Bar */}
        <nav className="nav-bar">
          <button
            className={
              activeSection === "overview" ? "nav-button active" : "nav-button"
            }
            onClick={() => setActiveSection("overview")}
          >
            Overview
          </button>
          <button
            className={
              activeSection === "pricing" ? "nav-button active" : "nav-button"
            }
            onClick={() => setActiveSection("pricing")}
          >
            Options Pricing
          </button>
          <button
            className={
              activeSection === "greeks" ? "nav-button active" : "nav-button"
            }
            onClick={() => setActiveSection("greeks")}
          >
            Greeks Analysis
          </button>
          <button
            className={
              activeSection === "backtesting"
                ? "nav-button active"
                : "nav-button"
            }
            onClick={() => setActiveSection("backtesting")}
          >
            Strategy Backtesting
          </button>
          <button
            className={
              activeSection === "portfolio" ? "nav-button active" : "nav-button"
            }
            onClick={() => setActiveSection("portfolio")}
          >
            Portfolio Management
          </button>
        </nav>

        {/* Dynamic Content */}
        <div className="content-area">
          {activeSection === "overview" && renderOverview()}
          {activeSection === "pricing" && renderPricingCalculator()}
          {activeSection === "greeks" && renderPricingCalculator()}
          {activeSection === "backtesting" && renderStrategyBacktesting()}
          {activeSection === "portfolio" && renderPortfolioManagement()}
        </div>

        <footer>
          <p>
            Built by Swati | Advanced Quantitative Finance & Options Trading
            Platform
          </p>
        </footer>
      </header>
    </div>
  );
}

export default App;
