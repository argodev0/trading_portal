# useFetchBalances Hook Documentation

A custom React hook for fetching cryptocurrency balance data from the `/api/accounts/balances` endpoint with comprehensive error handling, loading states, and authentication support.

## Features

- ✅ **Authenticated API Requests** - Automatic JWT token handling
- ✅ **Loading State Management** - Built-in loading indicators
- ✅ **Error Handling** - Comprehensive error states and messages
- ✅ **Auto-refresh** - Configurable automatic data refreshing
- ✅ **Manual Refresh** - Programmatic data refetching
- ✅ **Network Status** - Online/offline detection and handling
- ✅ **Token Management** - Automatic token cleanup on auth failures
- ✅ **TypeScript Support** - Full type safety and IntelliSense

## Installation

Make sure you have the required dependencies:

```bash
npm install axios react
npm install --save-dev @types/react @types/node
```

## Basic Usage

```tsx
import useFetchBalances from './hooks/useFetchBalances';

function BalanceComponent() {
  const { data, loading, error, refetch } = useFetchBalances();

  if (loading) return <div>Loading balances...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      <button onClick={refetch}>Refresh</button>
      {data?.map((balance, index) => (
        <div key={index}>
          {balance.asset}: {balance.value}
        </div>
      ))}
    </div>
  );
}
```

## API Reference

### Hook Signature

```typescript
useFetchBalances(options?: UseFetchBalancesOptions): UseFetchBalancesState
```

### Options Interface

```typescript
interface UseFetchBalancesOptions {
  authToken?: string;          // JWT token for authentication
  baseURL?: string;            // API base URL (default: process.env.REACT_APP_API_BASE_URL)
  autoFetch?: boolean;         // Auto-fetch on mount (default: true)
  refreshInterval?: number;    // Auto-refresh interval in ms
}
```

### Return State Interface

```typescript
interface UseFetchBalancesState {
  data: BalanceData[] | null;  // Array of balance objects or null
  loading: boolean;            // Loading state indicator
  error: string | null;        // Error message or null
  refetch: () => void;         // Function to manually refetch data
}
```

### Balance Data Interface

```typescript
interface BalanceData {
  asset: string;               // Asset symbol (e.g., 'BTC', 'ETH')
  value: number | string;      // Balance amount
  exchangeName?: string;       // Optional exchange name
  walletType?: string;         // Optional wallet type (e.g., 'Spot', 'Futures')
}
```

## Configuration Options

### Authentication Token

The hook automatically looks for authentication tokens in this order:

1. `authToken` option parameter
2. `localStorage.getItem('authToken')`
3. `localStorage.getItem('access_token')`
4. `localStorage.getItem('jwt_token')`

```tsx
// Option 1: Pass token directly
const { data } = useFetchBalances({ authToken: 'your-jwt-token' });

// Option 2: Store in localStorage (automatic detection)
localStorage.setItem('authToken', 'your-jwt-token');
const { data } = useFetchBalances();
```

### Auto-refresh

Enable automatic data refreshing at specified intervals:

```tsx
const { data } = useFetchBalances({
  refreshInterval: 30000, // Refresh every 30 seconds
});
```

### Custom Base URL

Override the default API base URL:

```tsx
const { data } = useFetchBalances({
  baseURL: 'https://api.mytrading.com'
});
```

### Manual Fetch Only

Disable automatic fetching on component mount:

```tsx
const { data, refetch } = useFetchBalances({
  autoFetch: false
});

// Call refetch manually when needed
const handleFetchClick = () => {
  refetch();
};
```

## Error Handling

The hook provides detailed error messages for different scenarios:

### Authentication Errors (401)
- **Message**: "Authentication failed. Please login again."
- **Action**: Automatically clears stored tokens

### Permission Errors (403)
- **Message**: "Access forbidden. You don't have permission to view balances."

### Network Errors
- **Message**: "Network error. Please check your connection and try again."
- **Action**: Automatically retries when connection is restored

