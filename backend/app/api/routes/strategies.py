from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/strategies")
async def list_strategies() -> List[Dict[str, Any]]:
    """List available trading strategies."""
    strategies = [
        {
            "id": "covered_call",
            "name": "Covered Call",
            "description": "Own stock and sell call options to generate income",
            "category": "Income",
            "risk_level": "Low",
            "parameters": [
                {"name": "strike_selection", "type": "string", "default": "30_delta", "options": ["30_delta", "5_percent_otm"]},
                {"name": "expiration_days", "type": "integer", "default": 30, "min": 7, "max": 90},
                {"name": "profit_target", "type": "float", "default": 0.5, "min": 0.1, "max": 1.0},
                {"name": "stop_loss", "type": "float", "default": 2.0, "min": 1.0, "max": 5.0}
            ]
        },
        {
            "id": "iron_condor",
            "name": "Iron Condor",
            "description": "Sell put spread and call spread for range-bound markets",
            "category": "Income",
            "risk_level": "Medium",
            "parameters": [
                {"name": "put_strike_delta", "type": "float", "default": 0.16, "min": 0.05, "max": 0.3},
                {"name": "call_strike_delta", "type": "float", "default": 0.16, "min": 0.05, "max": 0.3},
                {"name": "wing_width", "type": "float", "default": 10, "min": 5, "max": 20},
                {"name": "expiration_days", "type": "integer", "default": 45, "min": 14, "max": 90}
            ]
        },
        {
            "id": "delta_neutral",
            "name": "Delta Neutral",
            "description": "Maintain delta-neutral portfolio to profit from volatility",
            "category": "Volatility",
            "risk_level": "High",
            "parameters": [
                {"name": "target_delta", "type": "float", "default": 0.0, "min": -0.1, "max": 0.1},
                {"name": "rebalance_threshold", "type": "float", "default": 0.1, "min": 0.05, "max": 0.2},
                {"name": "strategy_type", "type": "string", "default": "short_straddle", "options": ["short_straddle", "long_straddle"]}
            ]
        },
        {
            "id": "directional",
            "name": "Directional",
            "description": "Buy calls or puts based on market direction",
            "category": "Directional",
            "risk_level": "High",
            "parameters": [
                {"name": "momentum_threshold", "type": "float", "default": 0.05, "min": 0.01, "max": 0.1},
                {"name": "option_delta", "type": "float", "default": 0.7, "min": 0.5, "max": 0.9},
                {"name": "hold_days", "type": "integer", "default": 5, "min": 1, "max": 30}
            ]
        }
    ]
    
    return strategies

@router.get("/strategies/{strategy_id}")
async def get_strategy_details(strategy_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific strategy."""
    strategies = await list_strategies()
    strategy = next((s for s in strategies if s["id"] == strategy_id), None)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return strategy

@router.post("/strategies/validate")
async def validate_strategy_parameters(
    strategy_id: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate strategy parameters."""
    try:
        strategy = await get_strategy_details(strategy_id)
        
        # Validate each parameter
        validation_errors = []
        
        for param in strategy["parameters"]:
            param_name = param["name"]
            param_type = param["type"]
            param_value = parameters.get(param_name)
            
            if param_value is None:
                continue
            
            # Type validation
            if param_type == "integer" and not isinstance(param_value, int):
                validation_errors.append(f"{param_name} must be an integer")
            elif param_type == "float" and not isinstance(param_value, (int, float)):
                validation_errors.append(f"{param_name} must be a number")
            elif param_type == "string" and not isinstance(param_value, str):
                validation_errors.append(f"{param_name} must be a string")
            
            # Range validation
            if param_type in ["integer", "float"]:
                if "min" in param and param_value < param["min"]:
                    validation_errors.append(f"{param_name} must be >= {param['min']}")
                if "max" in param and param_value > param["max"]:
                    validation_errors.append(f"{param_name} must be <= {param['max']}")
            
            # Options validation
            if "options" in param and param_value not in param["options"]:
                validation_errors.append(f"{param_name} must be one of {param['options']}")
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors
        }
        
    except Exception as e:
        logger.error("Failed to validate strategy parameters", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
