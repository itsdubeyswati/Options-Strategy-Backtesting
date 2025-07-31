import math
from scipy.stats import norm
from typing import Dict, Any

class GreeksCalculator:
    """Calculate option Greeks (Delta, Gamma, Theta, Vega, Rho)."""
    
    @staticmethod
    def _calculate_d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculate d1 parameter."""
        return (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    
    @staticmethod
    def _calculate_d2(d1: float, sigma: float, T: float) -> float:
        """Calculate d2 parameter."""
        return d1 - sigma * math.sqrt(T)
    
    @classmethod
    def delta(cls, S: float, K: float, T: float, r: float, sigma: float, 
              option_type: str) -> float:
        """
        Calculate option delta.
        
        Delta measures the rate of change of option price with respect to underlying price.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Delta value
        """
        if T <= 0:
            if option_type.lower() == 'call':
                return 1.0 if S > K else 0.0
            else:
                return -1.0 if S < K else 0.0
        
        d1 = cls._calculate_d1(S, K, T, r, sigma)
        
        if option_type.lower() == 'call':
            return norm.cdf(d1)
        elif option_type.lower() == 'put':
            return norm.cdf(d1) - 1
        else:
            raise ValueError("option_type must be 'call' or 'put'")
    
    @classmethod
    def gamma(cls, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Calculate option gamma.
        
        Gamma measures the rate of change of delta with respect to underlying price.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            
        Returns:
            Gamma value (same for calls and puts)
        """
        if T <= 0:
            return 0.0
        
        d1 = cls._calculate_d1(S, K, T, r, sigma)
        return norm.pdf(d1) / (S * sigma * math.sqrt(T))
    
    @classmethod
    def theta(cls, S: float, K: float, T: float, r: float, sigma: float,
              option_type: str) -> float:
        """
        Calculate option theta.
        
        Theta measures the rate of change of option price with respect to time.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Theta value (typically negative, representing time decay)
        """
        if T <= 0:
            return 0.0
        
        d1 = cls._calculate_d1(S, K, T, r, sigma)
        d2 = cls._calculate_d2(d1, sigma, T)
        
        term1 = -(S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
        
        if option_type.lower() == 'call':
            term2 = -r * K * math.exp(-r * T) * norm.cdf(d2)
            return term1 + term2
        elif option_type.lower() == 'put':
            term2 = r * K * math.exp(-r * T) * norm.cdf(-d2)
            return term1 + term2
        else:
            raise ValueError("option_type must be 'call' or 'put'")
    
    @classmethod
    def vega(cls, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        Calculate option vega.
        
        Vega measures the rate of change of option price with respect to volatility.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            
        Returns:
            Vega value (same for calls and puts)
        """
        if T <= 0:
            return 0.0
        
        d1 = cls._calculate_d1(S, K, T, r, sigma)
        return S * norm.pdf(d1) * math.sqrt(T)
    
    @classmethod
    def rho(cls, S: float, K: float, T: float, r: float, sigma: float,
            option_type: str) -> float:
        """
        Calculate option rho.
        
        Rho measures the rate of change of option price with respect to interest rate.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Rho value
        """
        if T <= 0:
            return 0.0
        
        d1 = cls._calculate_d1(S, K, T, r, sigma)
        d2 = cls._calculate_d2(d1, sigma, T)
        
        if option_type.lower() == 'call':
            return K * T * math.exp(-r * T) * norm.cdf(d2)
        elif option_type.lower() == 'put':
            return -K * T * math.exp(-r * T) * norm.cdf(-d2)
        else:
            raise ValueError("option_type must be 'call' or 'put'")
    
    @classmethod
    def all_greeks(cls, S: float, K: float, T: float, r: float, sigma: float,
                   option_type: str) -> Dict[str, float]:
        """
        Calculate all Greeks for an option.
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (in years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Dictionary containing all Greeks
        """
        return {
            'delta': cls.delta(S, K, T, r, sigma, option_type),
            'gamma': cls.gamma(S, K, T, r, sigma),
            'theta': cls.theta(S, K, T, r, sigma, option_type),
            'vega': cls.vega(S, K, T, r, sigma),
            'rho': cls.rho(S, K, T, r, sigma, option_type)
        }

class PortfolioGreeks:
    """Calculate portfolio-level Greeks."""
    
    @staticmethod
    def portfolio_delta(positions: list) -> float:
        """
        Calculate portfolio delta.
        
        Args:
            positions: List of position dictionaries with 'quantity', 'delta'
            
        Returns:
            Portfolio delta
        """
        return sum(pos['quantity'] * pos['delta'] for pos in positions)
    
    @staticmethod
    def portfolio_gamma(positions: list) -> float:
        """
        Calculate portfolio gamma.
        
        Args:
            positions: List of position dictionaries with 'quantity', 'gamma'
            
        Returns:
            Portfolio gamma
        """
        return sum(pos['quantity'] * pos['gamma'] for pos in positions)
    
    @staticmethod
    def portfolio_theta(positions: list) -> float:
        """
        Calculate portfolio theta.
        
        Args:
            positions: List of position dictionaries with 'quantity', 'theta'
            
        Returns:
            Portfolio theta
        """
        return sum(pos['quantity'] * pos['theta'] for pos in positions)
    
    @staticmethod
    def portfolio_vega(positions: list) -> float:
        """
        Calculate portfolio vega.
        
        Args:
            positions: List of position dictionaries with 'quantity', 'vega'
            
        Returns:
            Portfolio vega
        """
        return sum(pos['quantity'] * pos['vega'] for pos in positions)
    
    @staticmethod
    def all_portfolio_greeks(positions: list) -> Dict[str, float]:
        """
        Calculate all portfolio Greeks.
        
        Args:
            positions: List of position dictionaries with Greeks
            
        Returns:
            Dictionary containing all portfolio Greeks
        """
        return {
            'delta': PortfolioGreeks.portfolio_delta(positions),
            'gamma': PortfolioGreeks.portfolio_gamma(positions),
            'theta': PortfolioGreeks.portfolio_theta(positions),
            'vega': PortfolioGreeks.portfolio_vega(positions)
        }
