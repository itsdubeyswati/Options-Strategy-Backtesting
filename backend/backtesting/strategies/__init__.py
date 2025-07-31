from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from ..portfolio import Portfolio, Position

class TradingStrategy(ABC):
    """Abstract base class for all trading strategies."""
    
    def __init__(self, symbol: str, start_date: str, end_date: str):
        self.symbol = symbol
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.name = self.__class__.__name__
    
    @abstractmethod
    def generate_signals(self, market_data: pd.DataFrame) -> List[Dict]:
        """Generate trading signals based on market data."""
        pass
    
    @abstractmethod
    def execute_trades(self, portfolio: Portfolio, signals: List[Dict], 
                      current_date: datetime, market_data: Dict) -> None:
        """Execute trades based on signals."""
        pass

class CoveredCallStrategy(TradingStrategy):
    """Covered Call Strategy: Own stock and sell call options."""
    
    def __init__(self, symbol: str, start_date: str, end_date: str,
                 strike_selection: str = "30_delta", expiration_days: int = 30,
                 profit_target: float = 0.5, max_loss: float = -0.2):
        super().__init__(symbol, start_date, end_date)
        self.strike_selection = strike_selection  # "30_delta", "5_percent_otm", etc.
        self.expiration_days = expiration_days
        self.profit_target = profit_target
        self.max_loss = max_loss
        self.position_size = 100  # 100 shares per covered call
    
    def generate_signals(self, market_data: pd.DataFrame) -> List[Dict]:
        """Generate covered call signals."""
        signals = []
        
        # Initial position: buy stock
        if not market_data.empty:
            first_date = market_data.index[0]
            signals.append({
                'date': first_date,
                'action': 'buy_stock',
                'symbol': self.symbol,
                'quantity': self.position_size,
                'price': market_data.loc[first_date, 'close']
            })
        
        # Generate call selling signals monthly
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date in market_data.index:
                signals.append({
                    'date': current_date,
                    'action': 'sell_call',
                    'symbol': self.symbol,
                    'expiration_days': self.expiration_days
                })
            
            # Move to next month
            current_date += timedelta(days=30)
        
        return signals
    
    def execute_trades(self, portfolio: Portfolio, signals: List[Dict], 
                      current_date: datetime, market_data: Dict) -> None:
        """Execute covered call trades."""
        for signal in signals:
            if signal['date'].date() == current_date.date():
                if signal['action'] == 'buy_stock':
                    self._buy_stock(portfolio, signal, market_data)
                elif signal['action'] == 'sell_call':
                    self._sell_call(portfolio, signal, current_date, market_data)
    
    def _buy_stock(self, portfolio: Portfolio, signal: Dict, market_data: Dict) -> None:
        """Buy stock position."""
        current_price = market_data.get(self.symbol, {}).get('price', signal['price'])
        
        position = Position(
            symbol=self.symbol,
            option_type='stock',
            quantity=signal['quantity'],
            entry_price=current_price,
            entry_date=signal['date']
        )
        
        portfolio.add_position(position)
    
    def _sell_call(self, portfolio: Portfolio, signal: Dict, 
                   current_date: datetime, market_data: Dict) -> None:
        """Sell call option."""
        stock_data = market_data.get(self.symbol, {})
        current_price = stock_data.get('price', 0)
        volatility = stock_data.get('volatility', 0.25)
        
        if current_price <= 0:
            return
        
        # Calculate strike price based on selection method
        strike_price = self._calculate_strike_price(current_price, volatility)
        expiration_date = current_date + timedelta(days=signal['expiration_days'])
        
        # Calculate option price
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from pricing.black_scholes import BlackScholesCalculator
        time_to_expiry = signal['expiration_days'] / 365.0
        option_price = BlackScholesCalculator.call_price(
            S=current_price,
            K=strike_price,
            T=time_to_expiry,
            r=0.02,
            sigma=volatility
        )
        
        position = Position(
            symbol=self.symbol,
            option_type='call',
            strike=strike_price,
            expiration=expiration_date,
            quantity=-1,  # Short position
            entry_price=option_price,
            entry_date=current_date
        )
        
        portfolio.add_position(position)
    
    def _calculate_strike_price(self, current_price: float, volatility: float) -> float:
        """Calculate strike price based on selection method."""
        if self.strike_selection == "30_delta":
            # Approximate 30-delta strike (simplified)
            return current_price * 1.05
        elif self.strike_selection == "5_percent_otm":
            return current_price * 1.05
        elif self.strike_selection == "10_percent_otm":
            return current_price * 1.10
        else:
            return current_price * 1.05  # Default

