// Example usage patterns for the BalanceCard component

import React from 'react';
import BalanceCard from './components/BalanceCard';

// Example 1: Basic usage with sample data
const BasicExample = () => {
  const balanceData = [
    { asset: 'BTC', value: 0.12345678 },
    { asset: 'ETH', value: 2.5678 },
    { asset: 'USDT', value: 1250.50 },
  ];

  return (
    <BalanceCard
      exchangeName="Binance"
      walletType="Spot"
      balanceData={balanceData}
    />
  );
};

// Example 2: With string values (from API)
const ApiDataExample = () => {
  const apiData = [
    { asset: 'BTC', value: '0.00012345' },
    { asset: 'ETH', value: '1.234567' },
    { asset: 'USDT', value: '999.99' },
  ];

  return (
    <BalanceCard
      exchangeName="Coinbase Pro"
      walletType="Futures"
      balanceData={apiData}
    />
  );
};

// Example 3: Empty state
const EmptyStateExample = () => {
  return (
    <BalanceCard
      exchangeName="Kraken"
      walletType="Margin"
      balanceData={[]}
    />
  );
};

// Example 4: Large dataset
const LargeDatasetExample = () => {
  const largeDataset = [
    { asset: 'BTC', value: 0.001 },
    { asset: 'ETH', value: 0.5 },
    { asset: 'USDT', value: 100.25 },
    { asset: 'BNB', value: 25.75 },
    { asset: 'ADA', value: 50.0 },
    { asset: 'DOT', value: 10.5 },
    { asset: 'LINK', value: 15.25 },
    { asset: 'UNI', value: 8.75 },
  ];

  return (
    <BalanceCard
      exchangeName="Bybit"
      walletType="Savings"
      balanceData={largeDataset}
    />
  );
};

// Example 5: Dynamic data from props
interface DynamicExampleProps {
  exchange: string;
  wallet: string;
  balances: Array<{ asset: string; value: number | string }>;
}

const DynamicExample: React.FC<DynamicExampleProps> = ({ exchange, wallet, balances }) => {
  return (
    <BalanceCard
      exchangeName={exchange}
      walletType={wallet}
      balanceData={balances}
    />
  );
};

// Example 6: Grid layout with multiple cards
const GridLayoutExample = () => {
  const exchanges = [
    {
      name: 'Binance',
      walletType: 'Spot',
      balances: [
        { asset: 'BTC', value: 0.12 },
        { asset: 'ETH', value: 2.5 },
        { asset: 'USDT', value: 1250.50 },
      ],
    },
    {
      name: 'Coinbase',
      walletType: 'Futures',
      balances: [
        { asset: 'BTC', value: 0.05 },
        { asset: 'ETH', value: 1.2 },
        { asset: 'USDC', value: 500.00 },
      ],
    },
    {
      name: 'Kraken',
      walletType: 'Margin',
      balances: [],
    },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
      {exchanges.map((exchange, index) => (
        <BalanceCard
          key={index}
          exchangeName={exchange.name}
          walletType={exchange.walletType}
          balanceData={exchange.balances}
        />
      ))}
    </div>
  );
};

export {
  BasicExample,
  ApiDataExample,
  EmptyStateExample,
  LargeDatasetExample,
  DynamicExample,
  GridLayoutExample,
};
