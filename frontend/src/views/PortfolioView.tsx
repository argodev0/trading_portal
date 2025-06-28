import React from 'react';
import { Box, Typography } from '@mui/material';
import BalanceDashboard from '../components/BalanceDashboard';

const PortfolioView: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Portfolio
      </Typography>
      <BalanceDashboard />
    </Box>
  );
};

export default PortfolioView;
