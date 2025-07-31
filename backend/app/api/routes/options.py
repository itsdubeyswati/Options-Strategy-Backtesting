from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import structlog

from ....pricing.black_scholes import BlackScholesCalculator, ImpliedVolatilityCalculator
from ....pricing.greeks import GreeksCalculator
from ...schemas.options import (
    OptionPriceRequest,
    OptionPriceResponse,
    GreeksRequest,
    GreeksResponse,
    ImpliedVolatilityRequest,
    ImpliedVolatilityResponse
)

logger = structlog.get_logger()
router = APIRouter()

@router.post("/price", response_model=OptionPriceResponse)
async def calculate_option_price(request: OptionPriceRequest) -> OptionPriceResponse:
    """Calculate option price using Black-Scholes model."""
    try:
        price = BlackScholesCalculator.option_price(
            S=request.stock_price,
            K=request.strike_price,
            T=request.time_to_expiry,
            r=request.risk_free_rate,
            sigma=request.volatility,
            option_type=request.option_type
        )
        
        return OptionPriceResponse(
            option_price=price,
            stock_price=request.stock_price,
            strike_price=request.strike_price,
            time_to_expiry=request.time_to_expiry,
            volatility=request.volatility,
            risk_free_rate=request.risk_free_rate,
            option_type=request.option_type
        )
    
    except Exception as e:
        logger.error("Failed to calculate option price", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/greeks", response_model=GreeksResponse)
async def calculate_greeks(request: GreeksRequest) -> GreeksResponse:
    """Calculate option Greeks."""
    try:
        greeks = GreeksCalculator.all_greeks(
            S=request.stock_price,
            K=request.strike_price,
            T=request.time_to_expiry,
            r=request.risk_free_rate,
            sigma=request.volatility,
            option_type=request.option_type
        )
        
        return GreeksResponse(
            delta=greeks['delta'],
            gamma=greeks['gamma'],
            theta=greeks['theta'],
            vega=greeks['vega'],
            rho=greeks['rho'],
            stock_price=request.stock_price,
            strike_price=request.strike_price,
            time_to_expiry=request.time_to_expiry,
            volatility=request.volatility,
            risk_free_rate=request.risk_free_rate,
            option_type=request.option_type
        )
    
    except Exception as e:
        logger.error("Failed to calculate Greeks", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/implied-volatility", response_model=ImpliedVolatilityResponse)
async def calculate_implied_volatility(
    request: ImpliedVolatilityRequest
) -> ImpliedVolatilityResponse:
    """Calculate implied volatility from market price."""
    try:
        # Try Newton-Raphson first, fallback to bisection
        iv = ImpliedVolatilityCalculator.newton_raphson_iv(
            market_price=request.market_price,
            S=request.stock_price,
            K=request.strike_price,
            T=request.time_to_expiry,
            r=request.risk_free_rate,
            option_type=request.option_type
        )
        
        if iv is None:
            iv = ImpliedVolatilityCalculator.bisection_iv(
                market_price=request.market_price,
                S=request.stock_price,
                K=request.strike_price,
                T=request.time_to_expiry,
                r=request.risk_free_rate,
                option_type=request.option_type
            )
        
        if iv is None:
            raise ValueError("Unable to calculate implied volatility")
        
        return ImpliedVolatilityResponse(
            implied_volatility=iv,
            market_price=request.market_price,
            stock_price=request.stock_price,
            strike_price=request.strike_price,
            time_to_expiry=request.time_to_expiry,
            risk_free_rate=request.risk_free_rate,
            option_type=request.option_type
        )
    
    except Exception as e:
        logger.error("Failed to calculate implied volatility", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/chain/{symbol}")
async def get_options_chain(
    symbol: str,
    expiration_date: Optional[str] = None
) -> Dict[str, Any]:
    """Get options chain for a symbol (placeholder for real data)."""
    try:
        # This would connect to real options data provider
        # For now, return mock data structure
        return {
            "symbol": symbol,
            "expiration_date": expiration_date,
            "calls": [
                {
                    "strike": 100,
                    "bid": 2.50,
                    "ask": 2.60,
                    "last": 2.55,
                    "volume": 150,
                    "open_interest": 1200,
                    "implied_volatility": 0.25
                }
            ],
            "puts": [
                {
                    "strike": 100,
                    "bid": 1.80,
                    "ask": 1.90,
                    "last": 1.85,
                    "volume": 80,
                    "open_interest": 800,
                    "implied_volatility": 0.26
                }
            ]
        }
    
    except Exception as e:
        logger.error("Failed to get options chain", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategies/profit-loss")
async def calculate_strategy_pnl(
    positions: List[Dict[str, Any]],
    stock_prices: List[float],
    current_stock_price: float
) -> Dict[str, Any]:
    """Calculate profit/loss for options strategy at different stock prices."""
    try:
        pnl_data = []
        
        for stock_price in stock_prices:
            total_pnl = 0
            
            for position in positions:
                quantity = position.get('quantity', 0)
                strike = position.get('strike')
                option_type = position.get('option_type')
                premium_paid = position.get('premium_paid', 0)
                
                if option_type == 'call':
                    intrinsic_value = max(stock_price - strike, 0)
                elif option_type == 'put':
                    intrinsic_value = max(strike - stock_price, 0)
                else:  # stock
                    intrinsic_value = stock_price
                    strike = current_stock_price  # Use entry price
                
                position_pnl = quantity * (intrinsic_value - premium_paid)
                total_pnl += position_pnl
            
            pnl_data.append({
                'stock_price': stock_price,
                'pnl': total_pnl
            })
        
        return {
            'pnl_data': pnl_data,
            'max_profit': max(data['pnl'] for data in pnl_data),
            'max_loss': min(data['pnl'] for data in pnl_data),
            'breakeven_points': [
                data['stock_price'] for data in pnl_data 
                if abs(data['pnl']) < 0.01
            ]
        }
    
    except Exception as e:
        logger.error("Failed to calculate strategy P&L", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
