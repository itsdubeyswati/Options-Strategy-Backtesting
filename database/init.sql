-- Database initialization script for QuantOptions

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS market_data;
CREATE SCHEMA IF NOT EXISTS backtesting;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Market data tables
CREATE TABLE market_data.stocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE market_data.stock_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL,
    adjusted_close DECIMAL(12, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, date)
);

CREATE TABLE market_data.options_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    option_type VARCHAR(4) NOT NULL CHECK (option_type IN ('call', 'put')),
    strike DECIMAL(12, 4) NOT NULL,
    expiration_date DATE NOT NULL,
    date DATE NOT NULL,
    bid DECIMAL(8, 4),
    ask DECIMAL(8, 4),
    last DECIMAL(8, 4),
    volume INTEGER,
    open_interest INTEGER,
    implied_volatility DECIMAL(6, 4),
    delta DECIMAL(6, 4),
    gamma DECIMAL(8, 6),
    theta DECIMAL(8, 6),
    vega DECIMAL(8, 6),
    rho DECIMAL(8, 6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, option_type, strike, expiration_date, date)
);

-- Backtesting tables
CREATE TABLE backtesting.strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_type VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE backtesting.backtests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_id UUID NOT NULL REFERENCES backtesting.strategies(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    results JSONB
);

CREATE TABLE backtesting.portfolio_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    backtest_id UUID NOT NULL REFERENCES backtesting.backtests(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    cash DECIMAL(15, 2) NOT NULL,
    portfolio_value DECIMAL(15, 2) NOT NULL,
    positions_value DECIMAL(15, 2) NOT NULL,
    delta DECIMAL(10, 4),
    gamma DECIMAL(10, 6),
    theta DECIMAL(10, 6),
    vega DECIMAL(10, 6),
    rho DECIMAL(10, 6),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(backtest_id, date)
);

CREATE TABLE backtesting.trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    backtest_id UUID NOT NULL REFERENCES backtesting.backtests(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    option_type VARCHAR(10) NOT NULL CHECK (option_type IN ('call', 'put', 'stock')),
    strike DECIMAL(12, 4),
    expiration_date DATE,
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(8, 4) NOT NULL,
    exit_price DECIMAL(8, 4),
    entry_date DATE NOT NULL,
    exit_date DATE,
    pnl DECIMAL(12, 2),
    commission DECIMAL(6, 2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed', 'expired')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics tables
CREATE TABLE analytics.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    backtest_id UUID NOT NULL REFERENCES backtesting.backtests(id) ON DELETE CASCADE,
    total_return DECIMAL(8, 4),
    annual_return DECIMAL(8, 4),
    volatility DECIMAL(8, 4),
    sharpe_ratio DECIMAL(8, 4),
    max_drawdown DECIMAL(8, 4),
    win_rate DECIMAL(6, 4),
    profit_factor DECIMAL(8, 4),
    avg_trade_pnl DECIMAL(10, 2),
    max_consecutive_wins INTEGER,
    max_consecutive_losses INTEGER,
    total_trades INTEGER,
    profitable_trades INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_stock_prices_symbol_date ON market_data.stock_prices(symbol, date);
CREATE INDEX idx_stock_prices_date ON market_data.stock_prices(date);

CREATE INDEX idx_options_data_symbol_exp_date ON market_data.options_data(symbol, expiration_date, date);
CREATE INDEX idx_options_data_symbol_strike ON market_data.options_data(symbol, strike);

CREATE INDEX idx_backtests_status ON backtesting.backtests(status);
CREATE INDEX idx_backtests_created_at ON backtesting.backtests(created_at);

CREATE INDEX idx_portfolio_snapshots_backtest_date ON backtesting.portfolio_snapshots(backtest_id, date);

CREATE INDEX idx_trades_backtest_id ON backtesting.trades(backtest_id);
CREATE INDEX idx_trades_symbol_date ON backtesting.trades(symbol, entry_date);

-- Create functions for updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_stocks_updated_at BEFORE UPDATE ON market_data.stocks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON backtesting.strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO market_data.stocks (symbol, name, sector, industry) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics'),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software'),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Content & Information'),
('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary', 'Internet & Direct Marketing Retail'),
('TSLA', 'Tesla Inc.', 'Consumer Discretionary', 'Auto Manufacturers'),
('SPY', 'SPDR S&P 500 ETF Trust', 'ETF', 'Large Blend'),
('QQQ', 'Invesco QQQ Trust', 'ETF', 'Large Growth'),
('IWM', 'iShares Russell 2000 ETF', 'ETF', 'Small Blend');

-- Insert sample strategies
INSERT INTO backtesting.strategies (name, description, strategy_type, parameters) VALUES
('Basic Covered Call', 'Sell 30-delta call options monthly against stock holdings', 'covered_call', 
 '{"strike_selection": "30_delta", "expiration_days": 30, "profit_target": 0.5, "stop_loss": 2.0}'),
 
('Iron Condor Monthly', 'Sell monthly iron condors with 16-delta strikes', 'iron_condor',
 '{"put_strike_delta": 0.16, "call_strike_delta": 0.16, "wing_width": 10, "expiration_days": 45, "profit_target": 0.5, "stop_loss": 2.0}'),
 
('Delta Neutral Straddle', 'Maintain delta-neutral portfolio with short straddles', 'delta_neutral',
 '{"target_delta": 0.0, "rebalance_threshold": 0.1, "strategy_type": "short_straddle"}'),
 
('Momentum Call Buying', 'Buy calls on stocks with strong momentum', 'directional',
 '{"momentum_threshold": 0.05, "option_delta": 0.7, "hold_days": 5, "profit_target": 1.0, "stop_loss": 0.5}');

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA market_data TO quantoptions;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA backtesting TO quantoptions;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO quantoptions;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA market_data TO quantoptions;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA backtesting TO quantoptions;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO quantoptions;
