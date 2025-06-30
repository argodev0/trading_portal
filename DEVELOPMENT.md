# Trading Portal Development Guide

## Architecture Overview

This project is configured to run as a **static React application** in production, served by nginx. Django is **only used for development and testing**.

## Production (Live Site)
- **Frontend**: Static React app served by nginx
- **Backend**: None (static files only)
- **Features**: Limited to static content and client-side functionality
- **Location**: `/var/www/trading-portal/` served by nginx

## Development & Testing
- **Frontend**: React development server (`npm start`)
- **Backend**: Django development server (`python manage.py runserver`)
- **Features**: Full API functionality, authentication, real-time data
- **Database**: SQLite (for development only)

## Getting Started for Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis (for development features)

### Setup Development Environment

1. **Clone and navigate to project**:
   ```bash
   cd /root/trading_portal
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Configure environment variables**:
   - Copy `.env` file and configure with your API keys
   - Environment variables are loaded from `/root/trading_portal/.env`

5. **Initialize Django database**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Optional: for admin access
   ```

### Running in Development Mode

1. **Start Django backend** (Terminal 1):
   ```bash
   cd /root/trading_portal
   source .venv/bin/activate
   python manage.py runserver 127.0.0.1:8000
   ```

2. **Start React frontend** (Terminal 2):
   ```bash
   cd /root/trading_portal/frontend
   npm start
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Django Admin: http://localhost:8000/admin
   - API: http://localhost:8000/api

### Available Development Features

When Django backend is running, you have access to:
- ✅ User authentication and login
- ✅ Real exchange balance fetching (via ccxt)
- ✅ Exchange connection status monitoring
- ✅ Real-time event logs with connection status
- ✅ API endpoints for data retrieval
- ✅ Django admin interface
- ✅ Database persistence

### Exchange Connection Monitoring

The application includes real-time monitoring of exchange API connections:

**Production Mode (Static Site):**
- Shows simulated connection status for demo purposes
- Displays "Demo Mode" indicators
- Connection status updates every 30 seconds (simulated)

**Development Mode (Django Backend):**
- Tests actual API connections to Binance and KuCoin
- Measures connection latency
- Shows real error messages if connections fail
- API endpoints: `/api/exchanges/binance/status/` and `/api/exchanges/kucoin/status/`

**Event Logs:**
- Real-time connection status updates
- Color-coded log levels (INFO, SUCCESS, ERROR, WARNING)
- Automatic scrolling with last 10 events
- Timestamps for all events

### Production Deployment

To deploy updates to the live site:

1. **Build the frontend**:
   ```bash
   cd /root/trading_portal/frontend
   npm run build
   ```

2. **Deploy to nginx**:
   ```bash
   cp -r dist/* /var/www/trading-portal/
   ```

3. **Restart nginx** (if needed):
   ```bash
   sudo systemctl reload nginx
   ```

## Important Notes

- ⚠️ **Never run Django in production**: The live site should only serve static files
- 🔒 **API keys**: Keep exchange API keys secure and only in the `.env` file
- 🗄️ **Database**: SQLite is used for development; no database needed for production
- 📝 **Logs**: Check Django logs when developing: `python manage.py runserver --verbosity=2`

## File Structure

```
/root/trading_portal/
├── .env                    # Environment variables (development)
├── manage.py              # Django management
├── requirements.txt       # Python dependencies
├── frontend/              # React application
│   ├── src/
│   ├── package.json
│   └── dist/             # Built files (for production)
├── exchanges/            # Django app for exchange integration
├── trading_portal/       # Django project settings
└── /var/www/trading-portal/  # Production files (nginx)
```

## Troubleshooting

### Common Issues

1. **"Authentication is only available in development mode"**
   - This is expected in production. Start Django backend for full features.

2. **API calls returning 404**
   - Normal in production. Start Django backend to enable API endpoints.

3. **Environment variables not loading**
   - Ensure `.env` file exists in `/root/trading_portal/.env`
   - Restart Django server after changing environment variables

4. **Exchange API errors**
   - Check API keys in `.env` file
   - Verify exchange API credentials and permissions
   - Check Django logs for detailed error messages

### Development vs Production Behavior

| Feature | Development (Django + React) | Production (Static React) |
|---------|------------------------------|---------------------------|
| Authentication | ✅ Full login system | ❌ Disabled |
| API Endpoints | ✅ All endpoints available | ❌ Returns 404 |
| Real-time Data | ✅ Live exchange data | ❌ Disabled |
| Database | ✅ SQLite persistence | ❌ No database |
| Admin Interface | ✅ Django admin at /admin | ❌ Not available |

This architecture ensures the live site is fast, secure, and doesn't require a backend server, while providing full development capabilities when needed.
