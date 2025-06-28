// API service for interacting with the backend
import axios, { AxiosResponse } from 'axios';
import { envService } from './envService';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: envService.getApiBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login if needed
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    return Promise.reject(error);
  }
);

// Types for API responses
export interface ExchangeAccount {
  id: number;
  name: string;
  exchange: string;
  account_type: string;
  status: 'active' | 'inactive' | 'connecting';
  total_value_usd: number;
  balances: AccountBalance[];
  last_updated: string;
}

export interface AccountBalance {
  asset: string;
  free: number;
  locked: number;
  total: number;
  value_usd: number;
  value_btc: number;
}

export interface TradingPair {
  symbol: string;
  base_asset: string;
  quote_asset: string;
  price: number;
  change_24h: number;
  volume_24h: number;
}

export interface PortfolioSummary {
  total_value_usd: number;
  total_value_btc: number;
  day_change_usd: number;
  day_change_percent: number;
  week_change_usd: number;
  week_change_percent: number;
  asset_count: number;
}

export interface ChartData {
  symbol: string;
  interval: string;
  data: {
    time: number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }[];
}

// API Service class
class ApiService {
  // Authentication
  async login(username: string, password: string): Promise<{ access: string; refresh: string }> {
    const response = await apiClient.post('/api/auth/login/', {
      username,
      password,
    });
    return response.data;
  }

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await apiClient.post('/api/auth/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  }

  // Exchange accounts
  async getExchangeAccounts(): Promise<ExchangeAccount[]> {
    const response = await apiClient.get('/api/accounts/keys/');
    return this.transformExchangeData(response.data);
  }

  async syncExchangeAccount(accountId: number): Promise<ExchangeAccount> {
    const response = await apiClient.post(`/api/accounts/keys/${accountId}/sync/`);
    return response.data;
  }

  // Portfolio data
  async getPortfolioSummary(): Promise<PortfolioSummary> {
    const accounts = await this.getExchangeAccounts();
    return this.calculatePortfolioSummary(accounts);
  }

  // Chart data
  async getChartData(symbol: string, interval: string = '1h'): Promise<ChartData> {
    // Chart data is handled by TradingView widgets
    // This endpoint would be used for custom chart implementations
    const response = await apiClient.get('/api/market/chart/', {
      params: { symbol, interval }
    });
    return response.data;
  }

  // Market data
  async getMarketData(): Promise<TradingPair[]> {
    const response = await apiClient.get('/api/market/tickers/');
    return response.data;
  }

  // Transform exchange data from backend format
  private transformExchangeData(data: any[]): ExchangeAccount[] {
    return data.map((item, index) => ({
      id: item.id || index + 1,
      name: `${item.exchange || 'Unknown'} - ${item.account_type || 'Spot'}`,
      exchange: item.exchange || 'Unknown',
      account_type: item.account_type || 'spot',
      status: item.is_active ? 'active' : 'inactive',
      total_value_usd: item.total_value_usd || 0,
      balances: item.balances || [],
      last_updated: item.updated_at || new Date().toISOString(),
    }));
  }

  // Calculate portfolio summary from accounts
  private calculatePortfolioSummary(accounts: ExchangeAccount[]): PortfolioSummary {
    const totalValue = accounts.reduce((sum, account) => sum + account.total_value_usd, 0);
    const assetCount = accounts.reduce((count, account) => count + account.balances.length, 0);
    
    // Get BTC price from the first account's BTC balance or use market data
    const btcPrice = 45000; // This should come from real market data API
    
    return {
      total_value_usd: totalValue,
      total_value_btc: totalValue / btcPrice,
      day_change_usd: totalValue * 0.025, // These should come from historical data
      day_change_percent: 2.5,
      week_change_usd: totalValue * -0.015,
      week_change_percent: -1.5,
      asset_count: assetCount,
    };
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
