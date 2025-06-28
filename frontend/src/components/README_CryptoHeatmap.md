# CryptoHeatmap Component Documentation

## Overview

The `CryptoHeatmap` component is a React component that embeds TradingView's official Crypto Coins Heatmap widget. It provides real-time cryptocurrency market visualization with support for multiple exchanges, performance metrics, and customization options.

## Features

- **Real-time Market Data**: Live cryptocurrency market data from TradingView
- **Multiple Exchanges**: Support for Binance, Coinbase, Kraken, and other major exchanges
- **Performance Metrics**: Various timeframes (daily, weekly, monthly, yearly)
- **Theme Support**: Light and dark themes
- **Responsive Design**: Configurable dimensions and responsive layout
- **Error Handling**: Comprehensive error handling with retry functionality
- **Loading States**: Professional loading indicators
- **TypeScript Support**: Full TypeScript integration

## Installation

The component requires the following dependencies:

```bash
npm install @mui/material @emotion/react @emotion/styled
```

## Basic Usage

```tsx
import React from 'react';
import CryptoHeatmap from './components/CryptoHeatmap';

function App() {
  return (
    <div>
      <CryptoHeatmap />
    </div>
  );
}
```

## Props Interface

```tsx
interface CryptoHeatmapProps {
  width?: number | string;           // Widget width (default: '100%')
  height?: number | string;          // Widget height (default: 500)
  dataSource?: 'Crypto' | 'CFD';     // Data source type (default: 'Crypto')
  exchange?: string;                 // Exchange name (default: 'BINANCE')
  symbolsGroups?: string;            // Symbol groups (default: 'crypto')
  hasTopBar?: boolean;               // Show top bar (default: true)
  isTransparent?: boolean;           // Transparent background (default: false)
  noTimeScale?: boolean;             // Hide time scale (default: false)
  valuesTracking?: string;           // Values tracking (default: '1')
  changeMode?: ChangeMode;           // Performance metric (default: 'price-changes')
  locale?: string;                   // Locale (default: 'en')
  theme?: 'light' | 'dark';         // Theme (default: 'light')
}

type ChangeMode = 
  | 'price-changes'    // Current price changes
  | 'Perf%D'          // Daily performance
  | 'Perf%W'          // Weekly performance
  | 'Perf%M'          // Monthly performance
  | 'Perf%3M'         // 3-month performance
  | 'Perf%6M'         // 6-month performance
  | 'Perf%Y'          // Yearly performance
  | 'Perf%YTD';       // Year-to-date performance
```

## Usage Examples

### Basic Heatmap

```tsx
<CryptoHeatmap />
```

### Customized Heatmap

```tsx
<CryptoHeatmap
  width="100%"
  height={600}
  exchange="COINBASE"
  changeMode="Perf%W"
  theme="dark"
  hasTopBar={true}
/>
```

### Compact Heatmap

```tsx
<CryptoHeatmap
  width={800}
  height={400}
  hasTopBar={false}
  changeMode="Perf%D"
  theme="light"
/>
```

### Multiple Performance Views

```tsx
<div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
  <CryptoHeatmap
    width="100%"
    height={300}
    changeMode="Perf%D"
    hasTopBar={false}
    exchange="BINANCE"
  />
  <CryptoHeatmap
    width="100%"
    height={300}
    changeMode="Perf%W"
    hasTopBar={false}
    exchange="BINANCE"
  />
</div>
```

## Supported Exchanges

- `BINANCE`
- `COINBASE`
- `KRAKEN`
- `BITSTAMP`
- `BITFINEX`
- `HUOBI`
- `OKEX`

## Performance Metrics

### Price Changes (`price-changes`)
Shows current price changes from the previous period.

### Time-based Performance
- **Daily (`Perf%D`)**: 24-hour performance
- **Weekly (`Perf%W`)**: 7-day performance
- **Monthly (`Perf%M`)**: 30-day performance
- **3-Month (`Perf%3M`)**: 90-day performance
- **6-Month (`Perf%6M`)**: 180-day performance
- **Yearly (`Perf%Y`)**: 365-day performance
- **Year-to-Date (`Perf%YTD`)**: Performance since January 1st

