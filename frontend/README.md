# Trading Portal Frontend

A comprehensive React frontend application for a cryptocurrency trading platform, featuring professional-grade components built with TypeScript, Material-UI, and industry-standard charting libraries.

## 🚀 Features

### 📊 **TradingView Chart Integration**
- Professional candlestick charts using TradingView Lightweight Charts
- Real-time price data simulation
- Interactive crosshair and tooltips
- Volume histogram overlays
- Light/dark theme support
- Responsive design with auto-resize

### 💰 **Balance Management**
- Dynamic balance cards with exchange grouping
- Authenticated API data fetching
- Real-time balance updates
- Error handling and loading states
- Multiple exchange support

### 🔗 **API Integration**
- Custom React hooks for data fetching
- JWT authentication handling
- Comprehensive error management
- Auto-refresh capabilities
- Network status detection

## 🏗️ **Component Architecture**

### Core Components

1. **TradingViewChart** - Professional trading charts
   ```tsx
   <TradingViewChart
     symbol="BTC/USDT"
     interval="1h"
     theme="dark"
     width={800}
     height={400}
   />
   ```

2. **BalanceCard** - Exchange balance display
   ```tsx
   <BalanceCard
     exchangeName="Binance"
     walletType="Spot"
     balanceData={balanceData}
   />
   ```

3. **BalanceDashboard** - Integrated balance overview
   ```tsx
   <BalanceDashboard
     autoRefresh={true}
     refreshInterval={30000}
   />
   ```

### Custom Hooks

1. **useFetchBalances** - Authenticated balance fetching
   ```tsx
   const { data, loading, error, refetch } = useFetchBalances({
     authToken: 'jwt-token',
     refreshInterval: 30000
   });
   ```

## 🛠️ **Technology Stack**

### Core Technologies
- **React 18.2** - Latest React with hooks and concurrent features
- **TypeScript 5.0** - Full type safety and developer experience
- **Material-UI 5.15** - Professional UI component library
- **Vite 5.0** - Fast build tool and development server

### Specialized Libraries
- **TradingView Lightweight Charts 4.1** - Professional charting
- **Axios 1.6** - HTTP client for API requests
- **Emotion** - CSS-in-JS for styled components

### Development Tools
- **ESLint** - Code linting and quality
- **TypeScript Compiler** - Type checking
- **Vite Dev Server** - Hot module replacement

## 📦 **Installation**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check
```

## 🔧 **Configuration**

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Chart Configuration
REACT_APP_DEFAULT_SYMBOL=BTC/USDT
REACT_APP_DEFAULT_INTERVAL=1h

# Feature Flags
REACT_APP_ENABLE_DARK_MODE=true
REACT_APP_ENABLE_AUTO_REFRESH=true
```

### Chart Configuration

```typescript
// Chart settings in TradingViewChart component
const chartConfig = {
  width: 800,
  height: 400,
  theme: 'light', // or 'dark'
  symbol: 'BTC/USDT',
  interval: '1h',
  // Advanced options
  crosshair: true,
  volume: true,
  grid: true,
  timeScale: true
};
```

## 📱 **Responsive Design**

The application is fully responsive and supports:

- **Desktop**: Full feature set with large charts
- **Tablet**: Adapted layouts with touch interactions
- **Mobile**: Compact views optimized for small screens

### Breakpoints
- **xs**: 0px+ (mobile)
- **sm**: 600px+ (tablet)
- **md**: 900px+ (desktop)
- **lg**: 1200px+ (large desktop)
- **xl**: 1536px+ (extra large)

## 🎨 **Theming**

### Custom Theme Configuration

```typescript
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
    mode: 'light', // or 'dark'
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
  shape: {
    borderRadius: 8,
  },
});
```

### Dark Mode Support

```typescript
const useDarkMode = () => {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setDarkMode(mediaQuery.matches);

    const handleChange = (e) => setDarkMode(e.matches);
    mediaQuery.addEventListener('change', handleChange);

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return [darkMode, setDarkMode];
};
```

## 🔌 **API Integration**

### Authentication

```typescript
// JWT token handling
const authConfig = {
  tokenKey: 'authToken',
  refreshKey: 'refreshToken',
  baseURL: process.env.REACT_APP_API_BASE_URL,
  timeout: 10000,
};

// Auto token refresh
const useAuthToken = () => {
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  
  useEffect(() => {
    const refreshToken = async () => {
      try {
        const response = await axios.post('/api/auth/refresh');
        setToken(response.data.token);
        localStorage.setItem('authToken', response.data.token);
      } catch (error) {
        // Handle refresh failure
        localStorage.removeItem('authToken');
        window.location.href = '/login';
      }
    };

    if (token) {
      // Schedule token refresh
      const interval = setInterval(refreshToken, 15 * 60 * 1000); // 15 minutes
      return () => clearInterval(interval);
    }
  }, [token]);

  return token;
};
```

### Data Fetching Patterns

