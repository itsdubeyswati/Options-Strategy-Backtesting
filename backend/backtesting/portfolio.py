import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from pricing.black_scholes import BlackScholesCalculator
from pricing.greeks import GreeksCalculator

@dataclass
class Position:
    """Represents a single position in the portfolio."""
    symbol: str
    option_type: str  # 'call', 'put', 'stock'
    strike: Optional[float] = None
    expiration: Optional[datetime] = None
    quantity: int = 0
    entry_price: float = 0.0
    entry_date: datetime = None
    
@dataclass
class Trade:
    """Represents a completed trade."""
    symbol: str
    option_type: str
    strike: Optional[float]
    expiration: Optional[datetime]
    quantity: int
    entry_price: float
    exit_price: float
    entry_date: datetime
    exit_date: datetime
    pnl: float
    commission: float

class Portfolio:
    """Manages a portfolio of options and stock positions."""
    
    def __init__(self, initial_capital: float = 100000, commission: float = 1.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission = commission
        self.positions: List[Position] = []
        self.trades: List[Trade] = []
        self.equity_curve: List[Dict] = []
        
    def add_position(self, position: Position) -> None:
        """Add a new position to the portfolio."""
        # Check if position already exists
        existing_pos = self._find_position(
            position.symbol, position.option_type, 
            position.strike, position.expiration
        )
        
        if existing_pos:
            # Update existing position
            total_quantity = existing_pos.quantity + position.quantity
            if total_quantity == 0:
                self.positions.remove(existing_pos)
            else:
                # Weighted average entry price
                total_cost = (existing_pos.quantity * existing_pos.entry_price + 
                            position.quantity * position.entry_price)
                existing_pos.entry_price = total_cost / total_quantity
                existing_pos.quantity = total_quantity
        else:
            # Add new position
            self.positions.append(position)
        
        # Update cash
        cost = position.quantity * position.entry_price + self.commission
        self.cash -= cost
    
    def close_position(self, symbol: str, option_type: str, strike: Optional[float],
                      expiration: Optional[datetime], quantity: int, 
                      exit_price: float, exit_date: datetime) -> Optional[Trade]:
        """Close a position and record the trade."""
        position = self._find_position(symbol, option_type, strike, expiration)
        
        if not position or abs(quantity) > abs(position.quantity):
            return None
        
        # Calculate P&L
        if option_type == 'stock':
            pnl = quantity * (exit_price - position.entry_price)
        else:
            pnl = quantity * (exit_price - position.entry_price)
        
        # Account for commission
        pnl -= self.commission
        
        # Create trade record
        trade = Trade(
            symbol=symbol,
            option_type=option_type,
            strike=strike,
            expiration=expiration,
            quantity=quantity,
            entry_price=position.entry_price,
            exit_price=exit_price,
            entry_date=position.entry_date,
            exit_date=exit_date,
            pnl=pnl,
            commission=self.commission
        )
        
        self.trades.append(trade)
        
        # Update position
        position.quantity -= quantity
        if position.quantity == 0:
            self.positions.remove(position)
        
        # Update cash
        proceeds = quantity * exit_price - self.commission
        self.cash += proceeds
        
        return trade
    
    def _find_position(self, symbol: str, option_type: str, 
                      strike: Optional[float], expiration: Optional[datetime]) -> Optional[Position]:
        """Find an existing position."""
        for pos in self.positions:
            if (pos.symbol == symbol and pos.option_type == option_type and 
                pos.strike == strike and pos.expiration == expiration):
                return pos
        return None
    
    def get_portfolio_value(self, current_date: datetime, market_data: Dict,
                           risk_free_rate: float = 0.02) -> float:
        """Calculate current portfolio value."""
        total_value = self.cash
        
        for position in self.positions:
            if position.option_type == 'stock':
                # Stock position
                current_price = market_data.get(position.symbol, {}).get('price', 0)
                total_value += position.quantity * current_price
            else:
                # Options position
                stock_data = market_data.get(position.symbol, {})
                current_price = stock_data.get('price', 0)
                volatility = stock_data.get('volatility', 0.25)
                
                if current_price > 0 and position.expiration:
                    time_to_expiry = (position.expiration - current_date).days / 365.0
                    
                    if time_to_expiry > 0:
                        option_price = BlackScholesCalculator.option_price(
                            S=current_price,
                            K=position.strike,
                            T=time_to_expiry,
                            r=risk_free_rate,
                            sigma=volatility,
                            option_type=position.option_type
                        )
                    else:
                        # Option expired
                        if position.option_type == 'call':
                            option_price = max(current_price - position.strike, 0)
                        else:
                            option_price = max(position.strike - current_price, 0)
                    
                    total_value += position.quantity * option_price
        
        return total_value
    
    def get_portfolio_greeks(self, current_date: datetime, market_data: Dict,
                           risk_free_rate: float = 0.02) -> Dict[str, float]:
        """Calculate portfolio Greeks."""
        portfolio_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
        
        for position in self.positions:
            if position.option_type in ['call', 'put'] and position.expiration:
                stock_data = market_data.get(position.symbol, {})
                current_price = stock_data.get('price', 0)
                volatility = stock_data.get('volatility', 0.25)
                
                if current_price > 0:
                    time_to_expiry = (position.expiration - current_date).days / 365.0
                    
                    if time_to_expiry > 0:
                        greeks = GreeksCalculator.all_greeks(
                            S=current_price,
                            K=position.strike,
                            T=time_to_expiry,
                            r=risk_free_rate,
                            sigma=volatility,
                            option_type=position.option_type
                        )
                        
                        for greek, value in greeks.items():
                            portfolio_greeks[greek] += position.quantity * value
            elif position.option_type == 'stock':
                # Stock has delta of 1
                portfolio_greeks['delta'] += position.quantity
        
        return portfolio_greeks
    
    def update_equity_curve(self, date: datetime, portfolio_value: float) -> None:
        """Update the equity curve with current portfolio value."""
        self.equity_curve.append({
            'date': date,
            'portfolio_value': portfolio_value,
            'cash': self.cash,
            'positions_value': portfolio_value - self.cash
        })
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculate portfolio performance metrics."""
        if len(self.equity_curve) < 2:
            return {}
        
        # Convert to DataFrame for easier calculations
        df = pd.DataFrame(self.equity_curve)
        df['returns'] = df['portfolio_value'].pct_change().dropna()
        
        # Total return
        total_return = (df['portfolio_value'].iloc[-1] / self.initial_capital) - 1
        
        # Annual return (assuming daily data)
        days = len(df)
        annual_return = (1 + total_return) ** (252 / days) - 1
        
        # Volatility
        volatility = df['returns'].std() * math.sqrt(252)
        
        # Sharpe ratio (assuming risk-free rate of 2%)
        sharpe_ratio = (annual_return - 0.02) / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        df['cummax'] = df['portfolio_value'].cummax()
        df['drawdown'] = (df['portfolio_value'] - df['cummax']) / df['cummax']
        max_drawdown = df['drawdown'].min()
        
        # Win rate
        profitable_trades = len([t for t in self.trades if t.pnl > 0])
        total_trades = len(self.trades)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'profitable_trades': profitable_trades
        }
