from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import structlog

from ...core.database import get_db
from ...services.backtest_service import BacktestService
from ...schemas.backtest import (
    BacktestRequest, 
    BacktestResponse, 
    BacktestStatus,
    BacktestResults
)

logger = structlog.get_logger()
router = APIRouter()

@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    db: AsyncSession = Depends(get_db)
) -> BacktestResponse:
    """Run a new backtest."""
    try:
        logger.info("Starting backtest", strategy=request.strategy_name, symbol=request.symbol)
        
        service = BacktestService(db)
        backtest_id = await service.run_backtest(request)
        
        return BacktestResponse(
            backtest_id=backtest_id,
            status=BacktestStatus.RUNNING,
            message="Backtest started successfully"
        )
    
    except Exception as e:
        logger.error("Failed to start backtest", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{backtest_id}/status", response_model=BacktestResponse)
async def get_backtest_status(
    backtest_id: str,
    db: AsyncSession = Depends(get_db)
) -> BacktestResponse:
    """Get backtest status."""
    try:
        service = BacktestService(db)
        status = await service.get_backtest_status(backtest_id)
        
        if status is None:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        return status
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get backtest status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{backtest_id}/results", response_model=BacktestResults)
async def get_backtest_results(
    backtest_id: str,
    db: AsyncSession = Depends(get_db)
) -> BacktestResults:
    """Get backtest results."""
    try:
        service = BacktestService(db)
        results = await service.get_backtest_results(backtest_id)
        
        if results is None:
            raise HTTPException(status_code=404, detail="Backtest results not found")
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get backtest results", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[BacktestResponse])
async def list_backtests(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[BacktestResponse]:
    """List all backtests."""
    try:
        service = BacktestService(db)
        backtests = await service.list_backtests(limit=limit, offset=offset)
        return backtests
    
    except Exception as e:
        logger.error("Failed to list backtests", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{backtest_id}")
async def delete_backtest(
    backtest_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Delete a backtest."""
    try:
        service = BacktestService(db)
        await service.delete_backtest(backtest_id)
        
        return {"message": "Backtest deleted successfully"}
    
    except Exception as e:
        logger.error("Failed to delete backtest", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{backtest_id}/equity-curve")
async def get_equity_curve(
    backtest_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get equity curve data for visualization."""
    try:
        service = BacktestService(db)
        equity_curve = await service.get_equity_curve(backtest_id)
        
        if equity_curve is None:
            raise HTTPException(status_code=404, detail="Equity curve not found")
        
        return equity_curve
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get equity curve", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{backtest_id}/trades")
async def get_backtest_trades(
    backtest_id: str,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get trade history for a backtest."""
    try:
        service = BacktestService(db)
        trades = await service.get_backtest_trades(backtest_id, limit=limit, offset=offset)
        
        if trades is None:
            raise HTTPException(status_code=404, detail="Trades not found")
        
        return trades
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get backtest trades", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
