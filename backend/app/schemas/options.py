from pydantic import BaseModel, Field
from typing import Literal

class OptionPriceRequest(BaseModel):
    """Request schema for option pricing."""
    stock_price: float = Field(..., gt=0, description="Current stock price")
    strike_price: float = Field(..., gt=0, description="Option strike price")
    time_to_expiry: float = Field(..., gt=0, description="Time to expiry in years")
    risk_free_rate: float = Field(0.02, description="Risk-free interest rate")
    volatility: float = Field(..., gt=0, le=5, description="Implied volatility")
    option_type: Literal["call", "put"] = Field(..., description="Option type")
    
    class Config:
        schema_extra = {
            "example": {
                "stock_price": 150.0,
                "strike_price": 155.0,
                "time_to_expiry": 0.0833,  # 30 days
                "risk_free_rate": 0.02,
                "volatility": 0.25,
                "option_type": "call"
            }
        }

class OptionPriceResponse(BaseModel):
    """Response schema for option pricing."""
    option_price: float
    stock_price: float
    strike_price: float
    time_to_expiry: float
    risk_free_rate: float
    volatility: float
    option_type: str

class GreeksRequest(BaseModel):
    """Request schema for Greeks calculations."""
    stock_price: float = Field(..., gt=0, description="Current stock price")
    strike_price: float = Field(..., gt=0, description="Option strike price")
    time_to_expiry: float = Field(..., gt=0, description="Time to expiry in years")
    risk_free_rate: float = Field(0.02, description="Risk-free interest rate")
    volatility: float = Field(..., gt=0, le=5, description="Implied volatility")
    option_type: Literal["call", "put"] = Field(..., description="Option type")

class GreeksResponse(BaseModel):
    """Response schema for Greeks calculations."""
    delta: float = Field(..., description="Option delta")
    gamma: float = Field(..., description="Option gamma")
    theta: float = Field(..., description="Option theta")
    vega: float = Field(..., description="Option vega")
    rho: float = Field(..., description="Option rho")
    stock_price: float
    strike_price: float
    time_to_expiry: float
    risk_free_rate: float
    volatility: float
    option_type: str

class ImpliedVolatilityRequest(BaseModel):
    """Request schema for implied volatility calculation."""
    market_price: float = Field(..., gt=0, description="Market price of the option")
    stock_price: float = Field(..., gt=0, description="Current stock price")
    strike_price: float = Field(..., gt=0, description="Option strike price")
    time_to_expiry: float = Field(..., gt=0, description="Time to expiry in years")
    risk_free_rate: float = Field(0.02, description="Risk-free interest rate")
    option_type: Literal["call", "put"] = Field(..., description="Option type")
    
    class Config:
        schema_extra = {
            "example": {
                "market_price": 5.50,
                "stock_price": 150.0,
                "strike_price": 155.0,
                "time_to_expiry": 0.0833,
                "risk_free_rate": 0.02,
                "option_type": "call"
            }
        }

class ImpliedVolatilityResponse(BaseModel):
    """Response schema for implied volatility calculation."""
    implied_volatility: float = Field(..., description="Calculated implied volatility")
    market_price: float
    stock_price: float
    strike_price: float
    time_to_expiry: float
    risk_free_rate: float
    option_type: str

class OptionChainRequest(BaseModel):
    """Request schema for options chain."""
    symbol: str = Field(..., description="Stock symbol")
    expiration_date: str = Field(None, description="Expiration date (YYYY-MM-DD)")

class OptionChainOption(BaseModel):
    """Single option in options chain."""
    strike: float
    bid: float
    ask: float
    last: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float

class OptionChainResponse(BaseModel):
    """Response schema for options chain."""
    symbol: str
    expiration_date: str
    stock_price: float
    calls: list[OptionChainOption]
    puts: list[OptionChainOption]
