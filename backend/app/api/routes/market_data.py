from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any, Optional
import structlog
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

logger = structlog.get_logger()
router = APIRouter()

@router.get("/symbols/search")
async def search_symbols(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for stock symbols."""
    # Popular symbols for demo
    popular_symbols = [
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "sector": "ETF"},
        {"symbol": "QQQ", "name": "Invesco QQQ Trust", "sector": "ETF"},
        {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "sector": "ETF"},
    ]
    
    # Filter symbols based on query
    filtered = [s for s in popular_symbols if query.upper() in s["symbol"] or query.lower() in s["name"].lower()]
    
    return filtered[:limit]

@router.get("/price/{symbol}")
async def get_current_price(symbol: str) -> Dict[str, Any]:
    """Get current price for a symbol."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
            "change": info.get("regularMarketChange", 0),
            "change_percent": info.get("regularMarketChangePercent", 0),
            "volume": info.get("regularMarketVolume", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", 0),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown")
        }
    except Exception as e:
        logger.error("Failed to get price data", symbol=symbol, error=str(e))
        raise HTTPException(status_code=404, detail=f"Price data not found for {symbol}")

@router.get("/history/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = "1y",
    interval: str = "1d"
) -> Dict[str, Any]:
    """Get historical price data."""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get historical data
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for {symbol}")
        
        # Convert to list of dictionaries
        data = []
        for date, row in hist.iterrows():
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })
        
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data": data
        }
        
    except Exception as e:
        logger.error("Failed to get historical data", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/volatility/{symbol}")
async def get_volatility_data(
    symbol: str,
    days: int = 30
) -> Dict[str, Any]:
    """Calculate historical volatility."""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get historical data for volatility calculation
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days*2)  # Get more data for calculation
        
        hist = ticker.history(start=start_date, end=end_date)
        
        if len(hist) < days:
            raise HTTPException(status_code=400, detail="Insufficient data for volatility calculation")
        
        # Calculate daily returns
        hist['returns'] = hist['Close'].pct_change()
        
        # Calculate rolling volatility
        hist['volatility'] = hist['returns'].rolling(window=days).std() * (252 ** 0.5)  # Annualized
        
        # Get recent volatility data
        recent_vol = hist['volatility'].dropna().tail(30)
        
        vol_data = []
        for date, vol in recent_vol.items():
            vol_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "volatility": round(vol, 4)
            })
        
        current_vol = recent_vol.iloc[-1] if not recent_vol.empty else 0.25
        
        return {
            "symbol": symbol,
            "current_volatility": round(current_vol, 4),
            "days": days,
            "data": vol_data
        }
        
    except Exception as e:
        logger.error("Failed to calculate volatility", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-status")
async def get_market_status() -> Dict[str, Any]:
    """Get current market status."""
    now = datetime.now()
    
    # Simple market hours check (US Eastern Time)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    is_weekday = now.weekday() < 5
    is_market_hours = market_open <= now <= market_close
    
    market_status = "open" if (is_weekday and is_market_hours) else "closed"
    
    return {
        "status": market_status,
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "next_open": market_open.strftime("%Y-%m-%d %H:%M:%S") if market_status == "closed" else None,
        "next_close": market_close.strftime("%Y-%m-%d %H:%M:%S") if market_status == "open" else None
    }

@router.get("/indicators/{symbol}")
async def get_technical_indicators(
    symbol: str,
    period: str = "3mo"
) -> Dict[str, Any]:
    """Get technical indicators for a symbol."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate simple technical indicators
        current_price = hist['Close'].iloc[-1]
        
        # Moving averages
        ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
        
        # Price levels
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        
        # Volatility
        returns = hist['Close'].pct_change()
        volatility = returns.std() * (252 ** 0.5)
        
        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "ma_20": round(ma_20, 2) if ma_20 else None,
            "ma_50": round(ma_50, 2) if ma_50 else None,
            "high_52w": round(high_52w, 2),
            "low_52w": round(low_52w, 2),
            "volatility": round(volatility, 4),
            "percent_from_high": round((current_price - high_52w) / high_52w * 100, 2),
            "percent_from_low": round((current_price - low_52w) / low_52w * 100, 2)
        }
        
    except Exception as e:
        logger.error("Failed to calculate indicators", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