```typescript
// Optimistic updates
const useOptimisticUpdate = () => {
  const [data, setData] = useState([]);
  
  const updateItem = async (id, newData) => {
    // Optimistically update UI
    setData(prev => prev.map(item => 
      item.id === id ? { ...item, ...newData } : item
    ));
    
    try {
      await api.updateItem(id, newData);
    } catch (error) {
      // Revert on error
      setData(prev => prev.map(item => 
        item.id === id ? originalData[id] : item
      ));
    }
  };
  
  return { data, updateItem };
};
```

## 🧪 **Testing**

### Component Testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import BalanceCard from './BalanceCard';

const renderWithTheme = (component) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('BalanceCard', () => {
  const mockData = [
    { asset: 'BTC', value: 0.123 },
    { asset: 'ETH', value: 2.456 },
  ];

  test('renders balance data correctly', () => {
    renderWithTheme(
      <BalanceCard
        exchangeName="Binance"
        walletType="Spot"
        balanceData={mockData}
      />
    );

    expect(screen.getByText('Binance')).toBeInTheDocument();
    expect(screen.getByText('BTC')).toBeInTheDocument();
    expect(screen.getByText('0.123')).toBeInTheDocument();
  });

  test('handles empty data gracefully', () => {
    renderWithTheme(
      <BalanceCard
        exchangeName="Binance"
        walletType="Spot"
        balanceData={[]}
      />
    );

    expect(screen.getByText('No balance data available')).toBeInTheDocument();
  });
});
```

### Hook Testing

```typescript
import { renderHook, act } from '@testing-library/react';
import useFetchBalances from './useFetchBalances';

describe('useFetchBalances', () => {
  test('fetches balance data successfully', async () => {
    const { result } = renderHook(() => useFetchBalances());

    expect(result.current.loading).toBe(true);

    await act(async () => {
      // Wait for hook to complete
    });

    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBeDefined();
  });
});
```

## 📈 **Performance Optimization**

### Code Splitting

```typescript
// Lazy load components
const TradingViewChart = lazy(() => import('./components/TradingViewChart'));
const BalanceDashboard = lazy(() => import('./components/BalanceDashboard'));

// Usage with Suspense
<Suspense fallback={<CircularProgress />}>
  <TradingViewChart />
</Suspense>
```

### Memoization

```typescript
// Memo for expensive components
const MemoizedChart = React.memo(TradingViewChart, (prevProps, nextProps) => {
  return (
    prevProps.symbol === nextProps.symbol &&
    prevProps.interval === nextProps.interval &&
    prevProps.theme === nextProps.theme
  );
});

// Callback memoization
const handleDataUpdate = useCallback((newData) => {
  setData(prevData => ({ ...prevData, ...newData }));
}, []);

// Value memoization
const expensiveValue = useMemo(() => {
  return data.reduce((sum, item) => sum + item.value, 0);
}, [data]);
```

### Bundle Optimization

```typescript
// Vite configuration for optimization
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@mui/material', '@emotion/react'],
          charts: ['lightweight-charts'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
});
```

## 🔒 **Security**

### Content Security Policy

```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline' fonts.googleapis.com;
  font-src 'self' fonts.gstatic.com;
  img-src 'self' data: https:;
  connect-src 'self' wss: https:;
">
```

### API Security

```typescript
// Request interceptor for auth
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 🚀 **Deployment**

### Production Build

```bash
# Build for production
npm run build

# Preview production build locally
npm run preview

# Analyze bundle size
npm run analyze
```

### Docker Deployment

```dockerfile
# Multi-stage build
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Configuration

```bash
# Production environment variables
REACT_APP_API_BASE_URL=https://api.trading-portal.com
REACT_APP_WS_URL=wss://api.trading-portal.com/ws
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0
```

## 📊 **Monitoring**

### Error Tracking

```typescript
// Error boundary with reporting
class ErrorBoundary extends Component {
  componentDidCatch(error, errorInfo) {
    // Send to error tracking service
    errorTracker.captureException(error, {
      extra: errorInfo,
      tags: {
        component: 'TradingViewChart',
        version: process.env.REACT_APP_VERSION,
      },
    });
  }
}
```

### Performance Monitoring

```typescript
// Performance metrics
const usePerformanceMonitoring = () => {
  useEffect(() => {
    // Mark component mount
    performance.mark('component-mount-start');
    
    return () => {
      performance.mark('component-mount-end');
      performance.measure(
        'component-mount',
        'component-mount-start',
        'component-mount-end'
      );
    };
  }, []);
};
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Use TypeScript for all new components
- Follow Material-UI design principles
- Write comprehensive tests
- Document complex logic
- Use meaningful commit messages

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- [TradingView](https://www.tradingview.com/) for the Lightweight Charts library
- [Material-UI](https://mui.com/) for the component library
- [React](https://reactjs.org/) team for the framework
- [TypeScript](https://www.typescriptlang.org/) team for the language
