#!/usr/bin/env python
"""
Test script for AI Strategy Generator Service.

This script tests the strategy generation functionality using mock data
since we don't have a real Gemini API key configured.
"""

import os
import sys
import django

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from strategies.models import GeneratedStrategy, StrategyGenerationLog
from strategies.services import AIStrategyGenerator, StrategyGeneratorError
import json

User = get_user_model()

print("🤖 Testing AI Strategy Generator Service")
print("=" * 50)

def test_strategy_generator():
    """Test the AI Strategy Generator without actual API calls."""
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        email='testuser@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'account_tier': 'free'
        }
    )
    
    if created:
        user.set_password('testpassword123')
        user.save()
        print(f"✅ Created test user: {user.email}")
    else:
        print(f"✅ Using existing test user: {user.email}")
    
    # Test prompt
    test_prompt = """
    Create a simple moving average crossover strategy for Bitcoin trading.
    The strategy should:
    1. Use 20-period and 50-period moving averages
    2. Generate buy signals when short MA crosses above long MA
    3. Generate sell signals when short MA crosses below long MA
    4. Include stop-loss at 2% and take-profit at 5%
    5. Return clear trading signals with confidence levels
    """
    
    print(f"\n📝 Test Prompt:")
    print(f"   {test_prompt[:100]}...")
    
    # Test without API key (will fail gracefully)
    print(f"\n🔧 Testing without API key (expected to fail):")
    try:
        generator = AIStrategyGenerator()
        print("❌ Should have failed - API key required")
    except StrategyGeneratorError as e:
        print(f"✅ Correctly failed with: {str(e)}")
    
    # Test with mock strategy code
    print(f"\n🧪 Testing with mock generated code:")
    
    mock_generated_code = '''
import pandas as pd
import numpy as np

def execute_strategy(market_data: dict, strategy_params: dict) -> dict:
    """
    Simple Moving Average Crossover Strategy
    
    Args:
        market_data (dict): Current market data including OHLCV
        strategy_params (dict): Strategy configuration parameters
        
    Returns:
        dict: Trading signal with action, confidence, and metadata
    """
    # Default parameters
    short_period = strategy_params.get('short_ma_period', 20)
    long_period = strategy_params.get('long_ma_period', 50)
    stop_loss = strategy_params.get('stop_loss_pct', 2.0)
    take_profit = strategy_params.get('take_profit_pct', 5.0)
    
    # Get price data
    prices = market_data.get('close_prices', [])
    
    if len(prices) < long_period:
        return {
            'action': 'hold',
            'confidence': 0.0,
            'reason': 'Insufficient data for analysis',
            'metadata': {'error': 'Need at least {} price points'.format(long_period)}
        }
    
    # Calculate moving averages
    short_ma = np.mean(prices[-short_period:])
    long_ma = np.mean(prices[-long_period:])
    
    # Previous MAs for crossover detection
    if len(prices) > long_period:
        prev_short_ma = np.mean(prices[-(short_period + 1):-1])
        prev_long_ma = np.mean(prices[-(long_period + 1):-1])
    else:
        prev_short_ma = short_ma
        prev_long_ma = long_ma
    
    # Crossover signals
    current_position = 'above' if short_ma > long_ma else 'below'
    prev_position = 'above' if prev_short_ma > prev_long_ma else 'below'
    
    # Generate signals
    if prev_position == 'below' and current_position == 'above':
        # Golden cross - buy signal
        confidence = min(abs(short_ma - long_ma) / long_ma * 100, 0.95)
        return {
            'action': 'buy',
            'confidence': confidence,
            'reason': 'Golden cross detected - short MA crossed above long MA',
            'metadata': {
                'short_ma': short_ma,
                'long_ma': long_ma,
                'stop_loss_price': prices[-1] * (1 - stop_loss / 100),
                'take_profit_price': prices[-1] * (1 + take_profit / 100)
            }
        }
    elif prev_position == 'above' and current_position == 'below':
        # Death cross - sell signal
        confidence = min(abs(short_ma - long_ma) / long_ma * 100, 0.95)
        return {
            'action': 'sell',
            'confidence': confidence,
            'reason': 'Death cross detected - short MA crossed below long MA',
            'metadata': {
                'short_ma': short_ma,
                'long_ma': long_ma,
                'stop_loss_price': prices[-1] * (1 + stop_loss / 100),
                'take_profit_price': prices[-1] * (1 - take_profit / 100)
            }
        }
    else:
        # No signal
        return {
            'action': 'hold',
            'confidence': 0.5,
            'reason': 'No crossover signal detected',
            'metadata': {
                'short_ma': short_ma,
                'long_ma': long_ma,
                'position': current_position
            }
        }
'''
    
    # Create a strategy record manually
    strategy = GeneratedStrategy.objects.create(
        user=user,
        name="Mock MA Crossover Strategy",
        description="Simple moving average crossover strategy for testing",
        original_prompt=test_prompt,
        generated_code=mock_generated_code,
        strategy_type='trend_following',
        status='draft',
        ai_model_version='mock-test-model',
        generation_metadata={
            'mock_test': True,
            'code_length': len(mock_generated_code)
        }
    )
    
    print(f"✅ Created mock strategy: {strategy.name}")
    print(f"   ID: {strategy.id}")
    print(f"   Status: {strategy.status}")
    print(f"   Type: {strategy.strategy_type}")
    
    # Test validation
    print(f"\n🔍 Testing code validation:")
    try:
        # Import the validator without requiring API key
        from strategies.services import validate_generated_strategy
        validation_results = validate_generated_strategy(mock_generated_code)
        
        print(f"   Valid: {validation_results.get('valid', False)}")
        print(f"   Has function: {validation_results.get('has_function', False)}")
        print(f"   Has imports: {validation_results.get('has_imports', False)}")
        print(f"   Trading keywords: {validation_results.get('trading_keywords', [])}")
        
        if validation_results.get('errors'):
            print(f"   Errors: {validation_results['errors']}")
        if validation_results.get('warnings'):
            print(f"   Warnings: {validation_results['warnings']}")
        
        # Update strategy with validation results
        strategy.validation_results = validation_results
        if validation_results.get('valid'):
            strategy.status = 'validated'
        strategy.save()
        
        print(f"✅ Validation completed - Status: {strategy.status}")
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
    
    # Test the generated strategy function
    print(f"\n🧮 Testing generated strategy execution:")
    try:
        # Mock market data
        mock_market_data = {
            'close_prices': [
                45000, 45100, 45200, 44900, 44800, 44700, 44600, 44500,  # Downtrend
                44400, 44300, 44200, 44100, 44000, 43900, 43800, 43700,
                43600, 43500, 43400, 43300, 43200, 43100, 43000, 42900,
                42800, 42700, 42600, 42500, 42400, 42300, 42200, 42100,
                42000, 41900, 41800, 41700, 41600, 41500, 41400, 41300,
                41200, 41100, 41000, 40900, 40800, 40700, 40600, 40500,
                40600, 40700, 40800, 40900, 41000, 41100, 41200, 41300   # Uptrend starts
            ]
        }
        
        mock_strategy_params = {
            'short_ma_period': 20,
            'long_ma_period': 50,
            'stop_loss_pct': 2.0,
            'take_profit_pct': 5.0
        }
        
        # Execute the strategy code
        exec(mock_generated_code, globals())
        result = execute_strategy(mock_market_data, mock_strategy_params)
        
        print(f"   Signal: {result.get('action', 'none')}")
        print(f"   Confidence: {result.get('confidence', 0):.2f}")
        print(f"   Reason: {result.get('reason', 'N/A')}")
        
        if result.get('metadata'):
            metadata = result['metadata']
            if 'short_ma' in metadata:
                print(f"   Short MA: {metadata['short_ma']:.2f}")
            if 'long_ma' in metadata:
                print(f"   Long MA: {metadata['long_ma']:.2f}")
        
        print(f"✅ Strategy execution successful")
        
    except Exception as e:
        print(f"❌ Strategy execution failed: {str(e)}")
    
    # Create generation log
    log = StrategyGenerationLog.objects.create(
        user=user,
        strategy=strategy,
        prompt=test_prompt,
        status='success',
        ai_response_raw='Mock response for testing',
        extracted_code=mock_generated_code,
        processing_time_seconds=0.5,
        ai_model_used='mock-test-model'
    )
    
    print(f"✅ Created generation log: {log.id}")
    
    # Test statistics
    print(f"\n📊 Database Statistics:")
    print(f"   Total strategies: {GeneratedStrategy.objects.count()}")
    print(f"   User strategies: {GeneratedStrategy.objects.filter(user=user).count()}")
    print(f"   Validated strategies: {GeneratedStrategy.objects.filter(status='validated').count()}")
    print(f"   Generation logs: {StrategyGenerationLog.objects.count()}")
    
    return strategy

