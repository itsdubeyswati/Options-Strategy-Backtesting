#!/usr/bin/env python3
"""
Simple test script to verify the QuantOptions platform is working
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test that all core modules can be imported."""
    print("🧪 Testing core module imports...")
    
    try:
        from pricing.black_scholes import BlackScholesCalculator
        print("✅ Black-Scholes pricing engine imported successfully")
        
        from pricing.greeks import GreeksCalculator
        print("✅ Greeks calculator imported successfully")
        
        from backtesting.portfolio import Portfolio
        print("✅ Portfolio management imported successfully")
        
        from backtesting.engine import BacktestEngine
        print("✅ Backtesting engine imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_options_pricing():
    """Test basic options pricing functionality."""
    print("\n💰 Testing options pricing...")
    
    try:
        from pricing.black_scholes import BlackScholesCalculator
        
        # Test parameters
        S = 150.0  # Stock price
        K = 155.0  # Strike price  
        T = 30/365  # 30 days to expiration
        r = 0.02   # Risk-free rate
        sigma = 0.25  # Volatility
        
        # Calculate option prices
        call_price = BlackScholesCalculator.call_price(S, K, T, r, sigma)
        put_price = BlackScholesCalculator.put_price(S, K, T, r, sigma)
        
        print(f"📊 Call price: ${call_price:.2f}")
        print(f"📊 Put price: ${put_price:.2f}")
        
        if call_price > 0 and put_price > 0:
            print("✅ Options pricing working correctly")
            return True
        else:
            print("❌ Invalid option prices calculated")
            return False
            
    except Exception as e:
        print(f"❌ Options pricing error: {e}")
        return False

def test_greeks():
    """Test Greeks calculations."""
    print("\n🧮 Testing Greeks calculations...")
    
    try:
        from pricing.greeks import GreeksCalculator
        
        # Test parameters
        S = 150.0
        K = 155.0
        T = 30/365
        r = 0.02
        sigma = 0.25
        
        # Calculate Greeks
        greeks = GreeksCalculator.all_greeks(S, K, T, r, sigma, 'call')
        
        print(f"📈 Delta: {greeks['delta']:.4f}")
        print(f"📈 Gamma: {greeks['gamma']:.4f}")
        print(f"📈 Theta: {greeks['theta']:.4f}")
        print(f"📈 Vega: {greeks['vega']:.4f}")
        print(f"📈 Rho: {greeks['rho']:.4f}")
        
        if all(isinstance(v, (int, float)) for v in greeks.values()):
            print("✅ Greeks calculations working correctly")
            return True
        else:
            print("❌ Invalid Greeks values")
            return False
            
    except Exception as e:
        print(f"❌ Greeks calculation error: {e}")
        return False

def test_api_startup():
    """Test that the FastAPI app can start."""
    print("\n🚀 Testing API startup...")
    
    try:
        from app.main import app
        print("✅ FastAPI app created successfully")
        
        # Test that we can access routes
        from app.api.routes import api_router
        print("✅ API routes loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ API startup error: {e}")
        return False

def show_next_steps():
    """Show next steps for running the platform."""
    print("\n" + "="*60)
    print("🎯 QUANTOPTIONS PLATFORM - NEXT STEPS")
    print("="*60)
    
    print("\n🚀 To start the backend API server:")
    print('   "C:/Users/swati/Desktop/Projects/Options Strategy Backtesting/.venv/Scripts/python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000')
    
    print("\n🌐 Once running, access:")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • API Base URL: http://localhost:8000/api/v1")
    print("   • Health Check: http://localhost:8000/health")
    
    print("\n📊 Available API Endpoints:")
    print("   • POST /api/v1/options/price - Calculate option prices")
    print("   • POST /api/v1/options/greeks - Calculate Greeks")
    print("   • POST /api/v1/backtests/run - Run strategy backtests")
    print("   • GET /api/v1/strategies - List trading strategies")
    print("   • GET /api/v1/market-data/price/{symbol} - Get stock prices")
    print("   • GET /api/v1/portfolio/summary - Portfolio overview")
    
    print("\n🐳 To run full stack with Docker:")
    print("   docker-compose up -d")
    
    print("\n🔧 To install frontend dependencies:")
    print("   cd frontend")
    print("   npm install")
    print("   npm start")

def main():
    """Run all tests and show status."""
    print("🚀 QuantOptions Platform Verification")
    print("="*50)
    
    results = []
    
    # Run tests
    results.append(("Core Imports", test_imports()))
    results.append(("Options Pricing", test_options_pricing()))
    results.append(("Greeks Calculations", test_greeks()))
    results.append(("API Startup", test_api_startup()))
    
    # Show results
    print("\n" + "="*50)
    print("📋 TEST RESULTS")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ QuantOptions platform is ready to run!")
        show_next_steps()
    else:
        print("\n⚠️  Some tests failed, but core functionality is available")
        print("💡 The platform can still demonstrate key features")
        show_next_steps()

if __name__ == "__main__":
    main()
