import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  Box,
  Divider,
  Chip
} from '@mui/material';
import { styled } from '@mui/material/styles';

// Type definitions for component props
interface BalanceData {
  asset: string;
  value: number | string;
}

interface BalanceCardProps {
  exchangeName: string;
  walletType: string;
  balanceData: BalanceData[];
}

// Styled components for enhanced UI
const StyledCard = styled(Card)(({ theme }) => ({
  minWidth: 300,
  margin: theme.spacing(1),
  backgroundColor: theme.palette.background.paper,
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: '12px',
  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  '&:hover': {
    boxShadow: '0 8px 12px -1px rgba(0, 0, 0, 0.2), 0 4px 8px -1px rgba(0, 0, 0, 0.1)',
    transform: 'translateY(-2px)',
    transition: 'all 0.3s ease-in-out',
  },
}));

const HeaderBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: theme.spacing(2),
}));

const BalanceItem = styled(ListItem)(({ theme }) => ({
  paddingLeft: 0,
  paddingRight: 0,
  '&:not(:last-child)': {
    borderBottom: `1px solid ${theme.palette.divider}`,
  },
}));

const AssetText = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  color: theme.palette.text.primary,
}));

const ValueText = styled(Typography)(({ theme }) => ({
  fontWeight: 500,
  color: theme.palette.text.secondary,
  textAlign: 'right',
}));

const BalanceCard: React.FC<BalanceCardProps> = ({
  exchangeName,
  walletType,
  balanceData
}) => {
  // Format balance value for display
  const formatBalance = (value: number | string): string => {
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    
    if (isNaN(numValue)) return '0.00';
    
    // Format with appropriate decimal places
    if (numValue >= 1) {
      return numValue.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      });
    } else {
      return numValue.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 8
      });
    }
  };

  // Get wallet type color for the chip
  const getWalletTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'spot':
        return { bgcolor: 'primary.main', color: 'black' };
      case 'futures':
        return { bgcolor: 'warning.main', color: 'black' };
      case 'margin':
        return { bgcolor: 'info.main', color: 'black' };
      case 'savings':
        return { bgcolor: 'success.main', color: 'black' };
      default:
        return { bgcolor: 'secondary.main', color: 'white' };
    }
  };

  return (
    <StyledCard>
      <CardContent>
        {/* Header with exchange name and wallet type */}
        <HeaderBox>
          <Typography variant="h6" component="h2" sx={{ color: 'text.primary', fontWeight: 600 }}>
            {exchangeName}
          </Typography>
          <Chip 
            label={walletType}
            size="small"
            sx={{
              ...getWalletTypeColor(walletType),
              fontWeight: 600,
              fontSize: '0.75rem'
            }}
          />
        </HeaderBox>

        <Divider sx={{ mb: 2 }} />

        {/* Balance list */}
        {balanceData.length > 0 ? (
          <List dense disablePadding>
            {balanceData.map((balance, index) => (
              <BalanceItem key={`${balance.asset}-${index}`}>
                <ListItemText
                  primary={
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <AssetText variant="body1">
                        {balance.asset.toUpperCase()}
                      </AssetText>
                      <ValueText variant="body1">
                        {formatBalance(balance.value)}
                      </ValueText>
                    </Box>
                  }
                />
              </BalanceItem>
            ))}
          </List>
        ) : (
          <Box 
            display="flex" 
            justifyContent="center" 
            alignItems="center" 
            minHeight={100}
          >
            <Typography 
              variant="body2" 
              color="text.secondary"
              style={{ fontStyle: 'italic' }}
            >
              No balance data available
            </Typography>
          </Box>
        )}

        {/* Summary info */}
        {balanceData.length > 0 && (
          <>
            <Divider sx={{ mt: 2, mb: 1 }} />
            <Typography 
              variant="caption" 
              color="text.secondary"
              display="block"
              textAlign="center"
            >
              {balanceData.length} asset{balanceData.length !== 1 ? 's' : ''} shown
            </Typography>
          </>
        )}
      </CardContent>
    </StyledCard>
  );
};

export default BalanceCard;
