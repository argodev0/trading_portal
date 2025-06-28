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
    try {
      const response = await apiClient.get('/api/accounts/keys/');
      return this.transformExchangeData(response.data);
    } catch (error) {
      console.error('Failed to fetch exchange accounts:', error);
      // Return mock data for development
      return this.getMockExchangeAccounts();
    }
  }

  async syncExchangeAccount(accountId: number): Promise<ExchangeAccount> {
    const response = await apiClient.post(`/api/accounts/keys/${accountId}/sync/`);
    return response.data;
  }

  // Portfolio data
  async getPortfolioSummary(): Promise<PortfolioSummary> {
    try {
      const accounts = await this.getExchangeAccounts();
      return this.calculatePortfolioSummary(accounts);
    } catch (error) {
      console.error('Failed to fetch portfolio summary:', error);
      return this.getMockPortfolioSummary();
    }
  }

  // Chart data
  async getChartData(symbol: string, interval: string = '1h'): Promise<ChartData> {
    try {
      // This would typically call a chart data endpoint
      // For now, we'll use the TradingView widget approach
      return this.getMockChartData(symbol, interval);
    } catch (error) {
      console.error('Failed to fetch chart data:', error);
      return this.getMockChartData(symbol, interval);
    }
  }

  // Market data
  async getMarketData(): Promise<TradingPair[]> {
    try {
      const response = await apiClient.get('/api/market/tickers/');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch market data:', error);
      return this.getMockMarketData();
    }
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
    
    return {
      total_value_usd: totalValue,
      total_value_btc: totalValue / 45000, // Mock BTC price
      day_change_usd: totalValue * 0.025, // Mock 2.5% daily change
      day_change_percent: 2.5,
      week_change_usd: totalValue * -0.015, // Mock -1.5% weekly change
      week_change_percent: -1.5,
      asset_count: assetCount,
    };
  }

  // Mock data generators for development
  private getMockExchangeAccounts(): ExchangeAccount[] {
    return [
      {
        id: 1,
        name: 'Binance - Funding',
        exchange: 'Binance',
        account_type: 'funding',
        status: 'active',
        total_value_usd: 178.62,
        balances: [
          {
            asset: 'BTC',
            free: 0.00166,
            locked: 0,
            total: 0.00166,
            value_usd: 178.62,
            value_btc: 0.00166,
          }
        ],
        last_updated: new Date().toISOString(),
      },
      {
        id: 2,
        name: 'Binance - Futures',
        exchange: 'Binance',
        account_type: 'futures',
        status: 'active',
        total_value_usd: 0.00,
        balances: [],
        last_updated: new Date().toISOString(),
      },
      {
        id: 3,
        name: 'Binance - Spot',
        exchange: 'Binance',
        account_type: 'spot',
        status: 'active',
        total_value_usd: 0.00,
        balances: [
          {
            asset: 'LDBNB',
            free: 0.00000,
            locked: 0,
            total: 0.00000,
            value_usd: 0.00,
            value_btc: 0,
          }
        ],
        last_updated: new Date().toISOString(),
      },
      {
        id: 4,
        name: 'KuCoin - Funding',
        exchange: 'KuCoin',
        account_type: 'funding',
        status: 'active',
        total_value_usd: 0.00,
        balances: [],
        last_updated: new Date().toISOString(),
      },
      {
        id: 5,
        name: 'KuCoin - Spot',
        exchange: 'KuCoin',
        account_type: 'spot',
        status: 'active',
        total_value_usd: 178.38,
        balances: [
          {
            asset: 'BTC',
            free: 0.00166,
            locked: 0,
            total: 0.00166,
            value_usd: 178.38,
            value_btc: 0.00166,
          },
          {
            asset: 'USDT',
            free: 0.00017,
            locked: 0,
            total: 0.00017,
            value_usd: 0.00,
            value_btc: 0,
          }
        ],
        last_updated: new Date().toISOString(),
      }
    ];
  }

  private getMockPortfolioSummary(): PortfolioSummary {
    return {
      total_value_usd: 1256.89,
      total_value_btc: 0.02793,
      day_change_usd: 45.67,
      day_change_percent: 3.77,
      week_change_usd: -23.45,
      week_change_percent: -1.83,
      asset_count: 4,
    };
  }

  private getMockChartData(symbol: string, interval: string): ChartData {
    const data: ChartData['data'] = [];
    const now = Date.now();
    const oneHour = 60 * 60 * 1000;
    let basePrice = 45000; // Starting BTC price

    for (let i = 100; i >= 0; i--) {
      const time = Math.floor((now - i * oneHour) / 1000);
      const volatility = 0.02;
      const randomChange = (Math.random() - 0.5) * volatility;
      
      const open = basePrice;
      const close = open * (1 + randomChange);
      const high = Math.max(open, close) * (1 + Math.random() * 0.01);
      const low = Math.min(open, close) * (1 - Math.random() * 0.01);
      
      data.push({
        time,
        open: parseFloat(open.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        volume: Math.floor(Math.random() * 1000) + 100,
      });

      basePrice = close;
    }

    return {
      symbol,
      interval,
      data,
    };
  }

  private getMockMarketData(): TradingPair[] {
    return [
      { symbol: 'BTCUSDT', base_asset: 'BTC', quote_asset: 'USDT', price: 45234.56, change_24h: 2.45, volume_24h: 1234567890 },
      { symbol: 'ETHUSDT', base_asset: 'ETH', quote_asset: 'USDT', price: 2345.67, change_24h: -1.23, volume_24h: 987654321 },
      { symbol: 'BNBUSDT', base_asset: 'BNB', quote_asset: 'USDT', price: 234.56, change_24h: 0.89, volume_24h: 456789123 },
      { symbol: 'ADAUSDT', base_asset: 'ADA', quote_asset: 'USDT', price: 0.4567, change_24h: 4.56, volume_24h: 123456789 },
    ];
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
