from fastapi import APIRouter

from ..routes import (
    strategies,
    backtests,
    options,
    market_data,
    portfolio
)

api_router = APIRouter()

# Include all route modules
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(backtests.router, prefix="/backtests", tags=["backtests"])
api_router.include_router(options.router, prefix="/options", tags=["options"])
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
