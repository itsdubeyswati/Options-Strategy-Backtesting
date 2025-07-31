import React from "react";
import "./App.css";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Options Strategy Backtesting Platform</h1>
        <p>Professional-grade options pricing and strategy analysis</p>

        <div className="feature-grid">
          <div className="feature-card">
            <h3>📊 Black-Scholes Pricing</h3>
            <p>
              Professional options valuation with industry-standard mathematical
              models
            </p>
          </div>

          <div className="feature-card">
            <h3>📈 Greeks Analytics</h3>
            <p>
              Complete risk metrics: Delta, Gamma, Theta, Vega, and Rho
              calculations
            </p>
          </div>

          <div className="feature-card">
            <h3>🎯 Strategy Backtesting</h3>
            <p>
              Test trading strategies with historical data and performance
              analytics
            </p>
          </div>

          <div className="feature-card">
            <h3>💼 Portfolio Analysis</h3>
            <p>Comprehensive portfolio tracking and risk management tools</p>
          </div>
        </div>

        <div className="status-section">
          <h2>Platform Status</h2>
          <div className="status-grid">
            <div>
              <p>
                ✅ <strong>Backend API:</strong> http://localhost:8000
              </p>
              <p>
                ✅ <strong>API Documentation:</strong>{" "}
                http://localhost:8000/docs
              </p>
              <p>
                ✅ <strong>Black-Scholes Engine:</strong> Fully Operational
              </p>
            </div>
            <div>
              <p>
                ✅ <strong>Greeks Calculator:</strong> All 5 metrics active
              </p>
              <p>
                ✅ <strong>Strategy Framework:</strong> Ready for backtesting
              </p>
              <p>
                🎯 <strong>Platform:</strong> Production Ready
              </p>
            </div>
          </div>
        </div>

        <footer>
          <p>
            Built by Swati | Quantitative Finance & Full-Stack Development
            Portfolio
          </p>
        </footer>
      </header>
    </div>
  );
}

export default App;
import { Box, Container, Typography, Paper, Grid, Card, CardContent } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CalculateIcon from '@mui/icons-material/Calculate';
import TimelineIcon from '@mui/icons-material/Timeline';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';

// Create dark theme for professional trading platform look
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00e676',
    },
    secondary: {
      main: '#ff5722',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
        <Container maxWidth="lg" sx={{ py: 4 }}>
          {/* Header */}
          <Paper elevation={3} sx={{ p: 4, mb: 4, textAlign: 'center' }}>
            <Typography variant="h4" component="h1" gutterBottom color="primary">
              🚀 Options Strategy Backtesting Platform
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Professional-grade options pricing, Greeks calculations, and strategy backtesting
            </Typography>
            <Typography variant="body1" sx={{ mt: 2 }}>
              Built with Black-Scholes models, FastAPI backend, and React frontend
            </Typography>
          </Paper>

          {/* Feature Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6} lg={3}>
              <Card elevation={2} sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <CalculateIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Black-Scholes Pricing
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Professional options valuation using industry-standard mathematical models
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6} lg={3}>
              <Card elevation={2} sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <TimelineIcon sx={{ fontSize: 48, color: 'secondary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Greeks Analytics
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Complete risk metrics: Delta, Gamma, Theta, Vega, and Rho calculations
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6} lg={3}>
              <Card elevation={2} sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <TrendingUpIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Strategy Backtesting
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Test trading strategies with historical data and performance analytics
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6} lg={3}>
              <Card elevation={2} sx={{ height: '100%' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <AccountBalanceIcon sx={{ fontSize: 48, color: 'secondary.main', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Portfolio Analysis
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Comprehensive portfolio tracking and risk management tools
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Status Section */}
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom color="primary">
              Platform Status
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  ✅ <strong>Backend API:</strong> http://localhost:8000
                </Typography>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  ✅ <strong>API Documentation:</strong> http://localhost:8000/docs
                </Typography>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  ✅ <strong>Black-Scholes Engine:</strong> Fully Operational
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  ✅ <strong>Greeks Calculator:</strong> All 5 metrics active
                </Typography>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  ✅ <strong>Strategy Framework:</strong> Ready for backtesting
                </Typography>
                <Typography variant="body1" sx={{ mb: 1 }}>
                  🎯 <strong>Platform:</strong> Production Ready
                </Typography>
              </Grid>
            </Grid>
          </Paper>

          {/* Footer */}
          <Box sx={{ textAlign: 'center', mt: 4, py: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Built by Swati | Quantitative Finance & Full-Stack Development Portfolio
            </Typography>
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default App;
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
      light: '#ff5983',
      dark: '#9a0036',
    },
    background: {
      default: '#0a0e27',
      paper: '#1e2139',
    },
    success: {
      main: '#4caf50',
    },
    error: {
      main: '#f44336',
    },
    warning: {
      main: '#ff9800',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#1e2139',
          border: '1px solid #2d3748',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: '1px solid #2d3748',
          '& .MuiDataGrid-cell': {
            borderColor: '#2d3748',
          },
          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: '#2d3748',
            borderColor: '#2d3748',
          },
        },
      },
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/strategy-builder" element={<StrategyBuilder />} />
              <Route path="/backtest-results/:backtestId?" element={<BacktestResults />} />
              <Route path="/options-calculator" element={<OptionsCalculator />} />
              <Route path="/market-data" element={<MarketData />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
