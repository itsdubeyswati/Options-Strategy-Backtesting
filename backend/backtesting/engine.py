import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import structlog

from .portfolio import Portfolio
from .strategies import TradingStrategy

logger = structlog.get_logger()

class BacktestEngine:
    """Main backtesting engine that runs trading strategies."""
    
    def __init__(self, initial_capital: float = 100000, commission: float = 1.0):
        self.initial_capital = initial_capital
        self.commission = commission
        self.results = None
    
    def run_backtest(self, strategy: TradingStrategy, market_data: Dict[str, pd.DataFrame],
                    risk_free_rate: float = 0.02) -> 'BacktestResults':
        """
        Run a complete backtest for a given strategy.
        
        Args:
            strategy: Trading strategy to test
            market_data: Dictionary with symbol -> DataFrame of OHLCV data
            risk_free_rate: Risk-free rate for option pricing
            
        Returns:
            BacktestResults object with performance metrics
        """
        logger.info(f"Starting backtest for {strategy.name}", 
                   symbol=strategy.symbol, 
                   start_date=strategy.start_date.strftime("%Y-%m-%d"),
                   end_date=strategy.end_date.strftime("%Y-%m-%d"))
        
        # Initialize portfolio
        portfolio = Portfolio(initial_capital=self.initial_capital, 
                            commission=self.commission)
        
        # Get market data for the strategy symbol
        symbol_data = market_data.get(strategy.symbol)
        if symbol_data is None:
            raise ValueError(f"No market data found for symbol {strategy.symbol}")
        
        # Filter data by strategy date range
        symbol_data = symbol_data[
            (symbol_data.index >= strategy.start_date) & 
            (symbol_data.index <= strategy.end_date)
        ]
        
        # Generate trading signals
        signals = strategy.generate_signals(symbol_data)
        logger.info(f"Generated {len(signals)} trading signals")
        
        # Run day-by-day simulation
        current_date = strategy.start_date
        while current_date <= strategy.end_date:
            # Skip weekends (assuming daily data)
            if current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Get market data for current date
            daily_market_data = self._get_daily_market_data(
                current_date, market_data, risk_free_rate
            )
            
            # Execute trades for current date
            strategy.execute_trades(portfolio, signals, current_date, daily_market_data)
            
            # Handle option expirations
            self._handle_expirations(portfolio, current_date, daily_market_data)
            
            # Calculate portfolio value
            portfolio_value = portfolio.get_portfolio_value(
                current_date, daily_market_data, risk_free_rate
            )
            
            # Update equity curve
            portfolio.update_equity_curve(current_date, portfolio_value)
            
            current_date += timedelta(days=1)
        
        # Create results
        self.results = BacktestResults(portfolio, strategy)
        
        logger.info("Backtest completed", 
                   total_trades=len(portfolio.trades),
                   final_value=portfolio.equity_curve[-1]['portfolio_value'] if portfolio.equity_curve else 0)
        
        return self.results
    
    def _get_daily_market_data(self, date: datetime, market_data: Dict[str, pd.DataFrame],
                              risk_free_rate: float) -> Dict[str, Dict]:
        """Get market data for a specific date."""
        daily_data = {}
        
        for symbol, data in market_data.items():
            if date in data.index:
                row = data.loc[date]
                daily_data[symbol] = {
                    'price': row['close'],
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'volume': row['volume'],
                    'volatility': self._calculate_volatility(data, date)
                }
        
        return daily_data
    
    def _calculate_volatility(self, data: pd.DataFrame, date: datetime, 
                            window: int = 30) -> float:
        """Calculate historical volatility."""
        try:
            # Get data up to current date
            hist_data = data[data.index <= date].tail(window)
            
            if len(hist_data) < 2:
                return 0.25  # Default volatility
            
            # Calculate daily returns
            returns = hist_data['close'].pct_change().dropna()
            
            if len(returns) < 2:
                return 0.25
            
            # Annualized volatility
            volatility = returns.std() * np.sqrt(252)
            return max(volatility, 0.05)  # Minimum 5% volatility
            
        except Exception:
            return 0.25  # Default fallback
    
    def _handle_expirations(self, portfolio: Portfolio, current_date: datetime,
                           market_data: Dict[str, Dict]) -> None:
        """Handle option expirations."""
        expired_positions = []
        
        for position in portfolio.positions:
            if (position.option_type in ['call', 'put'] and 
                position.expiration and 
                position.expiration.date() <= current_date.date()):
                expired_positions.append(position)
        
        # Process expired options
        for position in expired_positions:
            stock_data = market_data.get(position.symbol, {})
            current_price = stock_data.get('price', 0)
            
            if current_price > 0:
                # Calculate intrinsic value
                if position.option_type == 'call':
                    intrinsic_value = max(current_price - position.strike, 0)
                else:  # put
                    intrinsic_value = max(position.strike - current_price, 0)
                
                # Close the position at intrinsic value
                portfolio.close_position(
                    symbol=position.symbol,
                    option_type=position.option_type,
                    strike=position.strike,
                    expiration=position.expiration,
                    quantity=-position.quantity,  # Close entire position
                    exit_price=intrinsic_value,
                    exit_date=current_date
                )

