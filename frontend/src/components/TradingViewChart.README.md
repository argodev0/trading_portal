# TradingViewChart Component Documentation

A React component that integrates TradingView's Lightweight Charts library to display interactive cryptocurrency trading charts with candlestick data and volume indicators.

## Overview

The `TradingViewChart` component provides a professional-grade charting solution for displaying OHLC (Open, High, Low, Close) candlestick data with volume overlays. It's built using the official TradingView Lightweight Charts library and follows React best practices with hooks and TypeScript support.

## Features

### 📊 **Chart Features**
- ✅ Candlestick charts with OHLC data visualization
- ✅ Volume histogram overlay with color-coded bars
- ✅ Interactive crosshair with price and time tooltips
- ✅ Zoom and pan functionality
- ✅ Auto-fitting time scale
- ✅ Real-time price updates simulation
- ✅ Professional grid and axis styling

### ⚙️ **Technical Features**
- ✅ React hooks integration (`useEffect`, `useRef`, `useState`)
- ✅ TypeScript support with proper type definitions
- ✅ Responsive design with auto-resize capability
- ✅ Loading and error state management
- ✅ Light and dark theme support
- ✅ Memory leak prevention and proper cleanup
- ✅ Configurable dimensions and trading pairs

## Installation

Install the required dependencies:

```bash
npm install lightweight-charts react @mui/material
npm install --save-dev @types/react
```

## Basic Usage

```tsx
import TradingViewChart from './components/TradingViewChart';

function MyTradingApp() {
  return (
    <div>
      <h1>My Trading Dashboard</h1>
      <TradingViewChart />
    </div>
  );
}
```

## Props Interface

```typescript
interface TradingViewChartProps {
  symbol?: string;        // Trading pair (default: 'BTC/USDT')
  interval?: string;      // Time interval (default: '1h')
  width?: number;         // Chart width in pixels (default: 800)
  height?: number;        // Chart height in pixels (default: 400)
  theme?: 'light' | 'dark'; // Color theme (default: 'light')
}
```

## Advanced Usage Examples

### Custom Configuration

```tsx
<TradingViewChart
  symbol="ETH/USDT"
  interval="4h"
  theme="dark"
  width={1000}
  height={500}
/>
```

### Multiple Charts Dashboard

```tsx
const Dashboard = () => {
  const symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'];
  
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
      {symbols.map(symbol => (
        <TradingViewChart
          key={symbol}
          symbol={symbol}
          width={400}
          height={300}
        />
      ))}
    </div>
  );
};
```

### Responsive Chart

```tsx
const ResponsiveChart = () => {
  const [width, setWidth] = useState(800);

  useEffect(() => {
    const handleResize = () => {
      setWidth(Math.min(window.innerWidth - 40, 1200));
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <TradingViewChart
      symbol="BTC/USDT"
      width={width}
      height={400}
    />
  );
};
```

## Component Architecture

### Core Structure

```typescript
const TradingViewChart: React.FC<TradingViewChartProps> = (props) => {
  // Refs for DOM elements and chart instances
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  
  // State management
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);
  
  // Chart initialization and data fetching
  useEffect(() => {
    const cleanup = initializeChart();
    loadChartData();
    return cleanup;
  }, [symbol, interval, theme, width, height]);
  
  return (
    // JSX rendering
  );
};
```

### Data Flow

1. **Initialization**: `useEffect` triggers chart creation
2. **DOM Attachment**: Chart attaches to `chartContainerRef.current`
3. **Data Fetching**: `fetchChartData()` simulates API call
4. **Series Creation**: Candlestick and volume series are added
5. **Data Binding**: Chart data is set via `setData()`
6. **Cleanup**: Chart is properly disposed on unmount

## Data Format

### Candlestick Data

```typescript
interface CandleData {
  time: UTCTimestamp;     // Unix timestamp
  open: number;           // Opening price
  high: number;           // Highest price
  low: number;            // Lowest price
  close: number;          // Closing price
  volume?: number;        // Trading volume
}
```

### Sample Data

```typescript
const sampleData: CandleData[] = [
  {
    time: 1640995200 as UTCTimestamp, // 2022-01-01 00:00:00
    open: 47000.50,
    high: 48200.75,
    low: 46800.25,
    close: 47850.00,
    volume: 1234
  },
  // ... more data points
];
```

## Styling and Themes

### Light Theme Configuration

```typescript
const lightThemeOptions = {
  layout: {
    background: { color: '#ffffff' },
    textColor: '#000000',
  },
  grid: {
    vertLines: { color: '#f0f0f0' },
    horzLines: { color: '#f0f0f0' },
  },
  rightPriceScale: {
    borderColor: '#cccccc',
  },
  timeScale: {
    borderColor: '#cccccc',
  },
};
```

