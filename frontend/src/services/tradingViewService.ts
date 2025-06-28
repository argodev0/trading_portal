// TradingView Widget Service
interface TradingViewWindow extends Window {
  TradingView?: any;
}

declare const window: TradingViewWindow;

export interface TradingViewChartWidgetConfig {
  container_id: string;
  width?: number | string;
  height?: number | string;
  symbol?: string;
  interval?: string;
  timezone?: string;
  theme?: 'light' | 'dark';
  style?: string;
  locale?: string;
  toolbar_bg?: string;
  enable_publishing?: boolean;
  allow_symbol_change?: boolean;
  hide_top_toolbar?: boolean;
  hide_legend?: boolean;
  save_image?: boolean;
  hide_volume?: boolean;
  studies?: string[];
}

export interface TradingViewHeatmapWidgetConfig {
  container_id: string;
  width?: number | string;
  height?: number | string;
  dataSource?: string;
  exchange?: string;
  symbolsGroups?: string;
  blockSize?: string;
  blockColor?: string;
  locale?: string;
  hasTopBar?: boolean;
  isTransparent?: boolean;
  noTimeScale?: boolean;
  valuesTracking?: string;
  changeMode?: string;
  theme?: string;
}

class TradingViewService {
  private static instance: TradingViewService;
  private isScriptLoaded = false;
  private scriptPromise: Promise<void> | null = null;
  private widgets: Map<string, any> = new Map();

  private constructor() {}

  public static getInstance(): TradingViewService {
    if (!TradingViewService.instance) {
      TradingViewService.instance = new TradingViewService();
    }
    return TradingViewService.instance;
  }

  // Load TradingView script
  public async loadScript(): Promise<void> {
    if (this.isScriptLoaded) {
      return Promise.resolve();
    }

    if (this.scriptPromise) {
      return this.scriptPromise;
    }

    this.scriptPromise = new Promise((resolve, reject) => {
      // Check if script is already loaded
      if (window.TradingView) {
        this.isScriptLoaded = true;
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/tv.js';
      script.async = true;
      script.onload = () => {
        this.isScriptLoaded = true;
        resolve();
      };
      script.onerror = () => {
        reject(new Error('Failed to load TradingView script'));
      };

      document.head.appendChild(script);
    });

    return this.scriptPromise;
  }

  // Create chart widget
  public async createChartWidget(config: TradingViewChartWidgetConfig): Promise<any> {
    try {
      await this.loadScript();

      if (!window.TradingView) {
        throw new Error('TradingView library not available');
      }

      // Remove existing widget if it exists
      this.removeWidget(config.container_id);

      const widgetConfig = {
        autosize: true,
        symbol: config.symbol || 'BINANCE:BTCUSDT',
        interval: config.interval || '1H',
        timezone: config.timezone || 'Etc/UTC',
        theme: config.theme || 'dark',
        style: config.style || '1',
        locale: config.locale || 'en',
        toolbar_bg: config.toolbar_bg || '#f1f3f6',
        enable_publishing: config.enable_publishing || false,
        allow_symbol_change: config.allow_symbol_change || true,
        container_id: config.container_id,
        width: config.width || '100%',
        height: config.height || 400,
        hide_top_toolbar: config.hide_top_toolbar || false,
        hide_legend: config.hide_legend || false,
        save_image: config.save_image || false,
        hide_volume: config.hide_volume || false,
        studies: config.studies || [],
      };

      const widget = new window.TradingView.widget(widgetConfig);
      this.widgets.set(config.container_id, widget);

      return widget;
    } catch (error) {
      console.error('Failed to create TradingView chart widget:', error);
      throw error;
    }
  }

  // Create heatmap widget
  public async createHeatmapWidget(config: TradingViewHeatmapWidgetConfig): Promise<any> {
    try {
      await this.loadScript();

      if (!window.TradingView) {
        throw new Error('TradingView library not available');
      }

      // Remove existing widget if it exists
      this.removeWidget(config.container_id);

      const widgetConfig = {
        dataSource: config.dataSource || 'Crypto',
        exchange: config.exchange || 'BINANCE',
        symbolsGroups: config.symbolsGroups || 'crypto',
        blockSize: config.blockSize || 'market_cap_basic',
        blockColor: config.blockColor || 'change|60',
        locale: config.locale || 'en',
        hasTopBar: config.hasTopBar !== false,
        isTransparent: config.isTransparent || false,
        noTimeScale: config.noTimeScale || false,
        valuesTracking: config.valuesTracking || '0',
        changeMode: config.changeMode || 'price-changes',
        width: config.width || '100%',
        height: config.height || 400,
        theme: config.theme || 'dark',
        container_id: config.container_id,
      };

      const widget = new window.TradingView.CryptoCurrencyMarketWidget(widgetConfig);
      this.widgets.set(config.container_id, widget);

      return widget;
    } catch (error) {
      console.error('Failed to create TradingView heatmap widget:', error);
      throw error;
    }
  }

  // Remove widget
  public removeWidget(containerId: string): void {
    const widget = this.widgets.get(containerId);
    if (widget && typeof widget.remove === 'function') {
      widget.remove();
    }
    this.widgets.delete(containerId);

    // Clear container
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = '';
    }
  }

  // Remove all widgets
  public removeAllWidgets(): void {
    this.widgets.forEach((widget, containerId) => {
      this.removeWidget(containerId);
    });
  }

  // Check if script is loaded
  public isReady(): boolean {
    return this.isScriptLoaded && !!window.TradingView;
  }
}

export const tradingViewService = TradingViewService.getInstance();
