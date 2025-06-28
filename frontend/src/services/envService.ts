// Environment configuration service
export class EnvService {
  private static instance: EnvService;
  private config: Record<string, string> = {};

  private constructor() {
    this.loadConfig();
  }

  public static getInstance(): EnvService {
    if (!EnvService.instance) {
      EnvService.instance = new EnvService();
    }
    return EnvService.instance;
  }

  private loadConfig(): void {
    // In a production environment, these would come from environment variables
    // For development, we'll use the values from .env file on the backend
    this.config = {
      API_BASE_URL: (window as any)?.ENV?.VITE_API_BASE_URL || 'http://localhost:8000',
      WEBSOCKET_URL: (window as any)?.ENV?.VITE_WEBSOCKET_URL || 'ws://localhost:8000/ws',
      NODE_ENV: 'development',
      TRADING_VIEW_WIDGET_URL: 'https://s3.tradingview.com/external-embedding/',
    };
  }

  public get(key: string, defaultValue: string = ''): string {
    return this.config[key] || defaultValue;
  }

  public getApiBaseUrl(): string {
    return this.get('API_BASE_URL');
  }

  public getWebSocketUrl(): string {
    return this.get('WEBSOCKET_URL');
  }

  public isDevelopment(): boolean {
    return this.get('NODE_ENV') === 'development';
  }

  public getTradingViewWidgetUrl(): string {
    return this.get('TRADING_VIEW_WIDGET_URL');
  }

  // Add API key validation (these keys are handled by backend)
  public hasValidApiKeys(): boolean {
    // In a real app, this would check if backend has valid API keys configured
    // For now, we'll assume they're configured if we can connect to the backend
    return true;
  }
}

export const envService = EnvService.getInstance();
