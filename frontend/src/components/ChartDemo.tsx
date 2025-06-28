import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import TradingViewChart from '../components/TradingViewChart';

interface ChartDemoProps {
  // Optional props for demo customization
}

/**
 * Demo component showcasing the TradingViewChart component
 * with various configuration options and multiple chart instances
 */
const ChartDemo: React.FC<ChartDemoProps> = () => {
  // State for demo controls
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [interval, setInterval] = useState('1h');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [chartWidth, setChartWidth] = useState(800);
  const [chartHeight, setChartHeight] = useState(400);

  // Available trading pairs
  const tradingPairs = [
    'BTC/USDT',
    'ETH/USDT',
    'BNB/USDT',
    'ADA/USDT',
    'SOL/USDT',
    'MATIC/USDT',
    'DOT/USDT',
    'LINK/USDT'
  ];

  // Available time intervals
  const timeIntervals = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '30m', label: '30 Minutes' },
    { value: '1h', label: '1 Hour' },
    { value: '4h', label: '4 Hours' },
    { value: '1d', label: '1 Day' },
    { value: '1w', label: '1 Week' }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        TradingView Chart Component Demo
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Interactive cryptocurrency charts using TradingView Lightweight Charts library
      </Typography>

      {/* Chart Controls */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Chart Configuration
          </Typography>
          
          <Grid container spacing={3} alignItems="center">
            {/* Symbol Selection */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Trading Pair</InputLabel>
                <Select
                  value={symbol}
                  label="Trading Pair"
                  onChange={(e) => setSymbol(e.target.value)}
                >
                  {tradingPairs.map((pair) => (
                    <MenuItem key={pair} value={pair}>
                      {pair}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Interval Selection */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Time Interval</InputLabel>
                <Select
                  value={interval}
                  label="Time Interval"
                  onChange={(e) => setInterval(e.target.value)}
                >
                  {timeIntervals.map((int) => (
                    <MenuItem key={int.value} value={int.value}>
                      {int.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Theme Toggle */}
            <Grid item xs={12} sm={6} md={2}>
              <FormControlLabel
                control={
                  <Switch
                    checked={theme === 'dark'}
                    onChange={(e) => setTheme(e.target.checked ? 'dark' : 'light')}
                  />
                }
                label="Dark Theme"
              />
            </Grid>

            {/* Chart Dimensions */}
            <Grid item xs={12} md={4}>
              <Box sx={{ px: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Width: {chartWidth}px
                </Typography>
                <Slider
                  value={chartWidth}
                  onChange={(e, value) => setChartWidth(value as number)}
                  min={400}
                  max={1200}
                  step={50}
                  size="small"
                />
                
                <Typography variant="body2" gutterBottom sx={{ mt: 2 }}>
                  Height: {chartHeight}px
                </Typography>
                <Slider
                  value={chartHeight}
                  onChange={(e, value) => setChartHeight(value as number)}
                  min={300}
                  max={600}
                  step={50}
                  size="small"
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Main Chart */}
      <Paper sx={{ p: 2, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Primary Chart - {symbol} ({interval})
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <TradingViewChart
            symbol={symbol}
            interval={interval}
            theme={theme}
            width={chartWidth}
            height={chartHeight}
          />
        </Box>
      </Paper>

      {/* Multiple Charts Grid */}
      <Typography variant="h5" gutterBottom>
        Multiple Chart Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* BTC Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Bitcoin (BTC/USDT)
            </Typography>
            <TradingViewChart
              symbol="BTC/USDT"
              interval="1h"
              theme={theme}
              width={Math.min(chartWidth / 2, 600)}
              height={300}
            />
          </Paper>
        </Grid>

        {/* ETH Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Ethereum (ETH/USDT)
            </Typography>
            <TradingViewChart
              symbol="ETH/USDT"
              interval="1h"
              theme={theme}
              width={Math.min(chartWidth / 2, 600)}
              height={300}
            />
          </Paper>
        </Grid>

        {/* BNB Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Binance Coin (BNB/USDT)
            </Typography>
            <TradingViewChart
              symbol="BNB/USDT"
              interval="4h"
              theme={theme}
              width={Math.min(chartWidth / 2, 600)}
              height={300}
            />
          </Paper>
        </Grid>

        {/* ADA Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Cardano (ADA/USDT)
            </Typography>
            <TradingViewChart
              symbol="ADA/USDT"
              interval="1d"
              theme={theme}
              width={Math.min(chartWidth / 2, 600)}
              height={300}
            />
          </Paper>
        </Grid>
      </Grid>

      {/* Features List */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            TradingViewChart Component Features
          </Typography>
          
          <Divider sx={{ my: 2 }} />
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                📊 Chart Features:
              </Typography>
              <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                <li>Candlestick charts with OHLC data</li>
                <li>Volume histogram overlay</li>
                <li>Interactive crosshair and tooltips</li>
                <li>Zoom and pan functionality</li>
                <li>Time scale with automatic formatting</li>
                <li>Price scale with currency formatting</li>
                <li>Responsive design and auto-resize</li>
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                ⚙️ Technical Features:
              </Typography>
              <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                <li>React hooks integration (useEffect, useRef)</li>
                <li>TypeScript support with proper typing</li>
                <li>Loading and error state handling</li>
                <li>Light and dark theme support</li>
                <li>Configurable dimensions and symbols</li>
                <li>Memory leak prevention and cleanup</li>
                <li>Real-time data simulation</li>
              </Typography>
            </Grid>
          </Grid>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" gutterBottom>
            💡 Usage Example:
          </Typography>
          <Paper sx={{ p: 2, backgroundColor: 'grey.100', fontFamily: 'monospace' }}>
            <Typography variant="body2" component="pre">
{`<TradingViewChart
  symbol="BTC/USDT"
  interval="1h"
  theme="light"
  width={800}
  height={400}
/>`}
            </Typography>
          </Paper>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ChartDemo;
