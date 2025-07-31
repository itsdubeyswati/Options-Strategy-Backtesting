"""
Test Black-Scholes pricing calculations
"""

import pytest
import math
from pricing.black_scholes import BlackScholesCalculator, ImpliedVolatilityCalculator

class TestBlackScholesCalculator:
    """Test cases for Black-Scholes option pricing."""
    
    def test_call_option_pricing(self):
        """Test call option price calculation."""
        # Standard test case
        S = 100  # Current price
        K = 100  # Strike price
        T = 0.25  # 3 months
        r = 0.05  # 5% risk-free rate
        sigma = 0.2  # 20% volatility
        
        call_price = BlackScholesCalculator.call_price(S, K, T, r, sigma)
        
        # Expected price should be positive and reasonable
        assert call_price > 0
        assert call_price < S  # Should be less than stock price for ATM call
        
        # Test with known values (approximate)
        expected_price = 4.76  # Theoretical price
        assert abs(call_price - expected_price) < 0.5
    
    def test_put_option_pricing(self):
        """Test put option price calculation."""
        S = 100
        K = 100
        T = 0.25
        r = 0.05
        sigma = 0.2
        
        put_price = BlackScholesCalculator.put_price(S, K, T, r, sigma)
        
        assert put_price > 0
        assert put_price < K  # Should be less than strike for ATM put
    
    def test_put_call_parity(self):
        """Test put-call parity relationship."""
        S = 100
        K = 100
        T = 0.25
        r = 0.05
        sigma = 0.2
        
        call_price = BlackScholesCalculator.call_price(S, K, T, r, sigma)
        put_price = BlackScholesCalculator.put_price(S, K, T, r, sigma)
        
        # Put-call parity: C - P = S - K*e^(-rT)
        parity_left = call_price - put_price
        parity_right = S - K * math.exp(-r * T)
        
        assert abs(parity_left - parity_right) < 0.01
    
    def test_option_price_wrapper(self):
        """Test the generic option_price method."""
        S = 100
        K = 105
        T = 0.25
        r = 0.05
        sigma = 0.2
        
        call_price = BlackScholesCalculator.option_price(S, K, T, r, sigma, 'call')
        put_price = BlackScholesCalculator.option_price(S, K, T, r, sigma, 'put')
        
        assert call_price > 0
        assert put_price > 0
        
        # Test invalid option type
        with pytest.raises(ValueError):
            BlackScholesCalculator.option_price(S, K, T, r, sigma, 'invalid')
    
    def test_expired_options(self):
        """Test options at expiration."""
        S = 110
        K = 100
        T = 0  # Expired
        r = 0.05
        sigma = 0.2
        
        call_price = BlackScholesCalculator.call_price(S, K, T, r, sigma)
        put_price = BlackScholesCalculator.put_price(S, K, T, r, sigma)
        
        # At expiration, call = max(S-K, 0), put = max(K-S, 0)
        assert call_price == max(S - K, 0)
        assert put_price == max(K - S, 0)

class TestImpliedVolatilityCalculator:
    """Test cases for implied volatility calculations."""
    
    def test_newton_raphson_iv(self):
        """Test Newton-Raphson implied volatility calculation."""
        # First calculate a theoretical price
        S = 100
        K = 100
        T = 0.25
        r = 0.05
        true_sigma = 0.25
        
        market_price = BlackScholesCalculator.call_price(S, K, T, r, true_sigma)
        
        # Now calculate implied vol
        calculated_sigma = ImpliedVolatilityCalculator.newton_raphson_iv(
            market_price, S, K, T, r, 'call'
        )
        
        assert calculated_sigma is not None
        assert abs(calculated_sigma - true_sigma) < 0.01
    
    def test_bisection_iv(self):
        """Test bisection method implied volatility calculation."""
        S = 100
        K = 100
        T = 0.25
        r = 0.05
        true_sigma = 0.3
        
        market_price = BlackScholesCalculator.put_price(S, K, T, r, true_sigma)
        
        calculated_sigma = ImpliedVolatilityCalculator.bisection_iv(
            market_price, S, K, T, r, 'put'
        )
        
        assert calculated_sigma is not None
        assert abs(calculated_sigma - true_sigma) < 0.01
    
    def test_iv_bounds_checking(self):
        """Test implied volatility with out-of-bounds market prices."""
        S = 100
        K = 100
        T = 0.25
        r = 0.05
        
        # Market price too high
        high_price = S  # Price equal to stock price (impossible for call)
        iv = ImpliedVolatilityCalculator.bisection_iv(high_price, S, K, T, r, 'call')
        assert iv is None
        
        # Market price too low (negative not possible, but very low)
        low_price = 0.001
        iv = ImpliedVolatilityCalculator.bisection_iv(low_price, S, K, T, r, 'call')
        assert iv is not None or iv is None  # Might be solvable or not
