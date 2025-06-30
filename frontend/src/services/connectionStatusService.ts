import { environment } from '../config/environment';

export interface ExchangeConnectionStatus {
  exchange: 'binance' | 'kucoin';
  status: 'connected' | 'disconnected' | 'error' | 'checking';
  lastChecked: Date;
  message?: string;
  latency?: number;
}

export interface ConnectionStatusState {
  binance: ExchangeConnectionStatus;
  kucoin: ExchangeConnectionStatus;
  lastUpdate: Date;
}

class ConnectionStatusService {
  private listeners: ((status: ConnectionStatusState) => void)[] = [];
  private currentStatus: ConnectionStatusState;
  private checkInterval: NodeJS.Timeout | null = null;

  constructor() {
    this.currentStatus = {
      binance: {
        exchange: 'binance',
        status: 'disconnected',
        lastChecked: new Date(),
        message: 'Not connected'
      },
      kucoin: {
        exchange: 'kucoin',
        status: 'disconnected',
        lastChecked: new Date(),
        message: 'Not connected'
      },
      lastUpdate: new Date()
    };
  }

  public subscribe(callback: (status: ConnectionStatusState) => void): () => void {
    this.listeners.push(callback);
    // Immediately send current status
    callback(this.currentStatus);
    
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }

  private notifyListeners(): void {
    this.currentStatus.lastUpdate = new Date();
    this.listeners.forEach(listener => listener(this.currentStatus));
  }

  public async startMonitoring(): Promise<void> {
    // Initial check
    await this.checkConnections();
    
    // Set up periodic checks every 30 seconds
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }
    
    this.checkInterval = setInterval(() => {
      this.checkConnections();
    }, 30000);
  }

  public stopMonitoring(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  private async checkConnections(): Promise<void> {
    // Always try to use real API connections
    await Promise.all([
      this.checkBinanceConnection(),
      this.checkKucoinConnection()
    ]);
    
    this.notifyListeners();
  }

  private async checkBinanceConnection(): Promise<void> {
    const startTime = Date.now();
    
    try {
      this.currentStatus.binance.status = 'checking';
      this.notifyListeners();

      const response = await fetch('/api/exchanges/binance/status/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const latency = Date.now() - startTime;

      if (response.ok) {
        const data = await response.json();
        this.currentStatus.binance = {
          exchange: 'binance',
          status: 'connected',
          lastChecked: new Date(),
          message: data.message || 'Connected to Binance API',
          latency
        };
      } else if (response.status === 404) {
        // API endpoint not available (static mode)
        this.currentStatus.binance = {
          exchange: 'binance',
          status: 'error',
          lastChecked: new Date(),
          message: 'API not available - Django backend not running',
          latency
        };
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      this.currentStatus.binance = {
        exchange: 'binance',
        status: 'error',
        lastChecked: new Date(),
        message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        latency: Date.now() - startTime
      };
    }
  }

  private async checkKucoinConnection(): Promise<void> {
    const startTime = Date.now();
    
    try {
      this.currentStatus.kucoin.status = 'checking';
      this.notifyListeners();

      const response = await fetch('/api/exchanges/kucoin/status/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const latency = Date.now() - startTime;

      if (response.ok) {
        const data = await response.json();
        this.currentStatus.kucoin = {
          exchange: 'kucoin',
          status: 'connected',
          lastChecked: new Date(),
          message: data.message || 'Connected to KuCoin API',
          latency
        };
      } else if (response.status === 404) {
        // API endpoint not available (static mode)
        this.currentStatus.kucoin = {
          exchange: 'kucoin',
          status: 'error',
          lastChecked: new Date(),
          message: 'API not available - Django backend not running',
          latency
        };
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      this.currentStatus.kucoin = {
        exchange: 'kucoin',
        status: 'error',
        lastChecked: new Date(),
        message: `Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        latency: Date.now() - startTime
      };
    }
  }

  public getCurrentStatus(): ConnectionStatusState {
    return this.currentStatus;
  }

  public async forceCheck(): Promise<void> {
    await this.checkConnections();
  }
}

export const connectionStatusService = new ConnectionStatusService();
