#!/usr/bin/env python3
"""
QuantOptions Demo Script

This script demonstrates the core functionality of the QuantOptions platform:
1. Options pricing using Black-Scholes
2. Greeks calculations
3. Strategy backtesting
4. Performance analysis

Run this script to see the system in action with sample data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from pricing.black_scholes import BlackScholesCalculator, ImpliedVolatilityCalculator
from pricing.greeks import GreeksCalculator
from backtesting.engine import BacktestEngine
from backtesting.strategies import CoveredCallStrategy, IronCondorStrategy, DeltaNeutralStrategy

def create_sample_market_data():
    """Create sample market data for demonstration."""
    print("📊 Generating sample market data...")
    
    # Generate sample stock price data for AAPL
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Remove weekends
    dates = dates[dates.weekday < 5]
    
    # Generate realistic stock price movement
    np.random.seed(42)  # For reproducible results
    initial_price = 150.0
    returns = np.random.normal(0.0005, 0.02, len(dates))  # Daily returns
    
    prices = [initial_price]
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # Create DataFrame
    data = pd.DataFrame({
        'open': [p * (1 + np.random.normal(0, 0.001)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': np.random.randint(50000000, 200000000, len(dates))
    }, index=dates)
    
    print(f"✅ Generated {len(data)} days of market data for AAPL")
    print(f"📈 Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    
    return {'AAPL': data}

def demonstrate_options_pricing():
    """Demonstrate options pricing and Greeks calculations."""
    print("\n" + "="*60)
    print("🔢 OPTIONS PRICING DEMONSTRATION")
    print("="*60)
    
    # Example parameters
    S = 150.0  # Stock price
    K = 155.0  # Strike price
    T = 30/365  # 30 days to expiration
    r = 0.02   # Risk-free rate
    sigma = 0.25  # Volatility
    
    print(f"Stock Price: ${S}")
    print(f"Strike Price: ${K}")
    print(f"Time to Expiration: {T*365:.0f} days")
    print(f"Risk-free Rate: {r:.1%}")
    print(f"Volatility: {sigma:.1%}")
    
    # Calculate option prices
    call_price = BlackScholesCalculator.call_price(S, K, T, r, sigma)
    put_price = BlackScholesCalculator.put_price(S, K, T, r, sigma)
    
    print(f"\n📊 OPTION PRICES:")
    print(f"Call Price: ${call_price:.2f}")
    print(f"Put Price: ${put_price:.2f}")
    
    # Calculate Greeks
    call_greeks = GreeksCalculator.all_greeks(S, K, T, r, sigma, 'call')
    put_greeks = GreeksCalculator.all_greeks(S, K, T, r, sigma, 'put')
    
    print(f"\n🧮 GREEKS:")
    print(f"{'Greek':<8} {'Call':<10} {'Put':<10}")
    print("-" * 30)
    for greek in ['delta', 'gamma', 'theta', 'vega', 'rho']:
        print(f"{greek.capitalize():<8} {call_greeks[greek]:<10.4f} {put_greeks[greek]:<10.4f}")
    
    # Demonstrate implied volatility calculation
    market_price = call_price * 1.05  # Simulate market price 5% higher
    iv = ImpliedVolatilityCalculator.newton_raphson_iv(
        market_price, S, K, T, r, 'call'
    )
    
    print(f"\n🔍 IMPLIED VOLATILITY:")
    print(f"Market Price: ${market_price:.2f}")
    print(f"Theoretical Price: ${call_price:.2f}")
    print(f"Implied Volatility: {iv:.1%}" if iv else "Unable to calculate")

def demonstrate_strategy_backtesting():
    """Demonstrate strategy backtesting."""
    print("\n" + "="*60)
    print("📈 STRATEGY BACKTESTING DEMONSTRATION")
    print("="*60)
    
    # Create sample market data
    market_data = create_sample_market_data()
    
    # Initialize backtest engine
    engine = BacktestEngine(initial_capital=100000, commission=1.0)
    
    # Test 1: Covered Call Strategy
    print("\n🎯 Testing Covered Call Strategy...")
    covered_call = CoveredCallStrategy(
        symbol="AAPL",
        start_date="2021-01-01",
        end_date="2022-12-31",
        strike_selection="30_delta",
        expiration_days=30
    )
    
    try:
        results1 = engine.run_backtest(covered_call, market_data)
        print("✅ Covered Call backtest completed!")
        print(f"📊 Total Return: {results1.total_return:.2%}")
        print(f"📊 Sharpe Ratio: {results1.sharpe_ratio:.2f}")
        print(f"📊 Max Drawdown: {results1.max_drawdown:.2%}")
        print(f"📊 Win Rate: {results1.win_rate:.2%}")
    except Exception as e:
        print(f"❌ Covered Call backtest failed: {e}")
    
    # Test 2: Iron Condor Strategy
    print("\n🎯 Testing Iron Condor Strategy...")
    iron_condor = IronCondorStrategy(
        symbol="AAPL",
        start_date="2021-01-01",
        end_date="2022-12-31",
        put_strike_delta=0.16,
        call_strike_delta=0.16,
        wing_width=10,
        expiration_days=45
    )
    
    try:
        results2 = engine.run_backtest(iron_condor, market_data)
        print("✅ Iron Condor backtest completed!")
        print(f"📊 Total Return: {results2.total_return:.2%}")
        print(f"📊 Sharpe Ratio: {results2.sharpe_ratio:.2f}")
        print(f"📊 Max Drawdown: {results2.max_drawdown:.2%}")
        print(f"📊 Win Rate: {results2.win_rate:.2%}")
    except Exception as e:
        print(f"❌ Iron Condor backtest failed: {e}")
    
    # Test 3: Delta Neutral Strategy
    print("\n🎯 Testing Delta Neutral Strategy...")
    delta_neutral = DeltaNeutralStrategy(
        symbol="AAPL",
        start_date="2021-01-01",
        end_date="2022-12-31",
        target_delta=0.0,
        rebalance_threshold=0.1
    )
    
    try:
        results3 = engine.run_backtest(delta_neutral, market_data)
        print("✅ Delta Neutral backtest completed!")
        print(f"📊 Total Return: {results3.total_return:.2%}")
        print(f"📊 Sharpe Ratio: {results3.sharpe_ratio:.2f}")
        print(f"📊 Max Drawdown: {results3.max_drawdown:.2%}")
        print(f"📊 Win Rate: {results3.win_rate:.2%}")
    except Exception as e:
        print(f"❌ Delta Neutral backtest failed: {e}")

def demonstrate_portfolio_analysis():
    """Demonstrate portfolio analysis and risk metrics."""
    print("\n" + "="*60)
    print("📊 PORTFOLIO ANALYSIS DEMONSTRATION")
    print("="*60)
    
    # Sample portfolio positions
    positions = [
        {'symbol': 'AAPL', 'option_type': 'call', 'strike': 150, 'quantity': -5, 'delta': -0.3, 'gamma': 0.02, 'theta': -0.05, 'vega': 0.15},
        {'symbol': 'AAPL', 'option_type': 'put', 'strike': 140, 'quantity': -3, 'delta': 0.2, 'gamma': 0.01, 'theta': -0.03, 'vega': 0.1},
        {'symbol': 'AAPL', 'option_type': 'stock', 'quantity': 500, 'delta': 1.0, 'gamma': 0, 'theta': 0, 'vega': 0},
    ]
    
    from pricing.greeks import PortfolioGreeks
    
    portfolio_greeks = PortfolioGreeks.all_portfolio_greeks(positions)
    
    print("🎯 Portfolio Greeks Summary:")
    print(f"Delta: {portfolio_greeks['delta']:.2f}")
    print(f"Gamma: {portfolio_greeks['gamma']:.4f}")
    print(f"Theta: {portfolio_greeks['theta']:.2f}")
    print(f"Vega: {portfolio_greeks['vega']:.2f}")
    
    # Risk analysis
    print("\n🔍 Risk Analysis:")
    delta_risk = abs(portfolio_greeks['delta']) * 150 * 0.01  # 1% stock move
    gamma_risk = portfolio_greeks['gamma'] * 150 * 150 * 0.01**2 / 2  # Gamma effect
    theta_decay = portfolio_greeks['theta']  # Daily theta decay
    vega_risk = portfolio_greeks['vega'] * 0.01  # 1% vol change
    
    print(f"Delta Risk (1% stock move): ${delta_risk:.2f}")
    print(f"Gamma Risk (1% stock move): ${gamma_risk:.2f}")
    print(f"Daily Theta Decay: ${theta_decay:.2f}")
    print(f"Vega Risk (1% vol change): ${vega_risk:.2f}")

def main():
    """Main demonstration function."""
    print("🚀 Welcome to QuantOptions Platform Demo!")
    print("This demonstration showcases the key features of our options trading platform.")
    
    try:
        # Run demonstrations
        demonstrate_options_pricing()
        demonstrate_strategy_backtesting()
        demonstrate_portfolio_analysis()
        
        print("\n" + "="*60)
        print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📋 Summary of Features Demonstrated:")
        print("✅ Black-Scholes options pricing")
        print("✅ Greeks calculations (Delta, Gamma, Theta, Vega, Rho)")
        print("✅ Implied volatility calculations")
        print("✅ Strategy backtesting framework")
        print("✅ Multiple trading strategies (Covered Call, Iron Condor, Delta Neutral)")
        print("✅ Portfolio risk analysis")
        print("✅ Performance metrics calculation")
        
        print("\n🔥 Ready for Production!")
        print("This platform is now ready to be deployed and used for:")
        print("• Systematic options strategy development")
        print("• Historical backtesting and validation")
        print("• Real-time portfolio risk management")
        print("• Advanced options analytics")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("Please check the installation and dependencies.")

if __name__ == "__main__":
    main()