### Server Errors (500)
- **Message**: "Server error. Please try again later."

### Rate Limiting (429)
- **Message**: "Too many requests. Please try again later."

## Advanced Usage Examples

### With React Context

```tsx
import { createContext, useContext } from 'react';

const AuthContext = createContext({ token: null });

function BalanceWithContext() {
  const { token } = useContext(AuthContext);
  const { data, loading, error } = useFetchBalances({ authToken: token });
  
  return (
    <div>
      {/* Component content */}
    </div>
  );
}
```

### With Error Boundary

```tsx
function BalanceWithErrorHandling() {
  const { data, loading, error, refetch } = useFetchBalances();

  const handleRetry = () => {
    refetch();
  };

  if (error?.includes('Authentication')) {
    return (
      <div>
        <p>Authentication failed</p>
        <button onClick={() => window.location.href = '/login'}>
          Login
        </button>
      </div>
    );
  }

  return (
    <div>
      {loading && <div>Loading...</div>}
      {error && (
        <div>
          <p>Error: {error}</p>
          <button onClick={handleRetry}>Retry</button>
        </div>
      )}
      {/* Data display */}
    </div>
  );
}
```

### Integration with BalanceCard Component

```tsx
import BalanceCard from './BalanceCard';

function BalanceDashboard() {
  const { data, loading, error } = useFetchBalances({
    refreshInterval: 60000 // 1 minute
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  // Group balances by exchange
  const groupedBalances = data?.reduce((acc, balance) => {
    const key = `${balance.exchangeName}-${balance.walletType}`;
    if (!acc[key]) {
      acc[key] = {
        exchangeName: balance.exchangeName || 'Unknown',
        walletType: balance.walletType || 'Spot',
        balances: []
      };
    }
    acc[key].balances.push(balance);
    return acc;
  }, {});

  return (
    <div>
      {Object.entries(groupedBalances || {}).map(([key, group]) => (
        <BalanceCard
          key={key}
          exchangeName={group.exchangeName}
          walletType={group.walletType}
          balanceData={group.balances}
        />
      ))}
    </div>
  );
}
```

## Environment Variables

Set these environment variables for default configuration:

```bash
# .env file
REACT_APP_API_BASE_URL=http://localhost:8000
```

## Network Status Handling

The hook automatically handles network status changes:

- **Goes Offline**: Shows "You are offline" error
- **Comes Online**: Automatically retries if there was a network error

## Token Management

The hook provides automatic token management:

- **Valid Token**: Makes authenticated requests
- **Invalid/Expired Token**: Clears token from localStorage and shows auth error
- **Missing Token**: Shows "No authentication token found" error

## Performance Considerations

### Memory Management
- Automatically cleans up intervals on component unmount
- Removes event listeners when component unmounts

### Request Optimization
- Uses axios with 10-second timeout
- Debounces rapid refresh requests
- Caches axios instance configuration

### Bundle Size
- Uses tree-shaking friendly imports
- Minimal dependencies (only axios and React hooks)

## Troubleshooting

### Common Issues

1. **"Cannot find module 'axios'"**
   ```bash
   npm install axios
   ```

2. **Token not being sent**
   ```tsx
   // Check localStorage for token
   console.log(localStorage.getItem('authToken'));
   ```

3. **CORS errors**
   ```tsx
   // Ensure baseURL is correctly set
   const { data } = useFetchBalances({
     baseURL: 'https://your-api-domain.com'
   });
   ```

4. **TypeScript errors**
   ```bash
   npm install --save-dev @types/node @types/react
   ```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Testing

The hook can be easily tested using React Testing Library:

```tsx
import { renderHook } from '@testing-library/react';
import useFetchBalances from './useFetchBalances';

test('should fetch balances on mount', async () => {
  const { result } = renderHook(() => useFetchBalances());
  
  expect(result.current.loading).toBe(true);
  // Add more assertions...
});
```
