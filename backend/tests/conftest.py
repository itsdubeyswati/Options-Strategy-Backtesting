"""
Test configuration for Options Strategy Backtesting Platform
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Test database URL - using SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Create a test client."""
    with TestClient(app) as c:
        yield c

# Sample test data
@pytest.fixture
def sample_option_data():
    """Sample option pricing data for tests."""
    return {
        "underlying_price": 100.0,
        "strike_price": 105.0,
        "days_to_expiry": 30,
        "volatility": 0.25,
        "risk_free_rate": 0.05,
        "option_type": "call"
    }

@pytest.fixture
def sample_backtest_data():
    """Sample backtest data for tests."""
    return {
        "strategy_type": "covered_call",
        "symbol": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "initial_capital": 100000,
        "parameters": {
            "strike_selection": "otm_5",
            "expiry_days": 30,
            "profit_target": 0.5,
            "stop_loss": 2.0
        }
    }
