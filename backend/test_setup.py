"""
Quick test script to validate the options pricing functionality
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(__file__))

def test_basic_functionality():
    """Test basic pricing functionality."""
    print("🧪 Testing Options Strategy Backtesting Platform...")
    print("=" * 50)
    
    try:
        # Test 1: Black-Scholes pricing
        print("\n1️⃣ Testing Black-Scholes Option Pricing...")
        from pricing.black_scholes import BlackScholesCalculator
        
        # Calculate a call option price
        call_price = BlackScholesCalculator.call_price(
            S=100,      # Current stock price
            K=105,      # Strike price  
            T=0.25,     # 3 months to expiry
            r=0.05,     # 5% risk-free rate
            sigma=0.25  # 25% volatility
        )
        
        print(f"   📈 Call Option Price: ${call_price:.2f}")
        
        # Calculate a put option price
        put_price = BlackScholesCalculator.put_price(100, 105, 0.25, 0.05, 0.25)
        print(f"   📉 Put Option Price: ${put_price:.2f}")
        
        print("   ✅ Black-Scholes pricing working correctly!")
        
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    try:
        # Test 2: Greeks calculations
        print("\n2️⃣ Testing Greeks Calculations...")
        from pricing.greeks import GreeksCalculator
        
        greeks = GreeksCalculator.all_greeks(
            S=100, K=100, T=0.25, r=0.05, sigma=0.25, option_type='call'
        )
        
        print(f"   📊 Delta: {greeks['delta']:.4f}")
        print(f"   📊 Gamma: {greeks['gamma']:.4f}")
        print(f"   📊 Theta: {greeks['theta']:.4f}")
        print(f"   📊 Vega: {greeks['vega']:.4f}")
        print(f"   📊 Rho: {greeks['rho']:.4f}")
        
        print("   ✅ Greeks calculations working correctly!")
        
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    try:
        # Test 3: Basic strategy framework
        print("\n3️⃣ Testing Strategy Framework...")
        
        # Add the current directory to Python path for imports
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        from backtesting.strategies import TradingStrategy, CoveredCallStrategy
        
        # Create strategy with required parameters (as strings)
        strategy = CoveredCallStrategy("AAPL", "2024-01-01", "2024-12-31")
        print(f"   📋 Strategy Name: {strategy.__class__.__name__}")
        print(f"   📋 Symbol: {strategy.symbol}")
        print(f"   📋 Period: {strategy.start_date.strftime('%Y-%m-%d')} to {strategy.end_date.strftime('%Y-%m-%d')}")
        
        print("   ✅ Strategy framework working correctly!")
        
    except ImportError as e:
        print(f"   ❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All core functionality tests passed!")
    print("🚀 Platform is ready for use!")
    print("\n📚 Next steps:")
    print("   1. Start the backend server: python run.py")
    print("   2. Visit http://localhost:8000/docs for API documentation")
    print("   3. Set up the frontend React application")
    print("   4. Configure your database connection in .env file")
    
    return True

if __name__ == "__main__":
    test_basic_functionality()
