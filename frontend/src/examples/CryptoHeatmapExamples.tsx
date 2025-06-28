import React from 'react';
import { Box, Typography, Card, CardContent, Divider } from '@mui/material';
import CryptoHeatmap from '../components/CryptoHeatmap';

/**
 * Examples demonstrating different CryptoHeatmap configurations
 */

// Basic usage example
export const BasicHeatmapExample: React.FC = () => (
  <Card>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Basic Crypto Heatmap
      </Typography>
      <CryptoHeatmap />
    </CardContent>
  </Card>
);

// Customized heatmap example
export const CustomizedHeatmapExample: React.FC = () => (
  <Card>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Customized Heatmap - Dark Theme, Weekly Performance
      </Typography>
      <CryptoHeatmap
        width="100%"
        height={400}
        theme="dark"
        changeMode="Perf%W"
        exchange="COINBASE"
        hasTopBar={true}
        isTransparent={false}
      />
    </CardContent>
  </Card>
);

// Compact heatmap example
export const CompactHeatmapExample: React.FC = () => (
  <Card>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Compact Heatmap - No Top Bar
      </Typography>
      <CryptoHeatmap
        width="100%"
        height={300}
        hasTopBar={false}
        changeMode="Perf%D"
        theme="light"
      />
    </CardContent>
  </Card>
);

// Performance comparison example
export const PerformanceComparisonExample: React.FC = () => (
  <Box>
    <Typography variant="h5" gutterBottom>
      Performance Comparison Views
    </Typography>
    
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 2 }}>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Daily Performance
          </Typography>
          <CryptoHeatmap
            width="100%"
            height={250}
            changeMode="Perf%D"
            hasTopBar={false}
            exchange="BINANCE"
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Weekly Performance
          </Typography>
          <CryptoHeatmap
            width="100%"
            height={250}
            changeMode="Perf%W"
            hasTopBar={false}
            exchange="BINANCE"
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Monthly Performance
          </Typography>
          <CryptoHeatmap
            width="100%"
            height={250}
            changeMode="Perf%M"
            hasTopBar={false}
            exchange="BINANCE"
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Yearly Performance
          </Typography>
          <CryptoHeatmap
            width="100%"
            height={250}
            changeMode="Perf%Y"
            hasTopBar={false}
            exchange="BINANCE"
          />
        </CardContent>
      </Card>
    </Box>
  </Box>
);

// Different exchanges example
export const ExchangeComparisonExample: React.FC = () => (
  <Box>
    <Typography variant="h5" gutterBottom>
      Different Exchange Data
    </Typography>
    
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: 2 }}>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Binance
          </Typography>
          <CryptoHeatmap
            width="100%"
            height={300}
            exchange="BINANCE"
            hasTopBar={false}
            changeMode="price-changes"
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Coinbase
          </Typography>
          <CryptoHeatmap
            width="100%"
            height={300}
            exchange="COINBASE"
            hasTopBar={false}
            changeMode="price-changes"
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Kraken
          </Typography>
          <CryptoHeatmap
            width="100%"
            height={300}
            exchange="KRAKEN"
            hasTopBar={false}
            changeMode="price-changes"
          />
        </CardContent>
      </Card>
    </Box>
  </Box>
);

// Full-featured example
export const FullFeaturedHeatmapExample: React.FC = () => (
  <Card>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Full-Featured Heatmap
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Complete heatmap with all features enabled including top bar, 
        custom dimensions, and weekly performance tracking.
      </Typography>
      <CryptoHeatmap
        width="100%"
        height={500}
        dataSource="Crypto"
        exchange="BINANCE"
        symbolsGroups="crypto"
        hasTopBar={true}
        isTransparent={false}
        noTimeScale={false}
        valuesTracking="1"
        changeMode="Perf%W"
        locale="en"
        theme="light"
      />
    </CardContent>
  </Card>
);

// Mobile-optimized example
export const MobileOptimizedHeatmapExample: React.FC = () => (
  <Card>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Mobile-Optimized Heatmap
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Compact design optimized for mobile devices with essential features only.
      </Typography>
      <CryptoHeatmap
        width="100%"
        height={350}
        hasTopBar={false}
        isTransparent={false}
        changeMode="Perf%D"
        theme="light"
        exchange="BINANCE"
      />
    </CardContent>
  </Card>
);

// All examples component
const CryptoHeatmapExamples: React.FC = () => (
  <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
    <Typography variant="h4" gutterBottom>
      CryptoHeatmap Component Examples
    </Typography>
    
    <Typography variant="body1" color="text.secondary" paragraph>
      Various configurations and use cases for the CryptoHeatmap component.
    </Typography>

    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <BasicHeatmapExample />
      <Divider />
      
      <CustomizedHeatmapExample />
      <Divider />
      
      <CompactHeatmapExample />
      <Divider />
      
      <PerformanceComparisonExample />
      <Divider />
      
      <ExchangeComparisonExample />
      <Divider />
      
      <FullFeaturedHeatmapExample />
      <Divider />
      
      <MobileOptimizedHeatmapExample />
    </Box>
  </Box>
);

export default CryptoHeatmapExamples;
