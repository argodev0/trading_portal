# AI Strategy Generator Service Documentation

## Overview

The AI Strategy Generator Service is a powerful component of the Trading Portal that uses Google's Gemini AI with code execution capabilities to generate custom trading strategies based on natural language prompts.

## Features

### ✨ Core Capabilities
- **Natural Language Input**: Describe your strategy in plain English
- **AI-Powered Generation**: Uses Google Gemini 1.5 Pro with code execution tools
- **Automatic Validation**: Built-in code validation and syntax checking
- **Strategy Management**: Full CRUD operations for generated strategies
- **Performance Tracking**: Monitor usage, validation status, and performance metrics
- **Generation Logging**: Complete audit trail of all generation attempts

### 🏗️ Architecture

```
User Prompt → Gemini API → Code Extraction → Validation → Storage → Execution
```

## Models

### GeneratedStrategy
Stores AI-generated trading strategies with metadata.

**Key Fields:**
- `user`: Strategy owner
- `name`: Human-readable strategy name
- `original_prompt`: User's input prompt
- `generated_code`: AI-generated Python code
- `strategy_type`: Category (trend_following, mean_reversion, etc.)
- `status`: Current status (draft, validated, active, archived, error)
- `validation_results`: Code validation results
- `parameters`: Strategy configuration
- `performance_metrics`: Backtesting/live performance data
- `usage_count`: Number of times used

### StrategyGenerationLog
Logs all strategy generation attempts for debugging and analytics.

**Key Fields:**
- `user`: User who initiated generation
- `strategy`: Associated strategy (if successful)
- `prompt`: Original input prompt
- `status`: Generation result (success, failure, partial)
- `ai_response_raw`: Full AI response
- `extracted_code`: Extracted Python code
- `error_message`: Error details if failed
- `processing_time_seconds`: Generation duration
- `tokens_used`: API tokens consumed

## API Endpoints

### 🎯 Strategy Generation
```http
POST /api/strategies/generate/
```

**Request:**
```json
{
    "prompt": "Create a RSI-based strategy for scalping",
    "name": "RSI Scalping Strategy",
    "strategy_type": "scalping",
    "validate_code": true
}
```

**Response:**
```json
{
    "success": true,
    "message": "Strategy generated successfully",
    "data": {
        "id": "uuid",
        "name": "RSI Scalping Strategy",
        "generated_code": "def execute_strategy(...)...",
        "status": "validated",
        "validation_results": {...}
    },
    "generation_log_id": "uuid",
    "processing_time_seconds": 2.5
}
```

### 📋 List Strategies
```http
GET /api/strategies/
```

**Query Parameters:**
- `status`: Filter by status (draft, validated, active, archived)
- `type`: Filter by strategy type
- `page`: Page number for pagination
- `page_size`: Items per page

**Response:**
```json
{
    "success": true,
    "count": 10,
    "next": "http://...",
    "previous": null,
    "data": [
        {
            "id": "uuid",
            "name": "Strategy Name",
            "strategy_type": "trend_following",
            "status": "validated",
            "created_at": "2025-06-28T00:00:00Z",
            "usage_count": 5,
            "code_preview": "def execute_strategy..."
        }
    ]
}
```

### 🔍 Strategy Details
```http
GET /api/strategies/{strategy_id}/
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "name": "Strategy Name",
        "description": "Strategy description",
        "original_prompt": "User's original prompt",
        "generated_code": "Complete Python code",
        "strategy_type": "trend_following",
        "status": "validated",
        "validation_results": {
            "valid": true,
            "errors": [],
            "warnings": [],
            "has_function": true,
            "trading_keywords": ["signal", "buy", "sell"]
        },
        "parameters": {},
        "performance_metrics": {},
        "created_at": "2025-06-28T00:00:00Z",
        "usage_count": 5
    }
}
```

### ✏️ Update Strategy
```http
PUT /api/strategies/{strategy_id}/
```

### 🗑️ Delete Strategy
```http
DELETE /api/strategies/{strategy_id}/
```

### ✅ Validate Code
```http
POST /api/strategies/validate/
```

**Request:**
```json
{
    "code": "def execute_strategy(market_data, params): ..."
}
```

**Response:**
```json
{
    "success": true,
    "validation_results": {
        "valid": true,
        "errors": [],
        "warnings": [],
        "has_function": true,
        "has_imports": true,
        "trading_keywords": ["signal", "strategy"],
        "syntax_valid": true
    }
}
```

### 📊 Generation Logs
```http
GET /api/strategies/generation-logs/
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# AI Strategy Generator Configuration
# Get your API key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
```

### Django Settings

The strategies app is automatically configured when added to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'strategies',
]
```

## Usage Examples

### 1. Basic Strategy Generation

```python
from strategies.services import generate_strategy_code

