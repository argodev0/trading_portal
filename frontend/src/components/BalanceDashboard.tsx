import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Button,
  CircularProgress,
  Alert,
  RefreshIcon
} from '@mui/material';
import { Refresh as RefreshIconMUI } from '@mui/icons-material';
import BalanceCard from '../components/BalanceCard';
import useFetchBalances from '../hooks/useFetchBalances';

interface BalanceDashboardProps {
  authToken?: string;
  refreshInterval?: number;
  autoRefresh?: boolean;
}

/**
 * Dashboard component that uses the useFetchBalances hook to display balance cards
 */
const BalanceDashboard: React.FC<BalanceDashboardProps> = ({
  authToken,
  refreshInterval = 30000, // 30 seconds default
  autoRefresh = true
}) => {
  // Use the custom hook to fetch balances
  const { data, loading, error, refetch } = useFetchBalances({
    authToken,
    autoFetch: true,
    refreshInterval: autoRefresh ? refreshInterval : undefined
  });

  // Group balances by exchange if the data includes exchange information
  const groupBalancesByExchange = () => {
    if (!data) return {};
    
    return data.reduce((acc, balance) => {
      const exchangeName = balance.exchangeName || 'Unknown Exchange';
      const walletType = balance.walletType || 'Spot';
      const key = `${exchangeName}-${walletType}`;
      
      if (!acc[key]) {
        acc[key] = {
          exchangeName,
          walletType,
          balances: []
        };
      }
      
      acc[key].balances.push({
        asset: balance.asset,
        value: balance.value
      });
      
      return acc;
    }, {} as Record<string, { exchangeName: string; walletType: string; balances: Array<{ asset: string; value: number | string }> }>);
  };

  const groupedBalances = groupBalancesByExchange();

  // Loading state
  if (loading && !data) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="200px"
        flexDirection="column"
        gap={2}
      >
        <CircularProgress size={40} />
        <Typography variant="body2" color="text.secondary">
          Loading balances...
        </Typography>
      </Box>
    );
  }

  // Error state
  if (error && !data) {
    return (
      <Box sx={{ mb: 3 }}>
        <Alert 
          severity="error" 
          action={
            <Button 
              color="inherit" 
              size="small" 
              onClick={refetch}
              startIcon={<RefreshIconMUI />}
            >
              Retry
            </Button>
          }
        >
          <Typography variant="body2">
            <strong>Failed to load balances:</strong> {error}
          </Typography>
        </Alert>
      </Box>
    );
  }

  // Empty state
  if (!data || data.length === 0) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="200px"
        flexDirection="column"
        gap={2}
      >
        <Typography variant="h6" color="text.secondary">
          No balances found
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Connect your exchange accounts to view balances
        </Typography>
        <Button 
          variant="outlined" 
          onClick={refetch}
          startIcon={<RefreshIconMUI />}
        >
          Refresh
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header with refresh button */}
      <Box 
        display="flex" 
        justifyContent="space-between" 
        alignItems="center" 
        mb={3}
      >
        <Typography variant="h4" component="h1">
          Account Balances
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          {loading && (
            <CircularProgress size={20} />
          )}
          <Button
            variant="outlined"
            onClick={refetch}
            disabled={loading}
            startIcon={<RefreshIconMUI />}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Error alert if there's an error but we still have data */}
      {error && data && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>Warning:</strong> {error}
          </Typography>
        </Alert>
      )}

      {/* Auto-refresh indicator */}
      {autoRefresh && (
        <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
          Auto-refreshing every {refreshInterval / 1000} seconds
        </Typography>
      )}

      {/* Balance cards */}
      <Grid container spacing={3}>
        {Object.entries(groupedBalances).map(([key, group]) => (
          <Grid item xs={12} sm={6} md={4} key={key}>
            <BalanceCard
              exchangeName={group.exchangeName}
              walletType={group.walletType}
              balanceData={group.balances}
            />
          </Grid>
        ))}

        {/* Fallback: if data doesn't have exchange grouping, show a single card */}
        {Object.keys(groupedBalances).length === 0 && data && (
          <Grid item xs={12} sm={6} md={4}>
            <BalanceCard
              exchangeName="Trading Account"
              walletType="Portfolio"
              balanceData={data.map(item => ({
                asset: item.asset,
                value: item.value
              }))}
            />
          </Grid>
        )}
      </Grid>

      {/* Summary info */}
      <Box mt={4}>
        <Typography variant="body2" color="text.secondary">
          Showing {data.length} asset{data.length !== 1 ? 's' : ''} across{' '}
          {Object.keys(groupedBalances).length || 1} account{Object.keys(groupedBalances).length !== 1 ? 's' : ''}
        </Typography>
      </Box>
    </Box>
  );
};

export default BalanceDashboard;
