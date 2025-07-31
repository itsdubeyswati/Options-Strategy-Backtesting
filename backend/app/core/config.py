from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_NAME: str = "QuantOptions"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://quantoptions:password@localhost:5432/quantoptions"
    DATABASE_ECHO: bool = False
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    POLYGON_API_KEY: Optional[str] = None
    
    # Options pricing settings
    RISK_FREE_RATE: float = 0.02  # 2% default risk-free rate
    DEFAULT_VOLATILITY: float = 0.25  # 25% default volatility
    
    # Backtesting settings
    DEFAULT_COMMISSION: float = 1.0  # $1.00 per option contract
    DEFAULT_SLIPPAGE: float = 0.01  # 1% slippage
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
