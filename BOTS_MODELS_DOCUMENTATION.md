# Bot Models Documentation

## Overview
The `bots` app provides models for managing trading bots and tracking their execution runs. It includes comprehensive logging, performance tracking, and admin interface integration.

## Models

### Bot Model
Represents a trading bot configuration with all necessary parameters for automated trading.

#### Fields

**Basic Information:**
- `id` (UUIDField): Primary key, auto-generated UUID
- `name` (CharField): User-friendly name for the bot (max 100 chars)
- `user` (ForeignKey): Owner of the bot (links to custom User model)
- `status` (CharField): Current bot status (inactive/active/paused/error)
- `is_active` (BooleanField): Whether the bot is currently running

**Trading Configuration:**
- `exchange_key` (ForeignKey): API key to use for trading (links to UserAPIKey)
- `strategy` (CharField): Trading strategy type (grid, dca, scalping, etc.)
- `pair` (CharField): Trading pair (e.g., 'BTC/USDT', 'ETH/BTC')
- `timeframe` (CharField): Strategy execution timeframe (1m, 5m, 1h, etc.)
- `parameters` (JSONField): Strategy-specific parameters

**Risk Management:**
- `max_daily_trades` (PositiveIntegerField): Maximum trades per day (default: 10)
- `risk_percentage` (DecimalField): Risk per trade as percentage (0.01-100.00)

**Timestamps:**
- `created_at` (DateTimeField): When the bot was created
- `updated_at` (DateTimeField): Last modification time

#### Strategy Choices
- `grid`: Grid Trading
- `dca`: Dollar Cost Averaging
- `scalping`: Scalping
- `momentum`: Momentum Trading
- `mean_reversion`: Mean Reversion
- `arbitrage`: Arbitrage
- `custom`: Custom Strategy

#### Timeframe Choices
- `1m`: 1 Minute
- `5m`: 5 Minutes
- `15m`: 15 Minutes
- `30m`: 30 Minutes
- `1h`: 1 Hour
- `4h`: 4 Hours
- `1d`: 1 Day
- `1w`: 1 Week

#### Methods
- `get_current_run()`: Returns the currently active BotRun or None
- `get_total_runs()`: Returns total number of runs for this bot
- `get_successful_runs()`: Returns number of completed runs
- `clean()`: Validates that exchange_key belongs to the same user

#### Example Parameters JSON
```json
{
  "grid_size": 10,
  "take_profit": 2.0,
  "stop_loss": 1.0,
  "max_position_size": 100.0,
  "price_range": {"min": 30000, "max": 50000},
  "order_amount": 50.0
}
```

### BotRun Model
Logs each execution session of a bot, tracking performance and runtime data.

#### Fields

**Basic Information:**
- `id` (UUIDField): Primary key, auto-generated UUID
- `bot` (ForeignKey): The bot this run belongs to
- `status` (CharField): Current run status

**Timing:**
- `start_time` (DateTimeField): When the run started (auto-set)
- `end_time` (DateTimeField): When the run ended (nullable)

**Performance:**
- `trades_executed` (PositiveIntegerField): Number of trades executed
- `profit_loss` (DecimalField): P&L for this run (15 digits, 8 decimal places)

**Logging:**
- `logs` (JSONField): Array of log entries with timestamps
- `error_message` (TextField): Error details if run failed

**Timestamps:**
- `created_at` (DateTimeField): Record creation time
- `updated_at` (DateTimeField): Last update time

#### Status Choices
- `starting`: Bot is initializing
- `running`: Bot is actively trading
- `stopping`: Bot is shutting down
- `completed`: Run finished successfully
- `failed`: Run ended with errors
- `cancelled`: Run was manually stopped

#### Properties
- `duration`: Human-readable duration string (e.g., "2h 30m 15s")
- `is_running`: Boolean indicating if run is active

#### Methods
- `stop_run(status, error_message)`: Stop the run with given status
- `add_log(message, level)`: Add a timestamped log entry

#### Example Log Entry
```json
[
  {
    "timestamp": "2025-06-28T00:25:54.250000+00:00",
    "level": "info",
    "message": "Bot started successfully"
  },
  {
    "timestamp": "2025-06-28T00:26:15.123000+00:00",
    "level": "warning",
    "message": "Market volatility detected"
  }
]
```

