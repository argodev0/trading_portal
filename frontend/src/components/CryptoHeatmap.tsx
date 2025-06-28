import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Box, Typography, CircularProgress, Alert, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { tradingViewService } from '../services/tradingViewService';
import { Refresh } from '@mui/icons-material';

// Types for the component
interface CryptoHeatmapProps {
  width?: number | string;
  height?: number | string;
  dataSource?: 'Crypto' | 'CFD';
  exchange?: string;
  symbolsGroups?: string;
  hasTopBar?: boolean;
  isTransparent?: boolean;
  noTimeScale?: boolean;
  valuesTracking?: string;
  changeMode?: 'price-changes' | 'Perf%D' | 'Perf%W' | 'Perf%M' | 'Perf%3M' | 'Perf%6M' | 'Perf%Y' | 'Perf%YTD';
  locale?: string;
  theme?: 'light' | 'dark';
}

// Styled components
const HeatmapContainer = styled(Box)(({ theme }) => ({
  position: 'relative',
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  overflow: 'hidden',
}));

const HeatmapHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.default,
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
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
 * CryptoHeatmap Component using TradingView Crypto Coins Heatmap Widget
 * 
 * Features:
 * - Embeds TradingView's official Crypto Coins Heatmap widget
 * - Dynamic script loading with error handling
 * - Configurable widget properties
 * - Loading and error states
 * - Responsive design
 * - Theme support
 */
const CryptoHeatmap: React.FC<CryptoHeatmapProps> = ({
  width = '100%',
  height = 500,
  dataSource = 'Crypto',
  exchange = 'BINANCE',
  symbolsGroups = 'crypto',
  hasTopBar = true,
  isTransparent = false,
  noTimeScale = false,
  valuesTracking = '1',
  changeMode = 'price-changes',
  locale = 'en',
  theme = 'dark'
}) => {
  // Refs and state
  const heatmapContainerRef = useRef<HTMLDivElement>(null);
  const widgetIdRef = useRef<string>(`tv-heatmap-${Date.now()}-${Math.random()}`);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  // Initialize heatmap widget
  const initializeHeatmap = useCallback(async () => {
    if (!heatmapContainerRef.current) return;

    try {
      setLoading(true);
      setError(null);

      // Set container ID
      heatmapContainerRef.current.id = widgetIdRef.current;

      const heatmapHeight = typeof height === 'number' ? height - 60 : 440;

      // Create TradingView heatmap widget
      await tradingViewService.createHeatmapWidget({
        container_id: widgetIdRef.current,
        width,
        height: heatmapHeight,
        dataSource,
        exchange,
        symbolsGroups,
        blockSize: 'market_cap_basic',
        blockColor: 'change|60',
        locale,
        hasTopBar,
        isTransparent,
        noTimeScale,
        valuesTracking,
        changeMode,
        theme,
      });

      setLoading(false);
    } catch (err) {
      console.error('Failed to initialize TradingView heatmap:', err);
      setError(err instanceof Error ? err.message : 'Failed to load heatmap');
      setLoading(false);
    }
  }, [
    width,
    height,
    dataSource,
    exchange,
    symbolsGroups,
    hasTopBar,
    isTransparent,
    noTimeScale,
    valuesTracking,
    changeMode,
    locale,
    theme
  ]);

  // Retry initialization
  const retryInitialization = useCallback(() => {
    setRetryCount(prev => prev + 1);
    initializeHeatmap();
  }, [initializeHeatmap]);

  // Initialize heatmap on mount and when dependencies change
  useEffect(() => {
    const timer = setTimeout(initializeHeatmap, 100); // Small delay to ensure DOM is ready
    return () => clearTimeout(timer);
  }, [initializeHeatmap]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      tradingViewService.removeWidget(widgetIdRef.current);
    };
  }, []);

  return (
    <HeatmapContainer sx={{ width, height }}>
      {/* Header */}
      <HeatmapHeader>
        <Box>
          <Typography variant="h6" sx={{ 
            color: 'text.primary', 
            fontWeight: 600,
            fontSize: '1rem'
          }}>
            Crypto Market Heatmap
          </Typography>
          <Typography variant="body2" sx={{ 
            color: 'text.secondary',
            fontSize: '0.875rem'
          }}>
            {dataSource} • {exchange}
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
      </HeatmapHeader>

      {/* Heatmap Container */}
      <Box sx={{ 
        position: 'relative', 
        height: typeof height === 'number' ? height - 60 : 'calc(100% - 60px)'
      }}>
        <div ref={heatmapContainerRef} style={{ width: '100%', height: '100%' }} />

        {/* Loading Overlay */}
        {loading && (
          <LoadingOverlay>
            <Box sx={{ textAlign: 'center', color: 'white' }}>
              <CircularProgress size={40} sx={{ color: 'success.main', mb: 2 }} />
              <Typography variant="body2">
                Loading Crypto Heatmap...
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
              Unable to load heatmap data. Please check your connection and try again.
            </Typography>
            {retryCount > 0 && (
              <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
                Retry attempts: {retryCount}
              </Typography>
            )}
          </ErrorOverlay>
        )}
      </Box>
    </HeatmapContainer>
  );
};

export default CryptoHeatmap;
