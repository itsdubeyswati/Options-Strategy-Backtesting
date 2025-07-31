import numpy as np
from scipy.stats import norm
from typing import Optional
import math

class BlackScholesCalculator:
    """Black-Scholes options pricing calculator."""
    
    @staticmethod
    def calculate_d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate d1 parameter for Black-Scholes formula."""
        return (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    
    @staticmethod
    def calculate_d2(d1: float, sigma: float, T: float) -> float:
        """Calculate d2 parameter for Black-Scholes formula."""
        return d1 - sigma * math.sqrt(T)
    
    @classmethod
    def call_price(cls, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Calculate European call option price using Black-Scholes formula.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            
        Returns:
            Call option price
        """
        if T <= 0:
            return max(S - K, 0)
        
        d1 = cls.calculate_d1(S, K, T, r, sigma)
        d2 = cls.calculate_d2(d1, sigma, T)
        
        call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        return max(call_price, 0)
    
    @classmethod
    def put_price(cls, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Calculate European put option price using Black-Scholes formula.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            
        Returns:
            Put option price
        """
        if T <= 0:
            return max(K - S, 0)
        
        d1 = cls.calculate_d1(S, K, T, r, sigma)
        d2 = cls.calculate_d2(d1, sigma, T)
        
        put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return max(put_price, 0)
    
    @classmethod
    def option_price(cls, S: float, K: float, T: float, r: float, sigma: float, 
                    option_type: str) -> float:
        """
        Calculate option price for either call or put.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Option price
        """
        if option_type.lower() == 'call':
            return cls.call_price(S, K, T, r, sigma)
        elif option_type.lower() == 'put':
            return cls.put_price(S, K, T, r, sigma)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

class ImpliedVolatilityCalculator:
    """Calculate implied volatility using numerical methods."""
    
    @staticmethod
    def newton_raphson_iv(market_price: float, S: float, K: float, T: float, 
                         r: float, option_type: str, max_iterations: int = 100,
                         tolerance: float = 1e-6) -> Optional[float]:
        """
        Calculate implied volatility using Newton-Raphson method.
        
        Args:
            market_price: Observed market price of the option
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            option_type: 'call' or 'put'
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            
        Returns:
            Implied volatility or None if convergence fails
        """
        from .greeks import GreeksCalculator
        
        # Initial guess
        sigma = 0.25
        
        for i in range(max_iterations):
            # Calculate option price and vega
            calculated_price = BlackScholesCalculator.option_price(
                S, K, T, r, sigma, option_type
            )
            vega = GreeksCalculator.vega(S, K, T, r, sigma)
            
            # Check for convergence
            price_diff = calculated_price - market_price
            if abs(price_diff) < tolerance:
                return sigma
            
            # Newton-Raphson update
            if vega == 0:
                return None
            
            sigma_new = sigma - price_diff / vega
            
            # Ensure sigma stays positive
            if sigma_new <= 0:
                sigma = sigma / 2
            else:
                sigma = sigma_new
        
        return None  # Failed to converge
    
    @staticmethod
    def bisection_iv(market_price: float, S: float, K: float, T: float, 
                    r: float, option_type: str, vol_min: float = 0.001,
                    vol_max: float = 5.0, max_iterations: int = 100,
                    tolerance: float = 1e-6) -> Optional[float]:
        """
        Calculate implied volatility using bisection method.
        
        Args:
            market_price: Observed market price of the option
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            option_type: 'call' or 'put'
            vol_min: Minimum volatility bound
            vol_max: Maximum volatility bound
            max_iterations: Maximum number of iterations
            tolerance: Convergence tolerance
            
        Returns:
            Implied volatility or None if no solution found
        """
        # Check bounds
        price_min = BlackScholesCalculator.option_price(S, K, T, r, vol_min, option_type)
        price_max = BlackScholesCalculator.option_price(S, K, T, r, vol_max, option_type)
        
        if market_price < price_min or market_price > price_max:
            return None
        
        # Bisection method
        for i in range(max_iterations):
            vol_mid = (vol_min + vol_max) / 2
            price_mid = BlackScholesCalculator.option_price(S, K, T, r, vol_mid, option_type)
            
            if abs(price_mid - market_price) < tolerance:
                return vol_mid
            
            if price_mid < market_price:
                vol_min = vol_mid
            else:
                vol_max = vol_mid
        
        return (vol_min + vol_max) / 2  # Return best estimate
