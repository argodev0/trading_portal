import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  Stack,
  Divider
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as ConnectedIcon,
  Error as ErrorIcon,
  HourglassEmpty as CheckingIcon,
  Cancel as DisconnectedIcon
} from '@mui/icons-material';
import { 
  connectionStatusService, 
  ConnectionStatusState, 
  ExchangeConnectionStatus 
} from '../services/connectionStatusService';
import { environment } from '../config/environment';

const ConnectionStatusComponent: React.FC = () => {
  const [status, setStatus] = useState<ConnectionStatusState | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const unsubscribe = connectionStatusService.subscribe(setStatus);
    connectionStatusService.startMonitoring();

    return () => {
      unsubscribe();
      connectionStatusService.stopMonitoring();
    };
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await connectionStatusService.forceCheck();
    } finally {
      setIsRefreshing(false);
    }
  };

  const getStatusIcon = (exchangeStatus: ExchangeConnectionStatus) => {
    switch (exchangeStatus.status) {
      case 'connected':
        return <ConnectedIcon sx={{ color: 'success.main', fontSize: 16 }} />;
      case 'error':
        return <ErrorIcon sx={{ color: 'error.main', fontSize: 16 }} />;
      case 'checking':
        return <CheckingIcon sx={{ color: 'warning.main', fontSize: 16 }} />;
      case 'disconnected':
      default:
        return <DisconnectedIcon sx={{ color: 'grey.500', fontSize: 16 }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'success';
      case 'error':
        return 'error';
      case 'checking':
        return 'warning';
      case 'disconnected':
      default:
        return 'default';
    }
  };

  const formatLastChecked = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const seconds = Math.floor(diff / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    return `${Math.floor(seconds / 3600)}h ago`;
  };

  if (!status) {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="h6">Exchange Connections</Typography>
            <LinearProgress sx={{ flexGrow: 1, height: 4, borderRadius: 2 }} />
          </Box>
          <Typography variant="body2" color="text.secondary">
            Loading connection status...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Exchange Connections</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Tooltip title="Refresh connection status">
              <IconButton 
                size="small" 
                onClick={handleRefresh}
                disabled={isRefreshing}
              >
                <RefreshIcon sx={{ 
                  fontSize: 16,
                  animation: isRefreshing ? 'spin 1s linear infinite' : 'none',
                  '@keyframes spin': {
                    '0%': { transform: 'rotate(0deg)' },
                    '100%': { transform: 'rotate(360deg)' }
                  }
                }} />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Stack spacing={2}>
          {/* Binance Status */}
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              {getStatusIcon(status.binance)}
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                Binance
              </Typography>
              <Chip 
                label={status.binance.status.toUpperCase()} 
                size="small"
                color={getStatusColor(status.binance.status) as any}
                variant="outlined"
              />
              {status.binance.latency && (
                <Typography variant="caption" color="text.secondary">
                  {status.binance.latency}ms
                </Typography>
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              {status.binance.message}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ ml: 3 }}>
              Last checked: {formatLastChecked(status.binance.lastChecked)}
            </Typography>
          </Box>

          <Divider />

          {/* KuCoin Status */}
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              {getStatusIcon(status.kucoin)}
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                KuCoin
              </Typography>
              <Chip 
                label={status.kucoin.status.toUpperCase()} 
                size="small"
                color={getStatusColor(status.kucoin.status) as any}
                variant="outlined"
              />
              {status.kucoin.latency && (
                <Typography variant="caption" color="text.secondary">
                  {status.kucoin.latency}ms
                </Typography>
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ ml: 3 }}>
              {status.kucoin.message}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ ml: 3 }}>
              Last checked: {formatLastChecked(status.kucoin.lastChecked)}
            </Typography>
          </Box>
        </Stack>

        <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            Last updated: {formatLastChecked(status.lastUpdate)} • Real-time API monitoring
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ConnectionStatusComponent;
