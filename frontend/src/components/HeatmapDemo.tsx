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
  Card,
  CardContent,
  Divider,
  Slider
} from '@mui/material';
import CryptoHeatmap from '../components/CryptoHeatmap';

interface HeatmapDemoProps {
  // Optional props for demo customization
}

/**
 * Demo component showcasing the CryptoHeatmap component
 * with various configuration options
 */
const HeatmapDemo: React.FC<HeatmapDemoProps> = () => {
  // State for demo controls
  const [exchange, setExchange] = useState('BINANCE');
  const [changeMode, setChangeMode] = useState<'price-changes' | 'Perf%D' | 'Perf%W' | 'Perf%M' | 'Perf%3M' | 'Perf%6M' | 'Perf%Y' | 'Perf%YTD'>('price-changes');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [hasTopBar, setHasTopBar] = useState(true);
  const [isTransparent, setIsTransparent] = useState(false);
  const [height, setHeight] = useState(500);

  // Available exchanges
  const exchanges = [
    'BINANCE',
    'COINBASE',
    'KRAKEN',
    'BITSTAMP',
    'BITFINEX',
    'HUOBI',
    'OKEX'
  ];

  // Available change modes
  const changeModes = [
    { value: 'price-changes', label: 'Price Changes' },
    { value: 'Perf%D', label: 'Daily Performance' },
    { value: 'Perf%W', label: 'Weekly Performance' },
    { value: 'Perf%M', label: 'Monthly Performance' },
    { value: 'Perf%3M', label: '3-Month Performance' },
    { value: 'Perf%6M', label: '6-Month Performance' },
    { value: 'Perf%Y', label: 'Yearly Performance' },
    { value: 'Perf%YTD', label: 'Year-to-Date Performance' }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Crypto Heatmap Component Demo
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Interactive cryptocurrency market heatmap using TradingView's Crypto Coins Heatmap widget
      </Typography>

      {/* Heatmap Controls */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Heatmap Configuration
          </Typography>
          
          <Grid container spacing={3} alignItems="center">
            {/* Exchange Selection */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Exchange</InputLabel>
                <Select
                  value={exchange}
                  label="Exchange"
                  onChange={(e) => setExchange(e.target.value)}
                >
                  {exchanges.map((ex) => (
                    <MenuItem key={ex} value={ex}>
                      {ex}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Change Mode Selection */}
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Performance Metric</InputLabel>
                <Select
                  value={changeMode}
                  label="Performance Metric"
                  onChange={(e) => setChangeMode(e.target.value as any)}
                >
                  {changeModes.map((mode) => (
                    <MenuItem key={mode.value} value={mode.value}>
                      {mode.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Theme Selection */}
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Theme</InputLabel>
                <Select
                  value={theme}
                  label="Theme"
                  onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Top Bar Toggle */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={hasTopBar}
                    onChange={(e) => setHasTopBar(e.target.checked)}
                  />
                }
                label="Show Top Bar"
              />
            </Grid>

            {/* Transparent Background Toggle */}
            <Grid item xs={12} sm={6} md={3}>
              <FormControlLabel
                control={
                  <Switch
                    checked={isTransparent}
                    onChange={(e) => setIsTransparent(e.target.checked)}
                  />
                }
                label="Transparent Background"
              />
            </Grid>

            {/* Height Slider */}
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Height: {height}px</Typography>
              <Slider
                value={height}
                onChange={(_, newValue) => setHeight(newValue as number)}
                min={400}
                max={800}
                step={50}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Main Heatmap */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Cryptocurrency Market Heatmap
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Real-time cryptocurrency market data visualization showing market cap and performance
          </Typography>
          
          <Box sx={{ mt: 2 }}>
            <CryptoHeatmap
              width="100%"
              height={height}
              exchange={exchange}
              changeMode={changeMode}
              theme={theme}
              hasTopBar={hasTopBar}
              isTransparent={isTransparent}
              symbolsGroups="crypto"
              dataSource="Crypto"
              locale="en"
              valuesTracking="1"
              noTimeScale={false}
            />
          </Box>
        </CardContent>
      </Card>

      <Divider sx={{ my: 4 }} />

      {/* Multiple Heatmaps Example */}
      <Typography variant="h5" gutterBottom>
        Multiple Heatmap Views
      </Typography>
      
      <Grid container spacing={3}>
        {/* Daily Performance */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Daily Performance
              </Typography>
              <CryptoHeatmap
                width="100%"
                height={350}
                exchange="BINANCE"
                changeMode="Perf%D"
                theme={theme}
                hasTopBar={false}
                symbolsGroups="crypto"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Weekly Performance */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Weekly Performance
              </Typography>
              <CryptoHeatmap
                width="100%"
                height={350}
                exchange="BINANCE"
                changeMode="Perf%W"
                theme={theme}
                hasTopBar={false}
                symbolsGroups="crypto"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Monthly Performance */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Monthly Performance
              </Typography>
              <CryptoHeatmap
                width="100%"
                height={350}
                exchange="BINANCE"
                changeMode="Perf%M"
                theme={theme}
                hasTopBar={false}
                symbolsGroups="crypto"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Yearly Performance */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Yearly Performance
              </Typography>
              <CryptoHeatmap
                width="100%"
                height={350}
                exchange="BINANCE"
                changeMode="Perf%Y"
                theme={theme}
                hasTopBar={false}
                symbolsGroups="crypto"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Usage Information */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Usage Information
          </Typography>
          <Typography variant="body2" paragraph>
            The CryptoHeatmap component provides a comprehensive view of the cryptocurrency market
            with the following features:
          </Typography>
          <Box component="ul" sx={{ pl: 2 }}>
            <Typography component="li" variant="body2">
              Real-time market data from TradingView
            </Typography>
            <Typography component="li" variant="body2">
              Multiple performance metrics (daily, weekly, monthly, yearly)
            </Typography>
            <Typography component="li" variant="body2">
              Support for different exchanges
            </Typography>
            <Typography component="li" variant="body2">
              Light and dark theme support
            </Typography>
            <Typography component="li" variant="body2">
              Responsive design with configurable dimensions
            </Typography>
            <Typography component="li" variant="body2">
              Loading states and error handling
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default HeatmapDemo;
