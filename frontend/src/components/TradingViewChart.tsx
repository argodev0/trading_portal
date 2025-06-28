import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Box, Typography, CircularProgress, Alert, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { tradingViewService } from '../services/tradingViewService';
import { Refresh } from '@mui/icons-material';

// Types for the component
interface TradingViewChartProps {
  symbol?: string;
  interval?: string;
  width?: number | string;
  height?: number | string;
  theme?: 'light' | 'dark';
}

// Styled components
const ChartContainer = styled(Box)(({ theme }) => ({
  position: 'relative',
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  overflow: 'hidden',
}));

const ChartHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  backgroundColor: theme.palette.background.default,
}));

const LoadingOverlay = styled(Box)({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  backgroundColor: 'rgba(0, 0, 0, 0.5)',
  zIndex: 10,
});

const ErrorOverlay = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  zIndex: 10,
  backgroundColor: theme.palette.background.paper,
  padding: theme.spacing(3),
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[5],
  textAlign: 'center',
  maxWidth: 300,
}));

/**
 * TradingView Chart Component using official TradingView widgets
 * 
 * Features:
 * - Official TradingView chart widget integration
 * - Real-time data from TradingView
 * - Responsive design
 * - Loading and error states
 * - Light/dark theme support
 * - Symbol and interval customization
 */
const TradingViewChart: React.FC<TradingViewChartProps> = ({
  symbol = 'BINANCE:BTCUSDT',
  interval = '1H',
  width = '100%',
  height = 400,
  theme = 'dark'
}) => {
  // Refs and state
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const widgetIdRef = useRef<string>(`tv-chart-${Date.now()}-${Math.random()}`);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  // Initialize chart widget
  const initializeChart = useCallback(async () => {
    if (!chartContainerRef.current) return;

    try {
      setLoading(true);
      setError(null);

      // Set container ID
      chartContainerRef.current.id = widgetIdRef.current;

      const chartHeight = typeof height === 'number' ? height - 60 : 400;

      // Create TradingView chart widget
      await tradingViewService.createChartWidget({
        container_id: widgetIdRef.current,
        width,
        height: chartHeight,
        symbol,
        interval,
        theme,
        timezone: 'Etc/UTC',
        style: '1', // Candlestick
        locale: 'en',
        toolbar_bg: theme === 'dark' ? '#1a1a1a' : '#f1f3f6',
        enable_publishing: false,
        allow_symbol_change: true,
        hide_top_toolbar: false,
        hide_legend: false,
        save_image: false,
        hide_volume: false,
      });

      setLoading(false);
    } catch (err) {
      console.error('Failed to initialize TradingView chart:', err);
      setError(err instanceof Error ? err.message : 'Failed to load chart');
      setLoading(false);
    }
  }, [symbol, interval, width, height, theme]);

  // Retry initialization
  const retryInitialization = useCallback(() => {
    setRetryCount(prev => prev + 1);
    initializeChart();
  }, [initializeChart]);

  // Initialize chart on mount and when dependencies change
  useEffect(() => {
    const timer = setTimeout(initializeChart, 100); // Small delay to ensure DOM is ready
    return () => clearTimeout(timer);
  }, [initializeChart]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      tradingViewService.removeWidget(widgetIdRef.current);
    };
  }, []);

  return (
    <ChartContainer sx={{ width, height }}>
      {/* Header */}
      <ChartHeader>
        <Box>
          <Typography variant="h6" sx={{ 
            color: 'text.primary', 
            fontWeight: 600,
            fontSize: '1rem'
          }}>
            {symbol.replace('BINANCE:', '').replace(':', '/')}
          </Typography>
          <Typography variant="body2" sx={{ 
            color: 'text.secondary',
            fontSize: '0.875rem'
          }}>
            {interval} Chart
          </Typography>
        </Box>
        <Button
          size="small"
          onClick={retryInitialization}
          startIcon={<Refresh />}
          sx={{
            color: 'text.secondary',
            '&:hover': {
              backgroundColor: 'action.hover',
            }
          }}
        >
          Refresh
        </Button>
      </ChartHeader>

      {/* Chart Container */}
      <Box sx={{ 
        position: 'relative', 
        height: typeof height === 'number' ? height - 60 : 'calc(100% - 60px)'
      }}>
        <div ref={chartContainerRef} style={{ width: '100%', height: '100%' }} />

        {/* Loading Overlay */}
        {loading && (
          <LoadingOverlay>
            <Box sx={{ textAlign: 'center', color: 'white' }}>
              <CircularProgress size={40} sx={{ color: 'success.main', mb: 2 }} />
              <Typography variant="body2">
                Loading TradingView Chart...
              </Typography>
            </Box>
          </LoadingOverlay>
        )}

        {/* Error Overlay */}
        {error && !loading && (
          <ErrorOverlay>
            <Alert 
              severity="error" 
              sx={{ mb: 2 }}
              action={
                <Button 
                  size="small" 
                  onClick={retryInitialization}
                  sx={{ color: 'error.main' }}
                >
                  Retry
                </Button>
              }
            >
              {error}
            </Alert>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Unable to load chart data. Please check your connection and try again.
            </Typography>
            {retryCount > 0 && (
              <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
                Retry attempts: {retryCount}
              </Typography>
            )}
          </ErrorOverlay>
        )}
      </Box>
    </ChartContainer>
  );
};

export default TradingViewChart;
