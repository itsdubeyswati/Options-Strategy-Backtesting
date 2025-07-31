"""
Options Strategy Backtesting Platform

A comprehensive platform for options pricing, strategy backtesting, and portfolio analysis.
Developed for quantitative trading analysis and educational purposes.

Features:
- Black-Scholes option pricing with full Greeks calculations
- Multiple options trading strategies (Covered Call, Iron Condor, Delta Neutral, etc.)
- Historical backtesting with performance metrics
- Real-time market data integration via yfinance
- RESTful API with FastAPI
- PostgreSQL database for data persistence
- Docker containerization for easy deployment

Author: Swati
Date: July 2025
"""

import sys
import os
import uvicorn

# Add current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from app.main import app
except ImportError as e:
    print(f"Import error: {e}")
    print("Creating a simple FastAPI app for demonstration...")
    
    from fastapi import FastAPI
    
    app = FastAPI(
        title="Options Strategy Backtesting Platform",
        description="A comprehensive platform for options pricing and strategy backtesting",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Options Strategy Backtesting Platform",
            "status": "running",
            "features": [
                "Black-Scholes Option Pricing",
                "Greeks Calculations", 
                "Trading Strategies",
                "Backtesting Engine"
            ]
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "platform": "options_backtesting"}

if __name__ == "__main__":
    print("🚀 Starting Options Strategy Backtesting Platform...")
    print("📊 Features: Black-Scholes Pricing, Greeks, Strategy Backtesting")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)
