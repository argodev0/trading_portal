import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  Refresh,
} from '@mui/icons-material';
import TradingViewChart from '../components/TradingViewChart';

const TradingChartsView: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('BINANCE:BTCUSDT');
  const [selectedInterval, setSelectedInterval] = useState('1H');

  const popularSymbols = [
    { value: 'BINANCE:BTCUSDT', label: 'BTC/USDT' },
    { value: 'BINANCE:ETHUSDT', label: 'ETH/USDT' },
    { value: 'BINANCE:BNBUSDT', label: 'BNB/USDT' },
    { value: 'BINANCE:ADAUSDT', label: 'ADA/USDT' },
    { value: 'BINANCE:SOLUSDT', label: 'SOL/USDT' },
    { value: 'BINANCE:DOTUSDT', label: 'DOT/USDT' },
  ];

  const intervals = [
    { value: '1m', label: '1 Minute' },
    { value: '5m', label: '5 Minutes' },
    { value: '15m', label: '15 Minutes' },
    { value: '1H', label: '1 Hour' },
    { value: '4H', label: '4 Hours' },
    { value: '1D', label: '1 Day' },
    { value: '1W', label: '1 Week' },
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        mb: 4 
      }}>
        <Box>
          <Typography variant="h4" sx={{ color: 'text.primary', fontWeight: 600, mb: 1 }}>
            TradingView Charts
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>
            Advanced cryptocurrency trading charts with technical analysis
          </Typography>
        </Box>
        <Chip 
          icon={<TrendingUp />}
          label="Live Data"
          variant="outlined"
          sx={{ 
            color: 'success.main',
            borderColor: 'success.main',
            '& .MuiChip-icon': { color: 'success.main' }
          }}
        />
      </Box>

      {/* Chart Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Trading Pair</InputLabel>
                <Select
                  value={selectedSymbol}
                  label="Trading Pair"
                  onChange={(e) => setSelectedSymbol(e.target.value)}
                  sx={{
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'divider',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'success.main',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'success.main',
                    },
                  }}
                >
                  {popularSymbols.map((symbol) => (
                    <MenuItem key={symbol.value} value={symbol.value}>
                      {symbol.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Time Interval</InputLabel>
                <Select
                  value={selectedInterval}
                  label="Time Interval"
                  onChange={(e) => setSelectedInterval(e.target.value)}
                  sx={{
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'divider',
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'success.main',
                    },
                    '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'success.main',
                    },
                  }}
                >
                  {intervals.map((interval) => (
                    <MenuItem key={interval.value} value={interval.value}>
                      {interval.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                fullWidth
                sx={{
                  bgcolor: 'success.main',
                  color: 'black',
                  fontWeight: 600,
                  '&:hover': {
                    bgcolor: 'success.dark',
                  }
                }}
                onClick={() => {
                  // Force refresh by updating key
                  window.location.reload();
                }}
              >
                Refresh Chart
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Main Trading Chart */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <TradingViewChart
            symbol={selectedSymbol}
            interval={selectedInterval}
            width="100%"
            height={600}
            theme="dark"
          />
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <Grid container spacing={3}>
            {/* Secondary Charts */}
            <Grid item xs={12}>
              <TradingViewChart
                symbol="BINANCE:ETHUSDT"
                interval="1H"
                width="100%"
                height={280}
                theme="dark"
              />
            </Grid>
            
            <Grid item xs={12}>
              <TradingViewChart
                symbol="BINANCE:BNBUSDT"
                interval="1H"
                width="100%"
                height={280}
                theme="dark"
              />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TradingChartsView;
