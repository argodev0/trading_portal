import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { 
  CssBaseline, 
  Box, 
  Drawer,
  AppBar,
  Toolbar,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  useMediaQuery,
  useTheme
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountBalance as PortfolioIcon,
  TrendingUp as LiveTradesIcon,
  ShowChart as TradingViewIcon,
  Science as BacktestingIcon,
  History as TradeHistoryIcon,
  AutoAwesome as StrategyGeneratorIcon,
  Settings as SettingsIcon,
  Menu as MenuIcon,
  GridView as HeatmapIcon
} from '@mui/icons-material';

// Import components
import DashboardView from './views/DashboardView';
import PortfolioView from './views/PortfolioView';
import TradingChartsView from './views/TradingChartsView';
import CryptoHeatmapView from './views/CryptoHeatmapView';
import LoginPage from './views/LoginPage';

// Create dark theme matching the attached image
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00D4AA', // Teal/green accent color
      dark: '#00B894',
      light: '#26DE81',
    },
    secondary: {
      main: '#6C5CE7',
      dark: '#5A4FCF',
      light: '#A29BFE',
    },
    background: {
      default: '#0F1419', // Very dark background
      paper: '#1A1F29',   // Card background
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#8B949E',
    },
    success: {
      main: '#00D4AA',
      dark: '#00B894',
    },
    error: {
      main: '#FF6B6B',
      dark: '#E55656',
    },
    divider: '#2D3748',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.75rem',
      lineHeight: 1.4,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1A1F29',
          border: '1px solid #2D3748',
          borderRadius: '12px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1A1F29',
          backgroundImage: 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          textTransform: 'none',
          fontWeight: 600,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(0, 212, 170, 0.3)',
          },
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#0F1419',
          borderRight: '1px solid #2D3748',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          margin: '4px 8px',
          '&.Mui-selected': {
            backgroundColor: 'rgba(0, 212, 170, 0.1)',
            '&:hover': {
              backgroundColor: 'rgba(0, 212, 170, 0.15)',
            },
          },
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
          },
        },
      },
    },
  },
});

const drawerWidth = 280;

// Navigation items matching the sidebar in the image
const navigationItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, id: 'dashboard' },
  { text: 'Portfolio', icon: <PortfolioIcon />, id: 'portfolio' },
  { text: 'Live Trades', icon: <LiveTradesIcon />, id: 'live-trades' },
  { text: 'TradingView Charts', icon: <TradingViewIcon />, id: 'charts' },
  { text: 'Crypto Heatmap', icon: <HeatmapIcon />, id: 'heatmap' },
  { text: 'Backtesting', icon: <BacktestingIcon />, id: 'backtesting' },
  { text: 'Trade History', icon: <TradeHistoryIcon />, id: 'history' },
  { text: 'Strategy Generator', icon: <StrategyGeneratorIcon />, id: 'strategy' },
  { text: 'Settings', icon: <SettingsIcon />, id: 'settings' },
  { text: 'Login', icon: <SettingsIcon />, id: 'login' }, // Add login nav
];

const App: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [selectedView, setSelectedView] = useState('dashboard');

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (viewId: string) => {
    setSelectedView(viewId);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const renderContent = () => {
    switch (selectedView) {
      case 'dashboard':
        return <DashboardView />;
      case 'portfolio':
        return <PortfolioView />;
      case 'charts':
        return <TradingChartsView />;
      case 'heatmap':
        return <CryptoHeatmapView />;
      case 'login':
        return <LoginPage />;
      default:
        return <DashboardView />;
    }
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo/Brand */}
      <Box sx={{ p: 3, borderBottom: '1px solid #2D3748' }}>
        <Typography variant="h5" sx={{ 
          color: 'primary.main', 
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}>
          <Box sx={{ 
            width: 8, 
            height: 8, 
            bgcolor: 'primary.main', 
            borderRadius: '50%',
            animation: 'pulse 2s infinite'
          }} />
          AlgoBot
        </Typography>
      </Box>

      {/* Navigation */}
      <List sx={{ flex: 1, pt: 2 }}>
        {navigationItems.map((item) => (
          <ListItem key={item.id} disablePadding>
            <ListItemButton
              selected={selectedView === item.id}
              onClick={() => handleNavigation(item.id)}
              sx={{
                '& .MuiListItemIcon-root': {
                  color: selectedView === item.id ? 'primary.main' : 'text.secondary',
                },
                '& .MuiListItemText-primary': {
                  color: selectedView === item.id ? 'primary.main' : 'text.primary',
                  fontWeight: selectedView === item.id ? 600 : 400,
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                primaryTypographyProps={{
                  fontSize: '0.875rem',
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      {/* Version info */}
      <Box sx={{ p: 2, borderTop: '1px solid #2D3748' }}>
        <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.75rem' }}>
          Version 3.10 | Full App
        </Typography>
      </Box>
    </Box>
  );

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        {/* Mobile AppBar */}
        {isMobile && (
          <AppBar
            position="fixed"
            sx={{
              width: '100%',
              bgcolor: 'background.default',
              borderBottom: '1px solid #2D3748',
              boxShadow: 'none',
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
                onClick={handleDrawerToggle}
                sx={{ mr: 2 }}
              >
                <MenuIcon />
              </IconButton>
              <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 700 }}>
                AlgoBot
              </Typography>
            </Toolbar>
          </AppBar>
        )}

        {/* Sidebar Navigation */}
        <Box
          component="nav"
          sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        >
          <Drawer
            variant={isMobile ? 'temporary' : 'permanent'}
            open={isMobile ? mobileOpen : true}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true, // Better open performance on mobile
            }}
            sx={{
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: drawerWidth,
                border: 'none',
              },
            }}
          >
            {drawer}
          </Drawer>
        </Box>

        {/* Main content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            width: { md: `calc(100% - ${drawerWidth}px)` },
            mt: { xs: 7, md: 0 },
            bgcolor: 'background.default',
            minHeight: '100vh',
          }}
        >
          {renderContent()}
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default App;