## Component Architecture

### Script Loading

The component dynamically loads TradingView's widget script:

```tsx
const script = document.createElement('script');
script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-crypto-coins-heatmap.js';
script.async = true;
```

### Configuration

Widget configuration is passed as JSON:

```tsx
const widgetConfig = {
  dataSource: 'Crypto',
  exchange: 'BINANCE',
  symbolsGroups: 'crypto',
  blockSize: 'market_cap_basic',
  blockColor: 'price-changes',
  locale: 'en',
  hasTopBar: true,
  isTransparent: false,
  noTimeScale: false,
  valuesTracking: '1',
  changeMode: 'price-changes',
  width: '100%',
  height: '500px',
  theme: 'light'
};
```

### Error Handling

The component handles various error scenarios:

- Script loading failures
- Network errors
- Widget initialization timeouts
- Configuration errors

## State Management

### Loading States

```tsx
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [scriptLoaded, setScriptLoaded] = useState(false);
```

### Cleanup

Proper cleanup prevents memory leaks:

```tsx
const cleanup = () => {
  if (scriptRef.current) {
    scriptRef.current.remove();
    scriptRef.current = null;
  }
  if (widgetRef.current) {
    widgetRef.current.innerHTML = '';
  }
  setScriptLoaded(false);
};
```

## Styling

### Container Styling

```tsx
const HeatmapContainer = styled(Box)(({ theme }) => ({
  position: 'relative',
  border: `1px solid ${theme.palette.divider}`,
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  overflow: 'hidden',
}));
```

### Responsive Design

The component automatically adapts to different screen sizes:

```tsx
const getContainerStyles = () => ({
  width: typeof width === 'string' ? width : `${width}px`,
  height: typeof height === 'string' ? height : `${height}px`,
  minHeight: 400,
});
```

## Best Practices

### Performance

1. **Memoization**: Use `React.memo()` for components that don't change frequently
2. **Lazy Loading**: Load the component only when needed
3. **Cleanup**: Always clean up resources in `useEffect` return function

### Error Handling

1. **Retry Mechanism**: Provide retry functionality for failed loads
2. **Fallback UI**: Show meaningful error messages
3. **Timeout Handling**: Set reasonable timeouts for script loading

### Accessibility

1. **ARIA Labels**: Add appropriate ARIA labels for screen readers
2. **Keyboard Navigation**: Ensure keyboard accessibility
3. **Color Contrast**: Maintain sufficient color contrast ratios

## Integration with Material-UI

The component integrates seamlessly with Material-UI:

```tsx
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { styled } from '@mui/material/styles';
```

## Demo Components

### HeatmapDemo

Interactive demo with configuration controls:

```tsx
import HeatmapDemo from './components/HeatmapDemo';

<HeatmapDemo />
```

### Examples

Various usage examples:

```tsx
import CryptoHeatmapExamples from './examples/CryptoHeatmapExamples';

<CryptoHeatmapExamples />
```

## Troubleshooting

### Common Issues

1. **Script Loading Errors**
   - Check network connectivity
   - Verify TradingView service status
   - Ensure HTTPS in production

2. **Widget Not Displaying**
   - Check container dimensions
   - Verify widget configuration
   - Check browser console for errors

3. **Performance Issues**
   - Limit number of simultaneous widgets
   - Use appropriate refresh intervals
   - Consider widget caching

### Debug Mode

Enable debug logging:

```tsx
<CryptoHeatmap
  {...props}
  onError={(error) => console.error('Heatmap Error:', error)}
  onLoad={() => console.log('Heatmap Loaded')}
/>
```

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Security Considerations

1. **Content Security Policy**: Allow TradingView scripts
2. **HTTPS**: Use HTTPS in production
3. **XSS Protection**: Sanitize any user-provided configuration

## Version History

- **v1.0.0**: Initial implementation with basic heatmap functionality
- **v1.1.0**: Added error handling and loading states
- **v1.2.0**: Added theme support and responsive design
- **v1.3.0**: Added multiple exchange support and performance metrics

## License

This component uses TradingView's widget which is subject to TradingView's terms of service.
