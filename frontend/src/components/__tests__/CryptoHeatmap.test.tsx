import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CryptoHeatmap from '../components/CryptoHeatmap';

// Mock theme for testing
const theme = createTheme();

// Wrapper component for testing with theme
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>
    {children}
  </ThemeProvider>
);

// Mock TradingView script loading
const mockScript = {
  onload: null as (() => void) | null,
  onerror: null as (() => void) | null,
  remove: jest.fn(),
} as any;

beforeEach(() => {
  // Mock document.createElement for script elements
  jest.spyOn(document, 'createElement').mockImplementation((tagName) => {
    if (tagName === 'script') {
      return mockScript;
    }
    return document.createElement(tagName);
  });
  
  // Mock appendChild
  jest.spyOn(document.body, 'appendChild').mockImplementation(() => mockScript);
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe('CryptoHeatmap Component', () => {
  test('renders loading state initially', () => {
    render(
      <TestWrapper>
        <CryptoHeatmap />
      </TestWrapper>
    );

    expect(screen.getByText('Loading crypto heatmap...')).toBeInTheDocument();
  });

  test('renders with custom props', () => {
    render(
      <TestWrapper>
        <CryptoHeatmap
          width={800}
          height={600}
          exchange="COINBASE"
          theme="dark"
          changeMode="Perf%W"
        />
      </TestWrapper>
    );

    // Should still show loading initially
    expect(screen.getByText('Loading crypto heatmap...')).toBeInTheDocument();
  });

  test('handles script load success', async () => {
    render(
      <TestWrapper>
        <CryptoHeatmap />
      </TestWrapper>
    );

    // Simulate successful script load
    if (mockScript.onload) {
      mockScript.onload();
    }

    await waitFor(() => {
      expect(screen.queryByText('Loading crypto heatmap...')).not.toBeInTheDocument();
    });
  });

  test('handles script load error', async () => {
    render(
      <TestWrapper>
        <CryptoHeatmap />
      </TestWrapper>
    );

    // Simulate script load error
    if (mockScript.onerror) {
      mockScript.onerror();
    }

    await waitFor(() => {
      expect(screen.getByText('Failed to load TradingView widget script')).toBeInTheDocument();
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  test('creates script with correct src', () => {
    render(
      <TestWrapper>
        <CryptoHeatmap />
      </TestWrapper>
    );

    expect(document.createElement).toHaveBeenCalledWith('script');
    expect(mockScript.src).toBe('https://s3.tradingview.com/external-embedding/embed-widget-crypto-coins-heatmap.js');
    expect(mockScript.async).toBe(true);
  });

  test('renders with different exchange settings', () => {
    const exchanges = ['BINANCE', 'COINBASE', 'KRAKEN'];
    
    exchanges.forEach(exchange => {
      const { unmount } = render(
        <TestWrapper>
          <CryptoHeatmap exchange={exchange} />
        </TestWrapper>
      );
      
      expect(screen.getByText('Loading crypto heatmap...')).toBeInTheDocument();
      unmount();
    });
  });

  test('renders with different performance metrics', () => {
    const metrics = ['price-changes', 'Perf%D', 'Perf%W', 'Perf%M'] as const;
    
    metrics.forEach(metric => {
      const { unmount } = render(
        <TestWrapper>
          <CryptoHeatmap changeMode={metric} />
        </TestWrapper>
      );
      
      expect(screen.getByText('Loading crypto heatmap...')).toBeInTheDocument();
      unmount();
    });
  });

  test('applies correct container styles', () => {
    const { container } = render(
      <TestWrapper>
        <CryptoHeatmap width={800} height={600} />
      </TestWrapper>
    );

    const heatmapContainer = container.firstChild as HTMLElement;
    expect(heatmapContainer).toHaveStyle({
      width: '800px',
      height: '600px',
    });
  });

  test('handles string width and height', () => {
    const { container } = render(
      <TestWrapper>
        <CryptoHeatmap width="100%" height="500px" />
      </TestWrapper>
    );

    const heatmapContainer = container.firstChild as HTMLElement;
    expect(heatmapContainer).toHaveStyle({
      width: '100%',
      height: '500px',
    });
  });
});

// Integration test with HeatmapDemo
describe('CryptoHeatmap Integration', () => {
  test('works with multiple instances', () => {
    render(
      <TestWrapper>
        <div>
          <CryptoHeatmap changeMode="Perf%D" height={300} />
          <CryptoHeatmap changeMode="Perf%W" height={300} />
        </div>
      </TestWrapper>
    );

    const loadingTexts = screen.getAllByText('Loading crypto heatmap...');
    expect(loadingTexts).toHaveLength(2);
  });

  test('cleanup works correctly', () => {
    const { unmount } = render(
      <TestWrapper>
        <CryptoHeatmap />
      </TestWrapper>
    );

    unmount();

    expect(mockScript.remove).toHaveBeenCalled();
  });
});

export default {};
