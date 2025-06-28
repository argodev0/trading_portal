// Usage examples for the useFetchBalances hook

import React from 'react';
import useFetchBalances from '../hooks/useFetchBalances';

// Example 1: Basic usage
const BasicBalanceExample = () => {
  const { data, loading, error, refetch } = useFetchBalances();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data</div>;

  return (
    <div>
      <h2>Your Balances</h2>
      <button onClick={refetch}>Refresh</button>
      <ul>
        {data.map((balance, index) => (
          <li key={index}>
            {balance.asset}: {balance.value}
          </li>
        ))}
      </ul>
    </div>
  );
};

// Example 2: With custom auth token
const AuthenticatedBalanceExample = () => {
  const authToken = localStorage.getItem('userToken'); // or from context
  
  const { data, loading, error } = useFetchBalances({
    authToken,
    autoFetch: true
  });

  return (
    <div>
      {loading && <p>Loading balances...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {data && (
        <div>
          <h3>Account Balance</h3>
          {data.map((item, idx) => (
            <div key={idx}>
              {item.asset}: {item.value}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Example 3: With auto-refresh
const AutoRefreshBalanceExample = () => {
  const { data, loading, error, refetch } = useFetchBalances({
    refreshInterval: 10000, // 10 seconds
    autoFetch: true
  });

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <h2>Live Balances</h2>
        {loading && <span>🔄</span>}
        <button onClick={refetch} disabled={loading}>
          Manual Refresh
        </button>
      </div>
      
      {error && (
        <div style={{ color: 'red', margin: '10px 0' }}>
          {error}
        </div>
      )}
      
      {data && (
        <table>
          <thead>
            <tr>
              <th>Asset</th>
              <th>Value</th>
              <th>Exchange</th>
              <th>Wallet</th>
            </tr>
          </thead>
          <tbody>
            {data.map((balance, index) => (
              <tr key={index}>
                <td>{balance.asset}</td>
                <td>{balance.value}</td>
                <td>{balance.exchangeName || 'N/A'}</td>
                <td>{balance.walletType || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

// Example 4: With custom base URL
const CustomApiBalanceExample = () => {
  const { data, loading, error } = useFetchBalances({
    baseURL: 'https://api.mytrading.com',
    authToken: process.env.REACT_APP_API_TOKEN
  });

  return (
    <div>
      <h2>Custom API Balances</h2>
      {loading ? (
        <div>Loading from custom API...</div>
      ) : error ? (
        <div>API Error: {error}</div>
      ) : (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      )}
    </div>
  );
};

// Example 5: Manual fetch only (no auto-fetch)
const ManualFetchBalanceExample = () => {
  const { data, loading, error, refetch } = useFetchBalances({
    autoFetch: false // Don't fetch on mount
  });

  return (
    <div>
      <h2>Manual Fetch Example</h2>
      <button onClick={refetch} disabled={loading}>
        {loading ? 'Fetching...' : 'Fetch Balances'}
      </button>
      
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {data && (
        <div>
          <p>Found {data.length} balances:</p>
          <ul>
            {data.map((balance, index) => (
              <li key={index}>
                {balance.asset}: {balance.value}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

// Example 6: Integration with React Context
import { createContext, useContext } from 'react';

interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  isAuthenticated: false
});

const ContextBalanceExample = () => {
  const { token, isAuthenticated } = useContext(AuthContext);
  
  const { data, loading, error } = useFetchBalances({
    authToken: token || undefined,
    autoFetch: isAuthenticated
  });

  if (!isAuthenticated) {
    return <div>Please log in to view balances</div>;
  }

  return (
    <div>
      <h2>Authenticated Balances</h2>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {data && (
        <div>
          {data.map((balance, index) => (
            <div key={index}>
              {balance.asset}: {balance.value}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Example 7: Error handling with retry logic
const ErrorHandlingBalanceExample = () => {
  const { data, loading, error, refetch } = useFetchBalances();

  const handleRetry = () => {
    refetch();
  };

  const getErrorAction = () => {
    if (error?.includes('Authentication')) {
      return (
        <button onClick={() => window.location.href = '/login'}>
          Go to Login
        </button>
      );
    }
    
    if (error?.includes('Network')) {
      return (
        <button onClick={handleRetry}>
          Retry Connection
        </button>
      );
    }
    
    return (
      <button onClick={handleRetry}>
        Try Again
      </button>
    );
  };

  return (
    <div>
      <h2>Balance with Error Handling</h2>
      
      {loading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div>Loading...</div>
          <div className="spinner">⚡</div>
        </div>
      )}
      
      {error && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#fee', 
          border: '1px solid #fcc',
          borderRadius: '5px',
          margin: '10px 0'
        }}>
          <p style={{ color: '#c00', margin: '0 0 10px 0' }}>
            <strong>Error:</strong> {error}
          </p>
          {getErrorAction()}
        </div>
      )}
      
      {data && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: '#efe', 
          border: '1px solid #cfc',
          borderRadius: '5px'
        }}>
          <p><strong>Successfully loaded {data.length} balances</strong></p>
          {data.map((balance, index) => (
            <div key={index}>
              {balance.asset}: {balance.value}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export {
  BasicBalanceExample,
  AuthenticatedBalanceExample,
  AutoRefreshBalanceExample,
  CustomApiBalanceExample,
  ManualFetchBalanceExample,
  ContextBalanceExample,
  ErrorHandlingBalanceExample
};
