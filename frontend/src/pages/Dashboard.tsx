import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Assessment as AssessmentIcon,
  AccountBalance as AccountBalanceIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock data - in real app, this would come from API
const portfolioMetrics = {
  totalValue: 125430.50,
  dailyChange: 2340.25,
  dailyChangePercent: 1.90,
  totalReturn: 25430.50,
  totalReturnPercent: 25.43,
};

const recentBacktests = [
  {
    id: '1',
    strategy: 'Covered Call',
    symbol: 'AAPL',
    return: 15.2,
    sharpe: 1.34,
    maxDrawdown: -8.5,
    status: 'Completed',
    date: '2024-01-15',
  },
  {
    id: '2',
    strategy: 'Iron Condor',
    symbol: 'SPY',
    return: 12.8,
    sharpe: 1.12,
    maxDrawdown: -12.3,
    status: 'Completed',
    date: '2024-01-14',
  },
  {
    id: '3',
    strategy: 'Delta Neutral',
    symbol: 'QQQ',
    return: 8.9,
    sharpe: 0.98,
    maxDrawdown: -6.2,
    status: 'Running',
    date: '2024-01-13',
  },
];

const equityCurveData = [
  { date: '2024-01-01', value: 100000 },
  { date: '2024-01-02', value: 101200 },
  { date: '2024-01-03', value: 102800 },
  { date: '2024-01-04', value: 101900 },
  { date: '2024-01-05', value: 103500 },
  { date: '2024-01-08', value: 105200 },
  { date: '2024-01-09', value: 107100 },
  { date: '2024-01-10', value: 108900 },
  { date: '2024-01-11', value: 110300 },
  { date: '2024-01-12', value: 112700 },
  { date: '2024-01-15', value: 115400 },
];

export default function Dashboard() {
  const theme = useTheme();
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');
  }, []);

  const MetricCard = ({ 
    title, 
    value, 
    subtitle, 
    icon, 
    color = 'primary' 
  }: {
    title: string;
    value: string;
    subtitle?: string;
    icon: React.ReactNode;
    color?: 'primary' | 'secondary' | 'success' | 'error';
  }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={`${color}.main`}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ color: `${color}.main` }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {greeting}! Welcome to QuantOptions
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Monitor your options trading strategies and portfolio performance.
      </Typography>

      {/* Portfolio Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Portfolio Value"
            value={`$${portfolioMetrics.totalValue.toLocaleString()}`}
            icon={<AccountBalanceIcon fontSize="large" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Daily P&L"
            value={`$${portfolioMetrics.dailyChange.toLocaleString()}`}
            subtitle={`${portfolioMetrics.dailyChangePercent > 0 ? '+' : ''}${portfolioMetrics.dailyChangePercent}%`}
            icon={portfolioMetrics.dailyChange > 0 ? <TrendingUpIcon fontSize="large" /> : <TrendingDownIcon fontSize="large" />}
            color={portfolioMetrics.dailyChange > 0 ? 'success' : 'error'}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Return"
            value={`$${portfolioMetrics.totalReturn.toLocaleString()}`}
            subtitle={`${portfolioMetrics.totalReturnPercent}%`}
            icon={<TrendingUpIcon fontSize="large" />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Strategies"
            value="3"
            subtitle="2 profitable"
            icon={<AssessmentIcon fontSize="large" />}
            color="primary"
          />
        </Grid>
      </Grid>

      {/* Equity Curve Chart */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Portfolio Equity Curve
          </Typography>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={equityCurveData}>
                <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                <XAxis 
                  dataKey="date" 
                  stroke={theme.palette.text.secondary}
                  tick={{ fill: theme.palette.text.secondary }}
                />
                <YAxis 
                  stroke={theme.palette.text.secondary}
                  tick={{ fill: theme.palette.text.secondary }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: theme.palette.background.paper,
                    border: `1px solid ${theme.palette.divider}`,
                    borderRadius: '4px'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke={theme.palette.primary.main} 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </CardContent>
      </Card>

      {/* Recent Backtests */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="h6">
              Recent Backtests
            </Typography>
            <Button variant="outlined" size="small">
              View All
            </Button>
          </Box>
          <TableContainer component={Paper} sx={{ backgroundColor: 'transparent' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Strategy</TableCell>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Return (%)</TableCell>
                  <TableCell align="right">Sharpe Ratio</TableCell>
                  <TableCell align="right">Max Drawdown (%)</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {recentBacktests.map((backtest) => (
                  <TableRow key={backtest.id}>
                    <TableCell component="th" scope="row">
                      {backtest.strategy}
                    </TableCell>
                    <TableCell>{backtest.symbol}</TableCell>
                    <TableCell align="right">
                      <Typography
                        color={backtest.return > 0 ? 'success.main' : 'error.main'}
                      >
                        {backtest.return > 0 ? '+' : ''}{backtest.return}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{backtest.sharpe}</TableCell>
                    <TableCell align="right">
                      <Typography color="error.main">
                        {backtest.maxDrawdown}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={backtest.status}
                        color={backtest.status === 'Completed' ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{backtest.date}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}
