/**
 * Test file for useFetchBalances hook
 * 
 * This demonstrates how to test the custom hook with various scenarios.
 * To run these tests, you would need to install testing dependencies:
 * 
 * npm install --save-dev @testing-library/react @testing-library/react-hooks jest
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import axios from 'axios';
import useFetchBalances from './useFetchBalances';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('useFetchBalances Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue('mock-token');
    
    // Mock axios.create to return a mock instance
    const mockAxiosInstance = {
      get: jest.fn(),
    };
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);
  });

  test('should initialize with loading state', () => {
    const { result } = renderHook(() => useFetchBalances({ autoFetch: false }));
    
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe(null);
    expect(typeof result.current.refetch).toBe('function');
  });

  test('should fetch data successfully', async () => {
    const mockData = [
      { asset: 'BTC', value: 0.123 },
      { asset: 'ETH', value: 2.456 },
    ];

    const mockAxiosInstance = {
      get: jest.fn().mockResolvedValue({
        data: {
          success: true,
          data: mockData,
        },
      }),
    };
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

    const { result } = renderHook(() => useFetchBalances());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBe(null);
  });

  test('should handle API error responses', async () => {
    const mockAxiosInstance = {
      get: jest.fn().mockResolvedValue({
        data: {
          success: false,
          message: 'API Error',
        },
      }),
    };
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

    const { result } = renderHook(() => useFetchBalances());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBe(null);
    expect(result.current.error).toBe('API Error');
  });

  test('should handle 401 authentication error', async () => {
    const mockAxiosInstance = {
      get: jest.fn().mockRejectedValue({
        response: {
          status: 401,
          data: { message: 'Unauthorized' },
        },
      }),
    };
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

    const { result } = renderHook(() => useFetchBalances());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Authentication failed. Please login again.');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('authToken');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('jwt_token');
  });

  test('should handle network errors', async () => {
    const mockAxiosInstance = {
      get: jest.fn().mockRejectedValue({
        request: {},
        message: 'Network Error',
      }),
    };
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

    const { result } = renderHook(() => useFetchBalances());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Network error. Please check your connection and try again.');
  });

  test('should refetch data when refetch is called', async () => {
    const mockData = [{ asset: 'BTC', value: 0.123 }];
    const mockAxiosInstance = {
      get: jest.fn().mockResolvedValue({
        data: {
          success: true,
          data: mockData,
        },
      }),
    };
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

    const { result } = renderHook(() => useFetchBalances({ autoFetch: false }));

    act(() => {
      result.current.refetch();
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/accounts/balances');
    expect(result.current.data).toEqual(mockData);
  });

  test('should handle missing authentication token', () => {
    localStorageMock.getItem.mockReturnValue(null);

    const { result } = renderHook(() => useFetchBalances());

    expect(result.current.error).toBe('No authentication token found. Please login.');
    expect(result.current.loading).toBe(false);
  });

  test('should use provided auth token over localStorage', async () => {
    const customToken = 'custom-token';
    const mockAxiosInstance = {
      get: jest.fn().mockResolvedValue({
        data: { success: true, data: [] },
      }),
    };
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

    renderHook(() => useFetchBalances({ authToken: customToken }));

    expect(mockedAxios.create).toHaveBeenCalledWith({
      baseURL: 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${customToken}`,
      },
    });
  });

  test('should handle different HTTP status codes', async () => {
    const testCases = [
      { status: 403, expectedError: 'Access forbidden. You don\'t have permission to view balances.' },
      { status: 404, expectedError: 'Balance endpoint not found. Please check the API configuration.' },
      { status: 429, expectedError: 'Too many requests. Please try again later.' },
      { status: 500, expectedError: 'Server error. Please try again later.' },
    ];

    for (const testCase of testCases) {
      const mockAxiosInstance = {
        get: jest.fn().mockRejectedValue({
          response: {
            status: testCase.status,
            data: {},
          },
        }),
      };
      mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

      const { result } = renderHook(() => useFetchBalances());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBe(testCase.expectedError);
    }
  });

  test('should set up auto-refresh interval', async () => {
    jest.useFakeTimers();
    
    const mockAxiosInstance = {
      get: jest.fn().mockResolvedValue({
        data: { success: true, data: [] },
      }),
    };
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

    renderHook(() => useFetchBalances({ refreshInterval: 5000 }));

    // Initial call
    expect(mockAxiosInstance.get).toHaveBeenCalledTimes(1);

    // Fast-forward time
    act(() => {
      jest.advanceTimersByTime(5000);
    });

    // Should have called again
    expect(mockAxiosInstance.get).toHaveBeenCalledTimes(2);

    jest.useRealTimers();
  });

  test('should cleanup interval on unmount', () => {
    jest.useFakeTimers();
    const clearIntervalSpy = jest.spyOn(global, 'clearInterval');

    const { unmount } = renderHook(() => 
      useFetchBalances({ refreshInterval: 5000 })
    );

    unmount();

    expect(clearIntervalSpy).toHaveBeenCalled();

    jest.useRealTimers();
    clearIntervalSpy.mockRestore();
  });
});

// Integration test example
describe('useFetchBalances Integration', () => {
  test('should work with real axios (mocked response)', async () => {
    // This test would work with actual axios instance
    const mockBalanceData = [
      { asset: 'BTC', value: '0.12345678', exchangeName: 'Binance', walletType: 'Spot' },
      { asset: 'ETH', value: '2.5678', exchangeName: 'Binance', walletType: 'Spot' },
      { asset: 'USDT', value: '1250.50', exchangeName: 'Coinbase', walletType: 'Futures' },
    ];

    // Mock the actual API response structure
    const mockAxiosInstance = {
      get: jest.fn().mockResolvedValue({
        data: {
          success: true,
          data: mockBalanceData,
          count: mockBalanceData.length,
          message: 'Balances retrieved successfully'
        },
      }),
    };
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

    const { result } = renderHook(() => useFetchBalances({
      baseURL: 'https://api.trading-portal.com',
      autoFetch: true,
    }));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockBalanceData);
    expect(result.current.error).toBe(null);
    expect(mockAxiosInstance.get).toHaveBeenCalledWith('/api/accounts/balances');
  });
});
