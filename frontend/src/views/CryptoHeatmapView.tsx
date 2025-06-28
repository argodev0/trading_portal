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
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  Timeline,
  Refresh,
  TrendingUp,
} from '@mui/icons-material';
import CryptoHeatmap from '../components/CryptoHeatmap';

const CryptoHeatmapView: React.FC = () => {
  const [selectedExchange, setSelectedExchange] = useState('BINANCE');
  const [selectedTimeframe, setSelectedTimeframe] = useState('price-changes');
  const [selectedSize, setSelectedSize] = useState('market_cap_basic');

  const exchanges = [
    { value: 'BINANCE', label: 'Binance' },
    { value: 'COINBASE', label: 'Coinbase' },
    { value: 'KRAKEN', label: 'Kraken' },
    { value: 'HUOBI', label: 'Huobi' },
  ];

  const timeframes = [
    { value: 'price-changes', label: 'Price Changes' },
    { value: 'Perf%D', label: '1 Day' },
    { value: 'Perf%W', label: '1 Week' },
    { value: 'Perf%M', label: '1 Month' },
    { value: 'Perf%3M', label: '3 Months' },
    { value: 'Perf%6M', label: '6 Months' },
    { value: 'Perf%Y', label: '1 Year' },
  ];

  const sizingOptions = [
    { value: 'market_cap_basic', label: 'Market Cap' },
    { value: 'volume', label: 'Volume' },
    { value: 'last_price', label: 'Price' },
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
            Crypto Market Heatmap
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>
            Real-time cryptocurrency market visualization and performance tracking
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip 
            icon={<Timeline />}
            label="Real-time Data"
            variant="outlined"
            sx={{ 
              color: 'success.main',
              borderColor: 'success.main',
              '& .MuiChip-icon': { color: 'success.main' }
            }}
          />
          <Chip 
            icon={<TrendingUp />}
            label="Live Updates"
            variant="outlined"
            sx={{ 
              color: 'primary.main',
              borderColor: 'primary.main',
              '& .MuiChip-icon': { color: 'primary.main' }
            }}
          />
        </Box>
      </Box>

      {/* Heatmap Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Exchange</InputLabel>
                <Select
                  value={selectedExchange}
                  label="Exchange"
                  onChange={(e) => setSelectedExchange(e.target.value)}
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
                  {exchanges.map((exchange) => (
                    <MenuItem key={exchange.value} value={exchange.value}>
                      {exchange.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Timeframe</InputLabel>
                <Select
                  value={selectedTimeframe}
                  label="Timeframe"
                  onChange={(e) => setSelectedTimeframe(e.target.value)}
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
                  {timeframes.map((timeframe) => (
                    <MenuItem key={timeframe.value} value={timeframe.value}>
                      {timeframe.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Block Size</InputLabel>
                <Select
                  value={selectedSize}
                  label="Block Size"
                  onChange={(e) => setSelectedSize(e.target.value)}
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
                  {sizingOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
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
                  // Force refresh by reloading component
                  window.location.reload();
                }}
              >
                Refresh Heatmap
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Main Heatmap */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <CryptoHeatmap
            width="100%"
            height={700}
            dataSource="Crypto"
            exchange={selectedExchange}
            symbolsGroups="crypto"
            hasTopBar={true}
            isTransparent={false}
            noTimeScale={false}
            valuesTracking="1"
            changeMode={selectedTimeframe as any}
            locale="en"
            theme="dark"
          />
        </Grid>
      </Grid>

      {/* Additional Market Info */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ color: 'text.primary', fontWeight: 600, mb: 2 }}>
                Market Overview
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
                The heatmap visualizes cryptocurrency performance using block sizes and colors to represent market cap and price changes.
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label="Green = Positive" size="small" sx={{ bgcolor: 'success.main', color: 'black' }} />
                <Chip label="Red = Negative" size="small" sx={{ bgcolor: 'error.main', color: 'white' }} />
                <Chip label="Size = Market Cap" size="small" variant="outlined" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ color: 'text.primary', fontWeight: 600, mb: 2 }}>
                How to Read
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
                • Larger blocks = Higher market capitalization
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
                • Green colors = Price increases
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
                • Red colors = Price decreases
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                • Hover over blocks for detailed information
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CryptoHeatmapView;