### Dark Theme Configuration

```typescript
const darkThemeOptions = {
  layout: {
    background: { color: '#1a1a1a' },
    textColor: '#ffffff',
  },
  grid: {
    vertLines: { color: '#2a2a2a' },
    horzLines: { color: '#2a2a2a' },
  },
  rightPriceScale: {
    borderColor: '#485c7b',
  },
  timeScale: {
    borderColor: '#485c7b',
  },
};
```

### Custom Color Scheme

```typescript
const candlestickOptions = {
  upColor: '#26a69a',        // Green for bullish candles
  downColor: '#ef5350',      // Red for bearish candles
  borderVisible: false,
  wickUpColor: '#26a69a',    // Green for bullish wicks
  wickDownColor: '#ef5350',  // Red for bearish wicks
};
```

## API Integration

### Real API Implementation

```typescript
const fetchRealChartData = async (symbol: string, interval: string) => {
  try {
    const response = await fetch(`/api/chart-data?symbol=${symbol}&interval=${interval}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Transform API data to chart format
    return data.map((item: any) => ({
      time: item.timestamp as UTCTimestamp,
      open: parseFloat(item.open),
      high: parseFloat(item.high),
      low: parseFloat(item.low),
      close: parseFloat(item.close),
      volume: parseInt(item.volume)
    }));
  } catch (error) {
    console.error('Error fetching chart data:', error);
    throw error;
  }
};
```

### WebSocket Integration Example

```typescript
const useRealTimeData = (symbol: string) => {
  const [latestCandle, setLatestCandle] = useState<CandleData | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`wss://api.example.com/ws/${symbol}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLatestCandle({
        time: data.timestamp as UTCTimestamp,
        open: data.open,
        high: data.high,
        low: data.low,
        close: data.close,
        volume: data.volume
      });
    };

    return () => ws.close();
  }, [symbol]);

  return latestCandle;
};
```

## Performance Considerations

### Memory Management
- Charts are properly disposed on component unmount
- Event listeners are cleaned up in `useEffect` return function
- Refs are cleared when component unmounts

### Optimization Tips
```typescript
// Debounce resize events
const debouncedResize = useCallback(
  debounce(() => {
    if (chartRef.current && chartContainerRef.current) {
      chartRef.current.applyOptions({
        width: chartContainerRef.current.clientWidth,
      });
    }
  }, 100),
  []
);

// Lazy load chart data
const loadDataLazily = useCallback(async () => {
  const data = await import('./chartData.json');
  setCandlestickData(data.default);
}, []);
```

## Error Handling

### Error States
- Network connection errors
- API authentication failures
- Data parsing errors
- Chart rendering failures

### Error Recovery
```typescript
const handleError = (error: Error) => {
  setError(error.message);
  setLoading(false);
  
  // Log error for monitoring
  console.error('Chart error:', error);
  
  // Optional: Send to error tracking service
  // errorTracker.captureException(error);
};
```

## Testing

### Unit Test Example

```typescript
import { render, screen } from '@testing-library/react';
import TradingViewChart from './TradingViewChart';

describe('TradingViewChart', () => {
  test('renders chart container', () => {
    render(<TradingViewChart />);
    expect(screen.getByText('BTC/USDT')).toBeInTheDocument();
  });

  test('handles loading state', () => {
    render(<TradingViewChart />);
    expect(screen.getByText('Loading chart data...')).toBeInTheDocument();
  });

  test('displays error message on failure', async () => {
    // Mock fetch to return error
    global.fetch = jest.fn().mockRejectedValue(new Error('API Error'));
    
    render(<TradingViewChart />);
    
    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch chart data/)).toBeInTheDocument();
    });
  });
});
```

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Dependencies

```json
{
  "dependencies": {
    "lightweight-charts": "^4.1.0",
    "react": "^18.0.0",
    "@mui/material": "^5.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
```

## Troubleshooting

### Common Issues

1. **Chart not rendering**
   - Ensure container has dimensions
   - Check console for JavaScript errors
   - Verify lightweight-charts is installed

2. **Performance issues**
   - Limit data points (< 1000 recommended)
   - Debounce resize events
   - Use React.memo for optimization

3. **TypeScript errors**
   - Install @types/react
   - Check lightweight-charts version compatibility

### Debug Mode

```typescript
const TradingViewChart = (props) => {
  const DEBUG = process.env.NODE_ENV === 'development';
  
  useEffect(() => {
    if (DEBUG) {
      console.log('Chart props:', props);
      console.log('Chart ref:', chartRef.current);
    }
  }, [props]);
  
  // ... rest of component
};
```

## License

This component uses the TradingView Lightweight Charts library, which is licensed under Apache License 2.0. Ensure compliance with licensing requirements when using in commercial applications.
