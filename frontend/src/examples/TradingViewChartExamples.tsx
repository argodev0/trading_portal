// Real-world usage examples for TradingViewChart component

import React, { useState, useEffect } from 'react';
import TradingViewChart from '../components/TradingViewChart';
import { Box, Grid, Paper, Typography } from '@mui/material';

// Example 1: Basic chart with default settings
const BasicChartExample = () => {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Basic BTC/USDT Chart
      </Typography>
      <TradingViewChart />
    </Paper>
  );
};

// Example 2: Customized chart with different symbol and styling
const CustomizedChartExample = () => {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        ETH/USDT Dark Theme Chart
      </Typography>
      <TradingViewChart
        symbol="ETH/USDT"
        interval="4h"
        theme="dark"
        width={600}
        height={350}
      />
    </Paper>
  );
};

// Example 3: Multiple charts dashboard
const MultiChartDashboard = () => {
  const symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT'];
  
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Multi-Symbol Dashboard
      </Typography>
      <Grid container spacing={2}>
        {symbols.map((symbol) => (
          <Grid item xs={12} md={6} key={symbol}>
            <Paper sx={{ p: 1 }}>
              <Typography variant="subtitle1" gutterBottom>
                {symbol}
              </Typography>
              <TradingViewChart
                symbol={symbol}
                interval="1h"
                width={400}
                height={250}
              />
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

// Example 4: Chart with real API integration
interface ApiChartProps {
  apiEndpoint?: string;
  authToken?: string;
}

const ApiIntegratedChart: React.FC<ApiChartProps> = ({ 
  apiEndpoint = '/api/chart-data',
  authToken 
}) => {
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [interval, setInterval] = useState('1h');

  // Example of how you might integrate with a real API
  const fetchRealChartData = async (symbol: string, interval: string) => {
    try {
      const response = await fetch(`${apiEndpoint}?symbol=${symbol}&interval=${interval}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch chart data');
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching chart data:', error);
      throw error;
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        API-Integrated Chart
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        This chart would fetch real data from: {apiEndpoint}
      </Typography>
      <TradingViewChart
        symbol={symbol}
        interval={interval}
        width={800}
        height={400}
      />
    </Paper>
  );
};

// Example 5: Responsive chart that adapts to container
const ResponsiveChartExample = () => {
  const [containerWidth, setContainerWidth] = useState(800);

  useEffect(() => {
    const handleResize = () => {
      // In a real app, you'd get the actual container width
      const newWidth = Math.min(window.innerWidth - 100, 1000);
      setContainerWidth(newWidth);
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Set initial width

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Responsive Chart (Width: {containerWidth}px)
      </Typography>
      <TradingViewChart
        symbol="BTC/USDT"
        interval="1h"
        width={containerWidth}
        height={400}
      />
    </Paper>
  );
};

// Example 6: Chart with custom theme based on user preference
const ThemedChartExample = () => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  // This could come from a theme context or user preferences
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setIsDarkMode(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setIsDarkMode(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        System Theme Chart ({isDarkMode ? 'Dark' : 'Light'})
      </Typography>
      <TradingViewChart
        symbol="BTC/USDT"
        interval="1h"
        theme={isDarkMode ? 'dark' : 'light'}
        width={700}
        height={350}
      />
    </Paper>
  );
};

// Example 7: Chart with error boundary
import { ErrorBoundary } from 'react-error-boundary';

const ErrorFallback = ({ error, resetErrorBoundary }: any) => (
  <Paper sx={{ p: 3, textAlign: 'center' }}>
    <Typography variant="h6" color="error" gutterBottom>
      Chart Error
    </Typography>
    <Typography variant="body2" paragraph>
      {error.message}
    </Typography>
    <button onClick={resetErrorBoundary}>Try Again</button>
  </Paper>
);

const SafeChartExample = () => {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => window.location.reload()}
    >
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Error-Protected Chart
        </Typography>
        <TradingViewChart
          symbol="BTC/USDT"
          interval="1h"
          width={600}
          height={300}
        />
      </Paper>
    </ErrorBoundary>
  );
};

// Example 8: Chart with performance monitoring
const PerformanceMonitoredChart = () => {
  const [renderTime, setRenderTime] = useState<number | null>(null);

  useEffect(() => {
    const startTime = performance.now();
    
    // Simulate chart render completion
    const timer = setTimeout(() => {
      const endTime = performance.now();
      setRenderTime(endTime - startTime);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Performance Monitored Chart
      </Typography>
      {renderTime && (
        <Typography variant="caption" color="text.secondary">
          Render time: {renderTime.toFixed(2)}ms
        </Typography>
      )}
      <TradingViewChart
        symbol="BTC/USDT"
        interval="1h"
        width={600}
        height={300}
      />
    </Paper>
  );
};

// Export all examples
export {
  BasicChartExample,
  CustomizedChartExample,
  MultiChartDashboard,
  ApiIntegratedChart,
  ResponsiveChartExample,
  ThemedChartExample,
  SafeChartExample,
  PerformanceMonitoredChart
};

// Example usage in a main component
const ChartExamplesShowcase = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        TradingViewChart Examples
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <BasicChartExample />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <CustomizedChartExample />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <ThemedChartExample />
        </Grid>
        
        <Grid item xs={12}>
          <ResponsiveChartExample />
        </Grid>
        
        <Grid item xs={12}>
          <MultiChartDashboard />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <ApiIntegratedChart />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <PerformanceMonitoredChart />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ChartExamplesShowcase;