## Relationships

### Bot → User
- **Type**: Many-to-One (ForeignKey)
- **Constraint**: Each user can have multiple bots
- **Unique**: Bot names must be unique per user
- **Cascade**: Bots are deleted when user is deleted

### Bot → UserAPIKey
- **Type**: Many-to-One (ForeignKey)
- **Validation**: API key must belong to the same user as the bot
- **Cascade**: Bots are deleted when API key is deleted

### BotRun → Bot
- **Type**: Many-to-One (ForeignKey)
- **Relationship**: Each bot can have multiple runs
- **Cascade**: Runs are deleted when bot is deleted

## Database Constraints

### Unique Constraints
- `unique_bot_name_per_user`: Ensures bot names are unique per user

### Indexes
- `bot + start_time`: For efficient run queries per bot
- `status`: For filtering runs by status
- `start_time`: For chronological ordering

### Validators
- `max_daily_trades`: Minimum value of 1
- `risk_percentage`: Minimum value of 0.01

## Usage Examples

### Creating a Bot
```python
from bots.models import Bot
from exchanges.models import UserAPIKey

# Get user's API key
api_key = UserAPIKey.objects.get(user=user, name='My Binance Key')

# Create grid trading bot
bot = Bot.objects.create(
    name='BTC Grid Bot',
    user=user,
    exchange_key=api_key,
    strategy='grid',
    pair='BTC/USDT',
    timeframe='1h',
    parameters={
        'grid_size': 20,
        'take_profit': 1.5,
        'stop_loss': 2.0,
        'price_range': {'min': 40000, 'max': 60000}
    },
    max_daily_trades=50,
    risk_percentage=1.0
)
```

### Starting a Bot Run
```python
from bots.models import BotRun

# Start a new run
run = BotRun.objects.create(
    bot=bot,
    status='starting'
)

# Update status and add logs
run.status = 'running'
run.add_log('Grid orders placed successfully', 'info')
run.trades_executed = 1
run.profit_loss = 0.00050000
run.save()
```

### Stopping a Bot Run
```python
# Stop run successfully
run.stop_run(status='completed')

# Stop run with error
run.stop_run(status='failed', error_message='API connection lost')
```

### Querying Bot Performance
```python
# Get bot statistics
bot = Bot.objects.get(name='BTC Grid Bot')
total_runs = bot.get_total_runs()
successful_runs = bot.get_successful_runs()
success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0

# Get total P&L
total_pnl = sum(run.profit_loss for run in bot.runs.all())

# Get current run
current_run = bot.get_current_run()
if current_run:
    print(f"Bot running for {current_run.duration}")
```

## Admin Interface Features

### Bot Admin
- **List View**: Shows bot name, user, strategy, status, and performance metrics
- **Filters**: Strategy, status, timeframe, exchange, creation date
- **Search**: Name, user, pair, exchange
- **Actions**: Activate, deactivate, pause bots
- **Detailed View**: Current run info, statistics, formatted parameters

### BotRun Admin
- **List View**: Shows bot, timing, status, trades, and P&L
- **Filters**: Status, start time, strategy, user, exchange
- **Search**: Bot name, user, pair, error messages
- **Actions**: Stop runs, mark as completed/failed
- **Detailed View**: Bot config, formatted logs, performance data

## Security Considerations

1. **User Isolation**: Bots can only use API keys belonging to the same user
2. **Validation**: Clean method ensures proper user-API key relationships
3. **Cascade Protection**: Proper foreign key relationships prevent orphaned records
4. **Parameter Storage**: JSON parameters allow flexible strategy configuration
5. **Audit Trail**: Complete logging of all bot activities and runs

## Performance Optimizations

1. **Database Indexes**: Optimized for common query patterns
2. **Select Related**: Admin queries use select_related for efficiency
3. **Prefetch Related**: Runs are prefetched when needed
4. **JSON Storage**: Parameters stored efficiently as JSON
5. **Computed Properties**: Duration and statistics calculated on-demand
