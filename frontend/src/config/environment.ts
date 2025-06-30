// Environment configuration for the trading portal
export interface EnvironmentConfig {
  isDevelopment: boolean;
  isProduction: boolean;
  apiBaseUrl: string;
  features: {
    realTimeData: boolean;
    authentication: boolean;
    balanceFetching: boolean;
  };
}

// Force development mode features for live API functionality
const getEnvironment = (): EnvironmentConfig => {
  // Always enable real API features regardless of hostname
  // This ensures we always try to use the Django backend if available
  return {
    isDevelopment: true,  // Force development mode for API features
    isProduction: false,  // Disable production mode restrictions
    apiBaseUrl: '',       // Use relative URLs for nginx proxy
    features: {
      realTimeData: true,      // Enable real-time data
      authentication: true,    // Enable authentication
      balanceFetching: true,   // Enable balance fetching
    }
  };
};

export const environment = getEnvironment();
