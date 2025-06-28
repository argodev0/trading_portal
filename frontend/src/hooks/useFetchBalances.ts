import { useState, useEffect, useCallback } from 'react';
import axios, { AxiosResponse, AxiosError } from 'axios';

// Type definitions for the hook
interface BalanceData {
  asset: string;
  value: number | string;
  exchangeName?: string;
  walletType?: string;
}

interface FetchBalancesResponse {
  success: boolean;
  data: BalanceData[];
  message?: string;
  count?: number;
}

interface UseFetchBalancesState {
  data: BalanceData[] | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

interface UseFetchBalancesOptions {
  authToken?: string;
  baseURL?: string;
  autoFetch?: boolean;
  refreshInterval?: number;
}

/**
 * Custom React hook for fetching balance data from the API
 * 
 * @param options Configuration options for the hook
 * @returns Object containing data, loading state, error state, and refetch function
 */
const useFetchBalances = (options: UseFetchBalancesOptions = {}): UseFetchBalancesState => {
  const {
    authToken,
    baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
    autoFetch = true,
    refreshInterval
  } = options;

  // State management
  const [data, setData] = useState<BalanceData[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Get auth token from localStorage if not provided
  const getAuthToken = useCallback((): string | null => {
    if (authToken) return authToken;
    
    // Try to get token from localStorage
    const storedToken = localStorage.getItem('authToken') || 
                       localStorage.getItem('access_token') ||
                       localStorage.getItem('jwt_token');
    
    return storedToken;
  }, [authToken]);

  // Create axios instance with default config
  const createAxiosInstance = useCallback(() => {
    const token = getAuthToken();
    
    return axios.create({
      baseURL,
      timeout: 10000, // 10 seconds timeout
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    });
  }, [baseURL, getAuthToken]);

  // Main fetch function
  const fetchBalances = useCallback(async () => {
    const token = getAuthToken();
    
    if (!token) {
      setError('No authentication token found. Please login.');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const axiosInstance = createAxiosInstance();
      
      const response: AxiosResponse<FetchBalancesResponse> = await axiosInstance.get('/api/accounts/balances');
      
      if (response.data.success) {
        setData(response.data.data || []);
        setError(null);
      } else {
        setError(response.data.message || 'Failed to fetch balances');
        setData(null);
      }
    } catch (err) {
      const axiosError = err as AxiosError;
      
      // Handle different types of errors
      if (axiosError.response) {
        // Server responded with error status
        const status = axiosError.response.status;
        const responseData = axiosError.response.data as any;
        
        switch (status) {
          case 401:
            setError('Authentication failed. Please login again.');
            // Clear stored token on 401
            localStorage.removeItem('authToken');
            localStorage.removeItem('access_token');
            localStorage.removeItem('jwt_token');
            break;
          case 403:
            setError('Access forbidden. You don\'t have permission to view balances.');
            break;
          case 404:
            setError('Balance endpoint not found. Please check the API configuration.');
            break;
          case 429:
            setError('Too many requests. Please try again later.');
            break;
          case 500:
            setError('Server error. Please try again later.');
            break;
          default:
            setError(responseData?.message || `HTTP Error: ${status}`);
        }
      } else if (axiosError.request) {
        // Network error
        setError('Network error. Please check your connection and try again.');
      } else {
        // Other error
        setError(axiosError.message || 'An unexpected error occurred.');
      }
      
      setData(null);
      console.error('Balance fetch error:', axiosError);
    } finally {
      setLoading(false);
    }
  }, [getAuthToken, createAxiosInstance]);

  // Refetch function for manual refresh
  const refetch = useCallback(() => {
    fetchBalances();
  }, [fetchBalances]);

  // Initial fetch and auto-refresh setup
  useEffect(() => {
    if (autoFetch) {
      fetchBalances();
    }

    // Set up auto-refresh if interval is provided
    let intervalId: NodeJS.Timeout | null = null;
    
    if (refreshInterval && refreshInterval > 0) {
      intervalId = setInterval(() => {
        fetchBalances();
      }, refreshInterval);
    }

    // Cleanup interval on unmount
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [autoFetch, refreshInterval, fetchBalances]);

  // Listen for online/offline events
  useEffect(() => {
    const handleOnline = () => {
      if (error && error.includes('Network error')) {
        fetchBalances();
      }
    };

    const handleOffline = () => {
      setError('You are offline. Please check your connection.');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [error, fetchBalances]);

  return {
    data,
    loading,
    error,
    refetch
  };
};

export default useFetchBalances;

// Export types for external use
export type { 
  BalanceData, 
  FetchBalancesResponse, 
  UseFetchBalancesState, 
  UseFetchBalancesOptions 
};