class IronCondorStrategy(TradingStrategy):
    """Iron Condor Strategy: Sell put spread and call spread."""
    
    def __init__(self, symbol: str, start_date: str, end_date: str,
                 put_strike_delta: float = 0.16, call_strike_delta: float = 0.16,
                 wing_width: float = 10, expiration_days: int = 45,
                 profit_target: float = 0.5, stop_loss: float = 2.0):
        super().__init__(symbol, start_date, end_date)
        self.put_strike_delta = put_strike_delta
        self.call_strike_delta = call_strike_delta
        self.wing_width = wing_width
        self.expiration_days = expiration_days
        self.profit_target = profit_target
        self.stop_loss = stop_loss
    
    def generate_signals(self, market_data: pd.DataFrame) -> List[Dict]:
        """Generate iron condor signals."""
        signals = []
        
        # Generate signals monthly
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date in market_data.index:
                signals.append({
                    'date': current_date,
                    'action': 'open_iron_condor',
                    'symbol': self.symbol,
                    'expiration_days': self.expiration_days
                })
            
            # Move to next month
            current_date += timedelta(days=45)
        
        return signals
    
    def execute_trades(self, portfolio: Portfolio, signals: List[Dict], 
                      current_date: datetime, market_data: Dict) -> None:
        """Execute iron condor trades."""
        for signal in signals:
            if signal['date'].date() == current_date.date():
                if signal['action'] == 'open_iron_condor':
                    self._open_iron_condor(portfolio, signal, current_date, market_data)
    
    def _open_iron_condor(self, portfolio: Portfolio, signal: Dict,
                         current_date: datetime, market_data: Dict) -> None:
        """Open iron condor position."""
        stock_data = market_data.get(self.symbol, {})
        current_price = stock_data.get('price', 0)
        volatility = stock_data.get('volatility', 0.25)
        
        if current_price <= 0:
            return
        
        expiration_date = current_date + timedelta(days=signal['expiration_days'])
        time_to_expiry = signal['expiration_days'] / 365.0
        
        # Calculate strike prices (simplified delta approximation)
        put_strike_short = current_price * 0.95  # Short put
        put_strike_long = put_strike_short - self.wing_width  # Long put
        call_strike_short = current_price * 1.05  # Short call
        call_strike_long = call_strike_short + self.wing_width  # Long call
        
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from pricing.black_scholes import BlackScholesCalculator
        
        # Calculate option prices
        put_short_price = BlackScholesCalculator.put_price(
            current_price, put_strike_short, time_to_expiry, 0.02, volatility)
        put_long_price = BlackScholesCalculator.put_price(
            current_price, put_strike_long, time_to_expiry, 0.02, volatility)
        call_short_price = BlackScholesCalculator.call_price(
            current_price, call_strike_short, time_to_expiry, 0.02, volatility)
        call_long_price = BlackScholesCalculator.call_price(
            current_price, call_strike_long, time_to_expiry, 0.02, volatility)
        
        # Create positions
        positions = [
            Position(self.symbol, 'put', put_strike_short, expiration_date, 
                    -1, put_short_price, current_date),  # Sell put
            Position(self.symbol, 'put', put_strike_long, expiration_date, 
                    1, put_long_price, current_date),   # Buy put
            Position(self.symbol, 'call', call_strike_short, expiration_date, 
                    -1, call_short_price, current_date), # Sell call
            Position(self.symbol, 'call', call_strike_long, expiration_date, 
                    1, call_long_price, current_date)   # Buy call
        ]
        
        for position in positions:
            portfolio.add_position(position)

