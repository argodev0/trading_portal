import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Skeleton,
} from '@mui/material';
import {
  Add,
  Refresh,
  Sync,
} from '@mui/icons-material';
import { useConnectionStatus } from '../hooks/useApiData';
import useFetchBalances from '../hooks/useFetchBalances';
import ConnectionStatusComponent from '../components/ConnectionStatusComponent';
import { connectionStatusService, ConnectionStatusState } from '../services/connectionStatusService';
import { useBalanceWebSocket } from '../hooks/useBalanceWebSocket';

const DashboardView: React.FC = () => {
  const authToken = localStorage.getItem('authToken') || '';
  
  // Real-time balances via WebSocket
  const { balances: wsBalances, connected: wsConnected, error: wsError, refreshBalances: wsRefresh } = useBalanceWebSocket(authToken);

  // Fallback API balances
  const { 
    data: balanceData, 
    loading: balancesLoading, 
    error: balancesError, 
    refetch: refreshBalances 
  } = useFetchBalances({
    authToken,
    autoFetch: true,
    refreshInterval: 30000
  });
  
  const [exchangeConnectionStatus, setExchangeConnectionStatus] = useState<ConnectionStatusState | null>(null);
  const [eventLogs, setEventLogs] = useState<Array<{
    timestamp: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success';
  }>>([]);

  // Use WebSocket balances if available, otherwise fallback to API data
  const liveBalances = wsBalances && wsBalances.length > 0 ? wsBalances : balanceData;

  // Group balances by exchange and wallet type, ensuring all 6 cards are shown
  const groupedBalances = React.useMemo(() => {
    const exchanges = ['Binance', 'KuCoin'];
    const walletTypes = ['Spot', 'Future', 'Funding'];
    const grouped: { [key: string]: any } = {};
    
    // Initialize all 6 cards first
    exchanges.forEach(exchange => {
      walletTypes.forEach(walletType => {
        const key = `${exchange}-${walletType}`;
        grouped[key] = {
          exchange,
          walletType,
          balances: [],
          totalValue: 0
        };
      });
    });
    
    // Fill with real data if available
    if (liveBalances && liveBalances.length > 0) {
      liveBalances.forEach(balance => {
        const key = `${balance.exchangeName}-${balance.walletType}`;
        if (grouped[key]) {
          grouped[key].balances.push(balance);
          grouped[key].totalValue += (Number(balance.value) || 0);
        }
      });
    }
    
    return grouped;
  }, [liveBalances]);

  // Calculate total portfolio value
  const totalPortfolioValue = React.useMemo(() => {
    if (!balanceData || balanceData.length === 0) return 0;
    return balanceData.reduce((total, balance) => total + (Number(balance.value) || 0), 0);
  }, [balanceData]);

  useEffect(() => {
    // Subscribe to connection status updates
    const unsubscribe = connectionStatusService.subscribe((status) => {
      setExchangeConnectionStatus(status);
      
      // Add event logs for connection status changes
      const timestamp = new Date().toLocaleTimeString();
      const newLogs: typeof eventLogs = [];
      
      if (status.binance.status === 'connected') {
        newLogs.push({
          timestamp,
          message: `Binance API connected (${status.binance.latency}ms)`,
          type: 'success'
        });
      } else if (status.binance.status === 'error') {
        newLogs.push({
          timestamp,
          message: `Binance API connection failed: ${status.binance.message}`,
          type: 'error'
        });
      }
      
      if (status.kucoin.status === 'connected') {
        newLogs.push({
          timestamp,
          message: `KuCoin API connected (${status.kucoin.latency}ms)`,
          type: 'success'
        });
      } else if (status.kucoin.status === 'error') {
        newLogs.push({
          timestamp,
          message: `KuCoin API connection failed: ${status.kucoin.message}`,
          type: 'error'
        });
      }
      
      if (newLogs.length > 0) {
        setEventLogs(prevLogs => [...newLogs, ...prevLogs].slice(0, 10)); // Keep only last 10 logs
      }
    });

    // Initial event log
    setEventLogs([
      {
        timestamp: new Date().toLocaleTimeString(),
        message: 'Dashboard initialized',
        type: 'info'
      },
      {
        timestamp: new Date(Date.now() - 5000).toLocaleTimeString(),
        message: 'Starting exchange connection monitoring',
        type: 'info'
      }
    ]);

    return () => unsubscribe();
  }, []);
  
  const { 
    isConnected, 
    connectionStatus 
  } = useConnectionStatus();

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
          <Typography variant="h4" sx={{ color: 'text.primary', fontWeight: 600 }}>
            Dashboard
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary', mt: 1 }}>
            Total Portfolio Value: ${totalPortfolioValue.toLocaleString()}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip 
            icon={<Box sx={{ 
              width: 8, 
              height: 8, 
              bgcolor: isConnected ? 'success.main' : 'warning.main', 
              borderRadius: '50%' 
            }} />}
            label={connectionStatus}
            variant="outlined"
            sx={{ 
              color: isConnected ? 'success.main' : 'warning.main',
              borderColor: isConnected ? 'success.main' : 'warning.main',
              '& .MuiChip-icon': { 
                color: isConnected ? 'success.main' : 'warning.main' 
              }
            }}
          />
          <Button
            variant="contained"
            startIcon={<Add />}
            sx={{
              bgcolor: 'success.main',
              color: 'black',
              fontWeight: 600,
              '&:hover': {
                bgcolor: 'success.dark',
              }
            }}
          >
            Create Bot
          </Button>
        </Box>
      </Box>

      {/* Connection Status */}
      <ConnectionStatusComponent />

      {/* Loading State */}
      {balancesLoading && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} md={6} lg={4} key={i}>
              <Card sx={{ height: '350px' }}>
                <CardContent sx={{ p: 3 }}>
                  <Skeleton variant="text" width="60%" height={32} />
                  <Skeleton variant="rectangular" width={80} height={24} sx={{ mt: 1 }} />
                  <Skeleton variant="text" width="40%" height={48} sx={{ mt: 2 }} />
                  <Skeleton variant="rectangular" width="100%" height={150} sx={{ mt: 2 }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Error State */}
      {balancesError && (
        <Alert 
          severity="error" 
          sx={{ mb: 4 }}
          action={
            <Button color="inherit" size="small" onClick={refreshBalances}>
              Retry
            </Button>
          }
        >
          Failed to load balances: {balancesError}
        </Alert>
      )}

      {/* Exchange Account Cards - Always show all 6 cards */}
      {!balancesLoading && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {Object.entries(groupedBalances).map(([key, account]) => (
            <Grid item xs={12} md={6} lg={4} key={key}>
              <Card sx={{ 
                height: '100%',
                bgcolor: '#1e293b', // Dark blue-gray background
                border: '1px solid #334155',
                borderRadius: 2,
                minHeight: '280px'
              }}>
                <CardContent sx={{ p: 3 }}>
                  {/* Card Header */}
                  <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'flex-start',
                    mb: 3
                  }}>
                    <Box>
                      <Typography variant="h6" sx={{ 
                        color: '#ffffff', 
                        fontWeight: 500,
                        fontSize: '1.25rem',
                        mb: 1
                      }}>
                        {account.exchange} - {account.walletType}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ 
                        width: 8, 
                        height: 8, 
                        bgcolor: '#22c55e', // Green dot
                        borderRadius: '50%' 
                      }} />
                      <Typography variant="body2" sx={{ 
                        color: '#22c55e',
                        fontSize: '0.875rem',
                        fontWeight: 500
                      }}>
                        Active
                      </Typography>
                    </Box>
                  </Box>

                  {/* Total Value */}
                  <Box sx={{ mb: 4 }}>
                    <Typography variant="h3" sx={{ 
                      color: '#ffffff',
                      fontWeight: 700,
                      fontSize: '3rem',
                      lineHeight: 1,
                      mb: 1
                    }}>
                      ${account.totalValue.toFixed(2)}
                    </Typography>
                    <Typography variant="body2" sx={{ 
                      color: '#64748b',
                      fontSize: '1rem'
                    }}>
                      Total Value
                    </Typography>
                  </Box>

                  {/* Assets Table Header */}
                  <Box sx={{ mb: 2 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={4}>
                        <Typography variant="body2" sx={{ 
                          color: '#64748b', 
                          fontWeight: 500,
                          fontSize: '0.875rem'
                        }}>
                          Asset
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" sx={{ 
                          color: '#64748b', 
                          fontWeight: 500,
                          fontSize: '0.875rem',
                          textAlign: 'center'
                        }}>
                          Total
                        </Typography>
                      </Grid>
                      <Grid item xs={4}>
                        <Typography variant="body2" sx={{ 
                          color: '#64748b', 
                          fontWeight: 500,
                          fontSize: '0.875rem',
                          textAlign: 'right'
                        }}>
                          Value (USD)
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>

                  {/* Assets List */}
                  <Box>
                    {account.balances.length > 0 ? (
                      account.balances
                        .filter((balance: any) => balance.total > 0)
                        .map((balance: any, index: number) => (
                        <Box key={index} sx={{ mb: 1.5 }}>
                          <Grid container spacing={2} alignItems="center">
                            <Grid item xs={4}>
                              <Typography sx={{ 
                                color: '#ffffff',
                                fontWeight: 600,
                                fontSize: '1rem'
                              }}>
                                {balance.symbol}
                              </Typography>
                            </Grid>
                            <Grid item xs={4}>
                              <Typography sx={{ 
                                color: '#ffffff',
                                fontSize: '1rem',
                                textAlign: 'center'
                              }}>
                                {balance.total.toFixed(5)}
                              </Typography>
                            </Grid>
                            <Grid item xs={4}>
                              <Typography sx={{ 
                                color: '#22c55e',
                                fontWeight: 600,
                                fontSize: '1rem',
                                textAlign: 'right'
                              }}>
                                ${(Number(balance.value) || 0).toFixed(2)}
                              </Typography>
                            </Grid>
                          </Grid>
                        </Box>
                      ))
                    ) : (
                      <Box sx={{ 
                        textAlign: 'center', 
                        py: 3,
                        color: '#64748b'
                      }}>
                        <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                          No assets found
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Event Log */}
      <Card>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            mb: 2 
          }}>
            <Typography variant="h6" sx={{ 
              color: 'text.primary', 
              fontWeight: 600 
            }}>
              Event Log
            </Typography>
            <IconButton size="small" sx={{ color: 'text.secondary' }}>
              <Refresh fontSize="small" />
            </IconButton>
          </Box>

          <Box sx={{ 
            bgcolor: '#0A0E13',
            border: '1px solid #2D3748',
            borderRadius: 1,
            p: 2,
            fontFamily: 'monospace',
            maxHeight: '300px',
            overflowY: 'auto'
          }}>
            {eventLogs.length === 0 ? (
              <Typography
                variant="body2"
                sx={{
                  color: '#8B949E',
                  fontSize: '0.8rem',
                  fontStyle: 'italic'
                }}
              >
                No events yet...
              </Typography>
            ) : (
              eventLogs.map((log, index) => {
                const getLogColor = (type: string) => {
                  switch (type) {
                    case 'success': return '#26DE81';
                    case 'error': return '#FF6B6B';
                    case 'warning': return '#FFD93D';
                    case 'info': 
                    default: return '#6B73FF';
                  }
                };

                const getLogPrefix = (type: string) => {
                  switch (type) {
                    case 'success': return '[SUCCESS]';
                    case 'error': return '[ERROR]';
                    case 'warning': return '[WARNING]';
                    case 'info':
                    default: return '[INFO]';
                  }
                };

                return (
                  <Typography
                    key={index}
                    variant="body2"
                    sx={{
                      fontSize: '0.8rem',
                      lineHeight: 1.5,
                      mb: 0.5
                    }}
                  >
                    <span style={{ color: '#8B949E' }}>{log.timestamp}</span>{' '}
                    <span style={{ color: getLogColor(log.type) }}>{getLogPrefix(log.type)}</span>{' '}
                    <span style={{ color: '#FFFFFF' }}>{log.message.replace(/^\[.*?\]\s*/, '')}</span>
                  </Typography>
                );
              })
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardView;
