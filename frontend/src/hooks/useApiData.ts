import { useState, useEffect, useCallback } from 'react';
import { apiService, ExchangeAccount, PortfolioSummary, TradingPair } from '../services/apiService';

// Custom hook for exchange accounts
export const useExchangeAccounts = (autoRefresh: boolean = true, refreshInterval: number = 30000) => {
  const [accounts, setAccounts] = useState<ExchangeAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchAccounts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getExchangeAccounts();
      setAccounts(data);
      setLastUpdated(new Date());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch exchange accounts';
      setError(errorMessage);
      console.error('Error fetching exchange accounts:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshAccounts = useCallback(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  const syncAccount = useCallback(async (accountId: number) => {
    try {
      setError(null);
      await apiService.syncExchangeAccount(accountId);
      // Refresh all accounts after sync
      await fetchAccounts();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to sync account';
      setError(errorMessage);
      console.error('Error syncing account:', err);
    }
  }, [fetchAccounts]);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(fetchAccounts, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, fetchAccounts]);

  return {
    accounts,
    loading,
    error,
    lastUpdated,
    refreshAccounts,
    syncAccount,
  };
};

// Custom hook for portfolio summary
export const usePortfolioSummary = (autoRefresh: boolean = true, refreshInterval: number = 30000) => {
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchPortfolio = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getPortfolioSummary();
      setPortfolio(data);
      setLastUpdated(new Date());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch portfolio data';
      setError(errorMessage);
      console.error('Error fetching portfolio:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshPortfolio = useCallback(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(fetchPortfolio, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, fetchPortfolio]);

  return {
    portfolio,
    loading,
    error,
    lastUpdated,
    refreshPortfolio,
  };
};

// Custom hook for market data
export const useMarketData = (autoRefresh: boolean = true, refreshInterval: number = 10000) => {
  const [marketData, setMarketData] = useState<TradingPair[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchMarketData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getMarketData();
      setMarketData(data);
      setLastUpdated(new Date());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch market data';
      setError(errorMessage);
      console.error('Error fetching market data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshMarketData = useCallback(() => {
    fetchMarketData();
  }, [fetchMarketData]);

  useEffect(() => {
    fetchMarketData();
  }, [fetchMarketData]);

  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(fetchMarketData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, fetchMarketData]);

  return {
    marketData,
    loading,
    error,
    lastUpdated,
    refreshMarketData,
  };
};

// Connection status hook
export const useConnectionStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [connectionQuality, setConnectionQuality] = useState<'good' | 'poor' | 'offline'>('good');

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setConnectionQuality('good');
    };

    const handleOffline = () => {
      setIsOnline(false);
      setConnectionQuality('offline');
    };

    // Test connection quality periodically
    const testConnection = async () => {
      if (!navigator.onLine) {
        setConnectionQuality('offline');
        return;
      }

      try {
        const start = Date.now();
        await fetch('/api/health', { method: 'HEAD', cache: 'no-cache' });
        const duration = Date.now() - start;
        
        if (duration < 500) {
          setConnectionQuality('good');
        } else {
          setConnectionQuality('poor');
        }
      } catch {
        setConnectionQuality('poor');
      }
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    const interval = setInterval(testConnection, 30000);
    testConnection(); // Initial test

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, []);

  return {
    isOnline,
    connectionQuality,
    isConnected: isOnline && connectionQuality !== 'offline',
    connectionStatus: isOnline ? 
      (connectionQuality === 'good' ? 'Connected' : 'Poor Connection') : 
      'Disconnected',
  };
};

// Real-time price updates hook
export const useRealTimePrices = (symbols: string[] = ['BTCUSDT']) => {
  const [prices, setPrices] = useState<Record<string, { price: number; change: number }>>({});
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // This would typically connect to a WebSocket for real-time prices
    // For now, we'll simulate with periodic updates
    const updatePrices = () => {
      const newPrices: Record<string, { price: number; change: number }> = {};
      
      symbols.forEach(symbol => {
        const basePrice = symbol === 'BTCUSDT' ? 45000 : 
                         symbol === 'ETHUSDT' ? 2400 : 
                         symbol === 'BNBUSDT' ? 240 : 100;
        
        const change = (Math.random() - 0.5) * 0.02; // ±1% change
        const price = basePrice * (1 + change);
        
        newPrices[symbol] = {
          price: parseFloat(price.toFixed(2)),
          change: parseFloat((change * 100).toFixed(2)),
        };
      });
      
      setPrices(newPrices);
    };

    setConnected(true);
    updatePrices(); // Initial update
    
    const interval = setInterval(updatePrices, 5000); // Update every 5 seconds

    return () => {
      clearInterval(interval);
      setConnected(false);
    };
  }, [symbols]);

  return {
    prices,
    connected,
  };
};