class DeltaNeutralStrategy(TradingStrategy):
    """Delta Neutral Strategy: Maintain delta-neutral portfolio."""
    
    def __init__(self, symbol: str, start_date: str, end_date: str,
                 target_delta: float = 0.0, rebalance_threshold: float = 0.1,
                 strategy_type: str = "short_straddle"):
        super().__init__(symbol, start_date, end_date)
        self.target_delta = target_delta
        self.rebalance_threshold = rebalance_threshold
        self.strategy_type = strategy_type
    
    def generate_signals(self, market_data: pd.DataFrame) -> List[Dict]:
        """Generate delta neutral signals."""
        signals = []
        
        # Initial position
        if not market_data.empty:
            first_date = market_data.index[0]
            signals.append({
                'date': first_date,
                'action': f'open_{self.strategy_type}',
                'symbol': self.symbol
            })
        
        # Daily rebalancing checks
        for date in market_data.index[1:]:
            signals.append({
                'date': date,
                'action': 'check_rebalance',
                'symbol': self.symbol
            })
        
        return signals
    
    def execute_trades(self, portfolio: Portfolio, signals: List[Dict], 
                      current_date: datetime, market_data: Dict) -> None:
        """Execute delta neutral trades."""
        for signal in signals:
            if signal['date'].date() == current_date.date():
                if signal['action'] == 'open_short_straddle':
                    self._open_short_straddle(portfolio, current_date, market_data)
                elif signal['action'] == 'check_rebalance':
                    self._check_rebalance(portfolio, current_date, market_data)
    
    def _open_short_straddle(self, portfolio: Portfolio, current_date: datetime,
                           market_data: Dict) -> None:
        """Open short straddle position."""
        stock_data = market_data.get(self.symbol, {})
        current_price = stock_data.get('price', 0)
        volatility = stock_data.get('volatility', 0.25)
        
        if current_price <= 0:
            return
        
        expiration_date = current_date + timedelta(days=30)
        time_to_expiry = 30 / 365.0
        
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from pricing.black_scholes import BlackScholesCalculator
        
        # ATM straddle
        strike = current_price
        call_price = BlackScholesCalculator.call_price(
            current_price, strike, time_to_expiry, 0.02, volatility)
        put_price = BlackScholesCalculator.put_price(
            current_price, strike, time_to_expiry, 0.02, volatility)
        
        # Short straddle positions
        positions = [
            Position(self.symbol, 'call', strike, expiration_date, 
                    -1, call_price, current_date),
            Position(self.symbol, 'put', strike, expiration_date, 
                    -1, put_price, current_date)
        ]
        
        for position in positions:
            portfolio.add_position(position)
    
    def _check_rebalance(self, portfolio: Portfolio, current_date: datetime,
                        market_data: Dict) -> None:
        """Check if portfolio needs rebalancing."""
        portfolio_greeks = portfolio.get_portfolio_greeks(current_date, market_data)
        current_delta = portfolio_greeks.get('delta', 0)
        
        if abs(current_delta - self.target_delta) > self.rebalance_threshold:
            self._rebalance_delta(portfolio, current_delta, current_date, market_data)
    
    def _rebalance_delta(self, portfolio: Portfolio, current_delta: float,
                        current_date: datetime, market_data: Dict) -> None:
        """Rebalance portfolio to target delta."""
        delta_adjustment = self.target_delta - current_delta
        stock_price = market_data.get(self.symbol, {}).get('price', 0)
        
        if stock_price > 0:
            # Buy/sell stock to adjust delta
            shares_needed = int(delta_adjustment)
            if shares_needed != 0:
                position = Position(
                    symbol=self.symbol,
                    option_type='stock',
                    quantity=shares_needed,
                    entry_price=stock_price,
                    entry_date=current_date
                )
                portfolio.add_position(position)