prompt = """
Create a simple moving average strategy that:
1. Uses 20 and 50 period MAs
2. Buys when short MA crosses above long MA
3. Sells when short MA crosses below long MA
4. Includes 2% stop loss and 5% take profit
"""

try:
    code = generate_strategy_code(prompt)
    print("Generated strategy code:")
    print(code)
except StrategyGeneratorError as e:
    print(f"Generation failed: {e}")
```

### 2. Manual Strategy Creation

```python
from strategies.models import GeneratedStrategy
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='trader@example.com')

strategy = GeneratedStrategy.objects.create(
    user=user,
    name="Custom RSI Strategy",
    original_prompt="RSI-based momentum strategy",
    generated_code=strategy_code,
    strategy_type='momentum',
    status='draft'
)
```

### 3. Strategy Validation

```python
from strategies.services import validate_generated_strategy

validation = validate_generated_strategy(strategy_code)
if validation['valid']:
    print("Strategy is valid!")
    strategy.status = 'validated'
    strategy.save()
else:
    print(f"Validation errors: {validation['errors']}")
```

## Generated Strategy Format

The AI generates strategies following this template:

```python
def execute_strategy(market_data: dict, strategy_params: dict) -> dict:
    """
    Trading strategy implementation
    
    Args:
        market_data (dict): Current market data including OHLCV
        strategy_params (dict): Strategy configuration parameters
        
    Returns:
        dict: Trading signal with action, confidence, and metadata
    """
    
    # Strategy logic here
    
    return {
        'action': 'buy|sell|hold',
        'confidence': 0.85,  # 0.0 to 1.0
        'reason': 'Description of why this signal was generated',
        'metadata': {
            'indicators': {...},
            'stop_loss_price': 45000,
            'take_profit_price': 47000,
            'risk_level': 'medium'
        }
    }
```

## Integration with Trading Bots

Generated strategies can be directly used with the existing bot system:

```python
from bots.models import Bot
from strategies.models import GeneratedStrategy

# Get a validated strategy
strategy = GeneratedStrategy.objects.get(
    id='strategy-uuid',
    status='validated'
)

# Create a bot using the generated strategy
bot = Bot.objects.create(
    user=user,
    name="AI Generated Bot",
    exchange_key=api_key,
    strategy='custom',  # Use custom strategy type
    pair='BTC/USDT',
    timeframe='1h',
    parameters={
        'strategy_code': strategy.generated_code,
        'strategy_id': str(strategy.id),
        # ... other parameters
    }
)
```

## Testing

Run the comprehensive test suite:

```bash
# Test the strategy generator service
./ops.sh strategies

# Or run directly
python test_strategy_generator.py
```

## Security Considerations

1. **API Key Security**: Store Gemini API key securely in environment variables
2. **Code Validation**: All generated code is validated before storage
3. **User Isolation**: Users can only access their own strategies
4. **Rate Limiting**: Consider implementing API rate limiting for generation endpoints
5. **Code Execution**: Generated code should be sandboxed when executed

## Monitoring & Analytics

### Key Metrics to Track
- Strategy generation success rate
- Average processing time
- Most popular strategy types
- User adoption and usage patterns
- API costs and token consumption

### Admin Interface
- View all generated strategies
- Monitor generation logs
- Track validation results
- Manage strategy status

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   StrategyGeneratorError: GEMINI_API_KEY not found
   ```
   **Solution**: Add `GEMINI_API_KEY` to your `.env` file

2. **Invalid Code Generated**
   ```
   Validation errors: ['Syntax error: invalid syntax']
   ```
   **Solution**: Review the prompt and try again, or manually fix the code

3. **Import Errors in Generated Code**
   ```
   ModuleNotFoundError: No module named 'pandas'
   ```
   **Solution**: Ensure required packages are installed (`pandas`, `numpy`, etc.)

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.getLogger('strategies').setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Strategy Backtesting**: Automatic backtesting of generated strategies
2. **Strategy Templates**: Pre-built templates for common patterns
3. **Community Sharing**: Public strategy marketplace
4. **Performance Analytics**: Advanced performance tracking and optimization
5. **Multi-Model Support**: Support for other AI models (Claude, GPT, etc.)
6. **Strategy Optimization**: AI-powered parameter optimization

---

## Quick Start Checklist

- [ ] Get Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- [ ] Add `GEMINI_API_KEY` to `.env` file
- [ ] Run migrations: `python manage.py migrate`
- [ ] Test the service: `./ops.sh strategies`
- [ ] Try generating your first strategy via API
- [ ] Integrate with existing trading bots

**Status**: ✅ FULLY IMPLEMENTED AND TESTED
**Last Updated**: June 28, 2025
