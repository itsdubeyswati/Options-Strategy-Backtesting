from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class BacktestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class StrategyType(str, Enum):
    COVERED_CALL = "covered_call"
    IRON_CONDOR = "iron_condor"
    DELTA_NEUTRAL = "delta_neutral"
    DIRECTIONAL = "directional"
    BUTTERFLY = "butterfly"
    STRADDLE = "straddle"
    STRANGLE = "strangle"

class BacktestRequest(BaseModel):
    """Request schema for creating a new backtest."""
    strategy_name: str = Field(..., description="Name of the strategy to test")
    strategy_type: StrategyType = Field(..., description="Type of strategy")
    symbol: str = Field(..., description="Stock symbol to trade")
    start_date: str = Field(..., description="Start date for backtest (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date for backtest (YYYY-MM-DD)")
    initial_capital: float = Field(100000, description="Initial capital for backtest")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Strategy-specific parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "strategy_name": "AAPL Covered Calls",
                "strategy_type": "covered_call",
                "symbol": "AAPL",
                "start_date": "2021-01-01",
                "end_date": "2023-12-31",
                "initial_capital": 100000,
                "parameters": {
                    "strike_selection": "30_delta",
                    "expiration_days": 30,
                    "profit_target": 0.5,
                    "stop_loss": 2.0
                }
            }
        }

class BacktestResponse(BaseModel):
    """Response schema for backtest operations."""
    backtest_id: str = Field(..., description="Unique identifier for the backtest")
    status: BacktestStatus = Field(..., description="Current status of the backtest")
    message: str = Field(..., description="Status message or error description")
    progress: Optional[int] = Field(None, description="Progress percentage (0-100)")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

class PerformanceMetrics(BaseModel):
    """Performance metrics for a backtest."""
    total_return: float = Field(..., description="Total return percentage")
    annual_return: float = Field(..., description="Annualized return percentage")
    volatility: float = Field(..., description="Annualized volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown percentage")
    win_rate: float = Field(..., description="Win rate percentage")
    profit_factor: Optional[float] = Field(None, description="Profit factor")
    total_trades: int = Field(..., description="Total number of trades")
    profitable_trades: int = Field(..., description="Number of profitable trades")
    avg_trade_pnl: float = Field(..., description="Average trade P&L")
    max_consecutive_wins: int = Field(..., description="Maximum consecutive wins")
    max_consecutive_losses: int = Field(..., description="Maximum consecutive losses")

class TradeData(BaseModel):
    """Individual trade data."""
    symbol: str
    option_type: str
    strike: Optional[float]
    expiration_date: Optional[str]
    quantity: int
    entry_price: float
    exit_price: Optional[float]
    entry_date: str
    exit_date: Optional[str]
    pnl: Optional[float]
    commission: float
    status: str

class EquityPoint(BaseModel):
    """Single point in equity curve."""
    date: str
    portfolio_value: float
    cash: float
    positions_value: float

class BacktestResults(BaseModel):
    """Complete backtest results."""
    backtest_id: str
    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    performance_metrics: PerformanceMetrics
    equity_curve: List[EquityPoint]
    trades: List[TradeData]
    status: BacktestStatus
    created_at: datetime
    completed_at: Optional[datetime]

class BacktestSummary(BaseModel):
    """Summary information for backtest listing."""
    backtest_id: str
    strategy_name: str
    symbol: str
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    status: BacktestStatus
    created_at: datetime