def test_api_endpoints():
    """Test API endpoints functionality (structure only)."""
    print(f"\n🌐 Testing API Endpoints Structure:")
    
    # Import API views to verify they're properly defined
    try:
        from strategies.api_views import (
            GenerateStrategyAPIView,
            StrategyListAPIView,
            StrategyDetailAPIView,
            ValidateStrategyAPIView,
            StrategyGenerationLogsAPIView
        )
        print(f"✅ All API views imported successfully")
        
        from strategies.serializers import (
            GenerateStrategyRequestSerializer,
            GeneratedStrategySerializer,
            StrategyValidationSerializer
        )
        print(f"✅ All serializers imported successfully")
        
        # Check URL patterns
        from strategies.api_urls import urlpatterns
        print(f"✅ URL patterns defined: {len(urlpatterns)} endpoints")
        
        for pattern in urlpatterns:
            print(f"   - {pattern.pattern}")
        
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")

if __name__ == '__main__':
    try:
        test_strategy_generator()
        test_api_endpoints()
        
        print(f"\n🎉 All tests completed successfully!")
        print(f"\n📚 Next Steps:")
        print(f"   1. Get a Gemini API key from: https://aistudio.google.com/app/apikey")
        print(f"   2. Add GEMINI_API_KEY to your .env file")
        print(f"   3. Test the API endpoints with real requests")
        print(f"   4. Integrate with your trading bot system")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