class BacktestResults:
    """Contains the results of a backtest."""
    
    def __init__(self, portfolio: Portfolio, strategy: TradingStrategy):
        self.portfolio = portfolio
        self.strategy = strategy
        self.performance_metrics = portfolio.get_performance_metrics()
        self.equity_curve = pd.DataFrame(portfolio.equity_curve)
        self.trades = portfolio.trades
        
        # Calculate additional metrics
        self._calculate_additional_metrics()
    
    def _calculate_additional_metrics(self) -> None:
        """Calculate additional performance metrics."""
        if not self.trades:
            return
        
        # Trade-level metrics
        pnls = [trade.pnl for trade in self.trades]
        
        self.avg_trade_pnl = np.mean(pnls)
        self.best_trade = max(pnls) if pnls else 0
        self.worst_trade = min(pnls) if pnls else 0
        
        # Consecutive wins/losses
        win_streak = 0
        loss_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for pnl in pnls:
            if pnl > 0:
                win_streak += 1
                loss_streak = 0
                max_win_streak = max(max_win_streak, win_streak)
            else:
                loss_streak += 1
                win_streak = 0
                max_loss_streak = max(max_loss_streak, loss_streak)
        
        self.max_consecutive_wins = max_win_streak
        self.max_consecutive_losses = max_loss_streak
    
    @property
    def total_return(self) -> float:
        """Total return percentage."""
        return self.performance_metrics.get('total_return', 0)
    
    @property
    def annual_return(self) -> float:
        """Annualized return percentage."""
        return self.performance_metrics.get('annual_return', 0)
    
    @property
    def sharpe_ratio(self) -> float:
        """Sharpe ratio."""
        return self.performance_metrics.get('sharpe_ratio', 0)
    
    @property
    def max_drawdown(self) -> float:
        """Maximum drawdown percentage."""
        return self.performance_metrics.get('max_drawdown', 0)
    
    @property
    def win_rate(self) -> float:
        """Win rate percentage."""
        return self.performance_metrics.get('win_rate', 0)
    
    def summary(self) -> Dict[str, Any]:
        """Get a summary of all results."""
        return {
            'strategy': self.strategy.name,
            'symbol': self.strategy.symbol,
            'period': f"{self.strategy.start_date.strftime('%Y-%m-%d')} to {self.strategy.end_date.strftime('%Y-%m-%d')}",
            'total_return': f"{self.total_return:.2%}",
            'annual_return': f"{self.annual_return:.2%}",
            'sharpe_ratio': f"{self.sharpe_ratio:.2f}",
            'max_drawdown': f"{self.max_drawdown:.2%}",
            'win_rate': f"{self.win_rate:.2%}",
            'total_trades': len(self.trades),
            'avg_trade_pnl': f"${getattr(self, 'avg_trade_pnl', 0):.2f}",
            'best_trade': f"${getattr(self, 'best_trade', 0):.2f}",
            'worst_trade': f"${getattr(self, 'worst_trade', 0):.2f}",
            'max_consecutive_wins': getattr(self, 'max_consecutive_wins', 0),
            'max_consecutive_losses': getattr(self, 'max_consecutive_losses', 0)
        }
    
    def print_summary(self) -> None:
        """Print a formatted summary of results."""
        summary = self.summary()
        
        print(f"\n{'='*60}")
        print(f"BACKTEST RESULTS: {summary['strategy']}")
        print(f"{'='*60}")
        print(f"Symbol: {summary['symbol']}")
        print(f"Period: {summary['period']}")
        print(f"\nPERFORMANCE METRICS:")
        print(f"Total Return: {summary['total_return']}")
        print(f"Annual Return: {summary['annual_return']}")
        print(f"Sharpe Ratio: {summary['sharpe_ratio']}")
        print(f"Max Drawdown: {summary['max_drawdown']}")
        print(f"\nTRADE STATISTICS:")
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Win Rate: {summary['win_rate']}")
        print(f"Average Trade P&L: {summary['avg_trade_pnl']}")
        print(f"Best Trade: {summary['best_trade']}")
        print(f"Worst Trade: {summary['worst_trade']}")
        print(f"Max Consecutive Wins: {summary['max_consecutive_wins']}")
        print(f"Max Consecutive Losses: {summary['max_consecutive_losses']}")
        print(f"{'='*60}\n")
