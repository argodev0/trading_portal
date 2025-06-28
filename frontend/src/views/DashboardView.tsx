import React from 'react';
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
  LinearProgress,
  CircularProgress,
  Alert,
  Skeleton,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  MoreVert,
  Add,
  Refresh,
  Sync,
} from '@mui/icons-material';
import { useExchangeAccounts, useConnectionStatus, usePortfolioSummary } from '../hooks/useApiData';

const DashboardView: React.FC = () => {
  const { 
    accounts, 
    loading: accountsLoading, 
    error: accountsError, 
    refreshAccounts,
    syncAccount 
  } = useExchangeAccounts();
  
  const { 
    portfolio, 
    loading: portfolioLoading 
  } = usePortfolioSummary();
  
  const { 
    isConnected, 
    connectionStatus 
  } = useConnectionStatus();

  // Event logs (this could be enhanced with real backend events)
  const eventLogs = [
    {
      timestamp: new Date().toLocaleTimeString(),
      message: '[INFO] Dashboard rendered.',
      type: 'info'
    },
    {
      timestamp: new Date(Date.now() - 30000).toLocaleTimeString(),
      message: `[INFO] Connected to ${accounts.length} exchange accounts.`,
      type: 'info'
    }
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
          <Typography variant="h4" sx={{ color: 'text.primary', fontWeight: 600 }}>
            Dashboard
          </Typography>
          {portfolio && (
            <Typography variant="body1" sx={{ color: 'text.secondary', mt: 1 }}>
              Total Portfolio Value: ${portfolio.total_value_usd.toLocaleString()}
            </Typography>
          )}
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

      {/* Loading State */}
      {accountsLoading && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {[1, 2, 3].map((i) => (
            <Grid item xs={12} md={6} lg={4} key={i}>
              <Card sx={{ height: '300px' }}>
                <CardContent sx={{ p: 3 }}>
                  <Skeleton variant="text" width="60%" height={32} />
                  <Skeleton variant="rectangular" width={80} height={24} sx={{ mt: 1 }} />
                  <Skeleton variant="text" width="40%" height={48} sx={{ mt: 2 }} />
                  <Skeleton variant="rectangular" width="100%" height={100} sx={{ mt: 2 }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Error State */}
      {accountsError && (
        <Alert 
          severity="error" 
          sx={{ mb: 4 }}
          action={
            <Button color="inherit" size="small" onClick={refreshAccounts}>
              Retry
            </Button>
          }
        >
          Failed to load exchange accounts: {accountsError}
        </Alert>
      )}

      {/* Exchange Account Cards */}
      {!accountsLoading && !accountsError && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {accounts.length === 0 ? (
            <Grid item xs={12}>
              <Card>
                <CardContent sx={{ p: 4, textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: 'text.secondary', mb: 2 }}>
                    No Exchange Accounts Found
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3 }}>
                    Connect your exchange accounts to start trading
                  </Typography>
                  <Button variant="contained" sx={{ bgcolor: 'success.main', color: 'black' }}>
                    Add Exchange Account
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ) : (
            accounts.map((account) => (
              <Grid item xs={12} md={6} lg={4} key={account.id}>
                <Card sx={{ height: '100%' }}>
                  <CardContent sx={{ p: 3 }}>
                    {/* Card Header */}
                    <Box sx={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'flex-start',
                      mb: 2 
                    }}>
                      <Box>
                        <Typography variant="h6" sx={{ 
                          color: 'text.primary', 
                          fontWeight: 600,
                          fontSize: '1rem',
                          mb: 0.5
                        }}>
                          {account.name}
                        </Typography>
                        <Chip 
                          label={account.status}
                          size="small"
                          sx={{
                            bgcolor: account.status === 'active' ? 'success.main' : 'warning.main',
                            color: 'black',
                            fontWeight: 600,
                            fontSize: '0.75rem'
                          }}
                        />
                      </Box>
                      <IconButton 
                        size="small" 
                        sx={{ color: 'text.secondary' }}
                        onClick={() => syncAccount(account.id)}
                      >
                        <Sync fontSize="small" />
                      </IconButton>
                    </Box>

                    {/* Total Value */}
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h4" sx={{ 
                        color: 'text.primary',
                        fontWeight: 700,
                        fontSize: '2rem',
                        mb: 0.5
                      }}>
                        ${account.total_value_usd.toFixed(2)}
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                        Total Value
                      </Typography>
                    </Box>

                    {/* Assets Table */}
                    {account.balances.length > 0 ? (
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell sx={{ 
                                color: 'text.secondary', 
                                fontWeight: 600,
                                fontSize: '0.75rem',
                                border: 'none',
                                pb: 1
                              }}>
                                Asset
                              </TableCell>
                              <TableCell align="right" sx={{ 
                                color: 'text.secondary', 
                                fontWeight: 600,
                                fontSize: '0.75rem',
                                border: 'none',
                                pb: 1
                              }}>
                                Total
                              </TableCell>
                              <TableCell align="right" sx={{ 
                                color: 'text.secondary', 
                                fontWeight: 600,
                                fontSize: '0.75rem',
                                border: 'none',
                                pb: 1
                              }}>
                                Value (USD)
                              </TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {account.balances.filter(balance => balance.total > 0).map((balance, index) => (
                              <TableRow key={index}>
                                <TableCell sx={{ 
                                  color: 'text.primary',
                                  fontWeight: 600,
                                  border: 'none',
                                  py: 1
                                }}>
                                  {balance.asset}
                                </TableCell>
                                <TableCell align="right" sx={{ 
                                  color: 'text.primary',
                                  border: 'none',
                                  py: 1
                                }}>
                                  {balance.total.toFixed(5)}
                                </TableCell>
                                <TableCell align="right" sx={{ 
                                  color: 'success.main',
                                  fontWeight: 600,
                                  border: 'none',
                                  py: 1
                                }}>
                                  ${balance.value_usd.toFixed(2)}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    ) : (
                      <Box sx={{ 
                        textAlign: 'center', 
                        py: 2,
                        color: 'text.secondary'
                      }}>
                        <Typography variant="body2">
                          No assets found.
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))
          )}
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
            fontFamily: 'monospace'
          }}>
            {eventLogs.map((log, index) => (
              <Typography
                key={index}
                variant="body2"
                sx={{
                  color: log.type === 'info' ? '#6B73FF' : 'text.primary',
                  fontSize: '0.8rem',
                  lineHeight: 1.5
                }}
              >
                <span style={{ color: '#8B949E' }}>{log.timestamp}</span>{' '}
                <span style={{ color: '#6B73FF' }}>[INFO]</span>
                <span style={{ color: '#FFFFFF' }}>Dashboard rendered.</span>
              </Typography>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardView;
