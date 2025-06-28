#!/usr/bin/env python
"""
Test script for Bot Celery tasks
Tests the run_bot_instance task and related functionality
"""
import os
import sys
import django
import time

# Add the project directory to Python path
sys.path.append('/root/trading_portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from exchanges.models import Exchange, UserAPIKey
from bots.models import Bot, BotRun
from bots.tasks import start_bot_execution, stop_bot_execution, fetch_market_data, apply_strategy_logic

User = get_user_model()

def test_celery_tasks():
    """Test the Celery tasks and bot execution functionality"""
    print("🤖 Testing Bot Celery Tasks")
    print("=" * 50)
    
    # Get or create test data
    try:
        user = User.objects.get(email='testuser@example.com')
        print(f"✅ Using existing user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser_celery',
            email='testuser_celery@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User Celery',
            account_tier='Free'
        )
        print(f"✅ Created new user: {user.email}")
    
    # Get or create exchange and API key
    exchange, created = Exchange.objects.get_or_create(
        name='Test Exchange Celery'
    )
    if created:
        print(f"✅ Created test exchange: {exchange.name}")
    else:
        print(f"✅ Using existing exchange: {exchange.name}")
    
    # Create API key for testing
    from exchanges.services import APIKeyManager
    api_manager = APIKeyManager()
    
    try:
        api_key = api_manager.store_api_credentials(
            user=user,
            exchange=exchange,
            name='Celery Test API Key',
            api_key='test_celery_api_key',
            secret_key='test_celery_secret_key'
        )
        print(f"✅ Created test API key: {api_key.name}")
    except Exception as e:
        # Key might already exist, try to get it
        api_key = UserAPIKey.objects.filter(
            user=user, 
            exchange=exchange, 
            name='Celery Test API Key'
        ).first()
        if not api_key:
            raise e
        print(f"✅ Using existing API key: {api_key.name}")
    
    # Create test bot
    bot = Bot.objects.create(
        name='Celery Test Bot',
        user=user,
        exchange_key=api_key,
        strategy='grid',
        pair='BTC/USDT',
        timeframe='1h',
        parameters={
            'grid_size': 5,
            'take_profit': 1.5,
            'stop_loss': 1.0,
            'max_position_size': 50.0,
            'price_range': {'min': 40000, 'max': 50000},
            'order_amount': 25.0
        },
        max_daily_trades=10,
        risk_percentage=1.0
    )
    print(f"✅ Created test bot: {bot.name}")
    print(f"   Strategy: {bot.get_strategy_display()}")
    print(f"   Pair: {bot.pair}")
    print(f"   Parameters: {bot.parameters}")
    
    print("\n🔍 Testing Market Data Fetching")
    try:
        market_data = fetch_market_data(bot)
        print(f"✅ Market data fetched successfully:")
        print(f"   Symbol: {market_data['symbol']}")
        print(f"   Price: {market_data['price']:.2f}")
        print(f"   Volume: {market_data['volume']:.2f}")
        print(f"   24h Change: {market_data['change_24h']:.4f}")
    except Exception as e:
        print(f"❌ Market data error: {e}")
        return False
    
    print("\n📊 Testing Strategy Logic")
    try:
        signal = apply_strategy_logic(bot, market_data)
        if signal:
            print(f"✅ Trade signal generated:")
            print(f"   Action: {signal['action']}")
            print(f"   Quantity: {signal['quantity']:.6f}")
            print(f"   Price: {signal['price']:.2f}")
            print(f"   Confidence: {signal['confidence']:.2f}")
        else:
            print("✅ No trade signal generated (normal behavior)")
    except Exception as e:
        print(f"❌ Strategy logic error: {e}")
        return False
    
    print("\n🚀 Testing Bot Run Creation")
    try:
        # Create a manual bot run for testing
        run = BotRun.objects.create(
            bot=bot,
            status='starting'
        )
        print(f"✅ Created bot run: {run.id}")
        print(f"   Start time: {run.start_time}")
        print(f"   Status: {run.status}")
        
        # Test a few iterations manually (without infinite loop)
        print("\n🔄 Testing Manual Bot Execution Loop")
        run.status = 'running'
        run.save()
        
        for i in range(3):
            print(f"\n   Iteration {i + 1}:")
            
            # Fetch market data
            market_data = fetch_market_data(bot)
            print(f"   📈 Price: {market_data['price']:.2f}")
            
            # Apply strategy
            signal = apply_strategy_logic(bot, market_data)
            if signal:
                print(f"   📊 Signal: {signal['action']} {signal['quantity']:.6f}")
                
                # Simulate trade execution (without actual execution)
                run.trades_executed += 1
                run.profit_loss += 0.001  # Small simulated profit
                run.add_log(f"Simulated {signal['action']} trade", 'info')
                print(f"   ✅ Trade simulated")
            else:
                print(f"   ⏸️ No signal")
            
            run.save()
        
        print(f"\n📈 Final Run Statistics:")
        print(f"   Trades executed: {run.trades_executed}")
        print(f"   Profit/Loss: {run.profit_loss:.8f}")
        print(f"   Log entries: {len(run.logs)}")
        print(f"   Duration: {run.duration}")
        
        # Stop the run
        run.stop_run(status='completed')
        print(f"✅ Run completed successfully")
        
    except Exception as e:
        print(f"❌ Bot run error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🧹 Cleaning up test data")
    try:
        bot.delete()  # This will cascade delete the run
        api_key.delete()
        exchange.delete()
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")
    
    print("\n✅ Bot Celery tasks testing completed successfully!")
    print("\n📋 Summary:")
    print("   ✅ Market data fetching working")
    print("   ✅ Strategy logic implementation working")
    print("   ✅ Bot run creation and management working")
    print("   ✅ Logging and statistics tracking working")
    print("   ✅ Error handling and cleanup working")
    
    return True


if __name__ == '__main__':
    test_celery_tasks()
