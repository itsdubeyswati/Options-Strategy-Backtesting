# QuantOptions: Options Strategy Backtesting Platform

A comprehensive options trading strategy analyzer that combines accurate options pricing with robust backtesting capabilities.

## 🎯 Project Overview

QuantOptions is an end-to-end options trading platform that enables systematic options trading with proper risk management. It combines:

- **Options Pricing Engine**: Black-Scholes pricing with Greeks calculations
- **Historical Data Management**: Stock prices and options data with implied volatility
- **Strategy Backtesting Framework**: Test complex options strategies over historical data
- **Performance Analytics**: Advanced metrics for options portfolio analysis

## 🚀 Key Features

### Options Pricing Engine

- Black-Scholes option pricing for any historical date
- Greeks calculations (Delta, Gamma, Theta, Vega, Rho)
- Support for calls, puts, and complex spreads
- Real-time and historical implied volatility

### Backtesting Framework

- **Simple Strategies**: Directional plays (long calls/puts)
- **Income Strategies**: Covered calls, cash-secured puts
- **Spread Strategies**: Iron condors, butterflies, straddles
- **Greeks-based Strategies**: Delta-neutral, gamma scalping

### Performance Analytics

- Standard metrics: Returns, Sharpe ratio, max drawdown
- Options-specific: Time decay profits, volatility P&L
- Risk analysis: Portfolio Greeks, VaR calculations
- Interactive profit/loss diagrams

### Advanced Features

- Monte Carlo simulations
- Strategy comparison tools
- Portfolio-level risk management
- Real-time options chain analysis

## 🏗️ Technology Stack

**Backend:**

- Python 3.9+ (NumPy, Pandas, SciPy)
- FastAPI for REST API
- PostgreSQL for time-series data
- SQLAlchemy ORM
- Asyncio for concurrent data processing

**Frontend:**

- React 18 with TypeScript
- Material-UI for professional interface
- Chart.js/D3.js for interactive charts
- Redux for state management

**Data & Infrastructure:**

- Docker containers
- Redis for caching
- Celery for background tasks
- pytest for testing

## 📁 Project Structure

```
options-strategy-backtesting/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes
│   │   ├── core/             # Core business logic
│   │   ├── models/           # Database models
│   │   ├── services/         # Business services
│   │   └── utils/            # Utility functions
│   ├── data/
│   │   ├── collectors/       # Data collection modules
│   │   ├── processors/       # Data processing
│   │   └── storage/          # Database operations
│   ├── pricing/
│   │   ├── black_scholes.py  # BS pricing engine
│   │   ├── greeks.py         # Greeks calculations
│   │   └── volatility.py     # Volatility models
│   ├── backtesting/
│   │   ├── engine.py         # Backtesting engine
│   │   ├── strategies/       # Trading strategies
│   │   └── portfolio.py      # Portfolio management
│   └── analytics/
│       ├── performance.py    # Performance metrics
│       ├── risk.py          # Risk calculations
│       └── visualization.py  # Chart data prep
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── store/           # Redux store
│   │   └── utils/           # Utility functions
│   ├── public/
│   └── package.json
├── database/
│   ├── migrations/          # Database migrations
│   └── schemas/             # Database schemas
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    ├── api/                 # API documentation
    └── strategies/          # Strategy documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker (optional)

### Installation

1. **Clone and setup backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup database:**

```bash
createdb quantoptions
python manage.py migrate
```

3. **Setup frontend:**

```bash
cd frontend
npm install
```

4. **Run the application:**

```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm start
```

### Docker Setup

```bash
docker-compose up -d
```

## 📊 Usage Examples

### 1. Test a Covered Call Strategy

```python
from backtesting.strategies import CoveredCallStrategy
from backtesting.engine import BacktestEngine

strategy = CoveredCallStrategy(
    symbol="AAPL",
    start_date="2020-01-01",
    end_date="2023-12-31",
    strike_selection="30_delta",  # Sell 30-delta calls
    expiration_days=30
)

engine = BacktestEngine()
results = engine.run_backtest(strategy)
print(f"Annual Return: {results.annual_return:.2%}")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
print(f"Max Drawdown: {results.max_drawdown:.2%}")
```

### 2. Greeks-based Delta Neutral Strategy

```python
from backtesting.strategies import DeltaNeutralStrategy

strategy = DeltaNeutralStrategy(
    symbol="SPY",
    target_delta=0.0,
    rebalance_threshold=0.1,
    strategy_type="short_straddle"
)

results = engine.run_backtest(strategy)
```

### 3. Iron Condor Analysis

```python
from backtesting.strategies import IronCondorStrategy

strategy = IronCondorStrategy(
    symbol="QQQ",
    put_strike_delta=0.16,
    call_strike_delta=0.16,
    wing_width=10,
    expiration_days=45,
    profit_target=0.5,
    stop_loss=2.0
)
```

## 📈 Performance Metrics

### Standard Metrics

- **Total Return**: Cumulative strategy performance
- **Annual Return**: Annualized returns
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades

### Options-Specific Metrics

- **Theta P&L**: Profits from time decay
- **Delta P&L**: Profits from directional moves
- **Gamma P&L**: Profits from gamma scalping
- **Vega P&L**: Profits/losses from volatility changes
- **Greeks Exposure**: Portfolio-level Greeks over time

## 🔬 Research & Development

### Implemented Strategies

1. **Directional**: Long calls/puts, synthetic positions
2. **Income**: Covered calls, cash-secured puts, short strangles
3. **Spread**: Iron condors, butterflies, calendars
4. **Volatility**: Long/short straddles, delta-neutral
5. **Greeks-based**: Gamma scalping, theta collection

### Planned Features

- [ ] Machine learning for volatility prediction
- [ ] Real-time options flow analysis
- [ ] Advanced portfolio optimization
- [ ] Multi-asset strategy combinations
- [ ] Options market making simulations

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Generate coverage report
pytest --cov=app tests/
```

## 📚 Documentation

- [API Documentation](docs/api/README.md)
- [Strategy Guide](docs/strategies/README.md)
- [Database Schema](docs/database/README.md)
- [Deployment Guide](docs/deployment/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Project Goals

This project demonstrates:

- **Advanced Financial Engineering**: Options pricing, Greeks calculations, volatility modeling
- **Software Architecture**: Clean separation of concerns, scalable design
- **Data Engineering**: Efficient time-series data handling, real-time processing
- **Web Development**: Modern full-stack application with React and FastAPI
- **DevOps**: Containerized deployment, CI/CD pipelines
- **Quantitative Finance**: Systematic trading strategy development and validation

Perfect for showcasing comprehensive software development skills in the fintech domain!

---

**Built with ❤️ for systematic options trading**
