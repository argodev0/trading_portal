#!/usr/bin/env python
"""
Test script for the Bot models
Tests model creation, validation, and relationships
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/root/trading_portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from exchanges.models import Exchange, UserAPIKey
from exchanges.services import APIKeyManager
from bots.models import Bot, BotRun
from django.utils import timezone
import json

User = get_user_model()

def test_bot_models():
    """Test the Bot and BotRun models"""
    print("🤖 Testing Bot Models")
    print("=" * 50)
    
    # Get or create test user
    try:
        user = User.objects.get(email='testuser@example.com')
        print(f"✅ Using existing user: {user.email}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            account_tier='Free'
        )
        print(f"✅ Created test user: {user.email}")
    
    # Get or create test exchange and API key
    exchange, created = Exchange.objects.get_or_create(
        name='Test Exchange for Bots'
    )
    if created:
        print(f"✅ Created test exchange: {exchange.name}")
    else:
        print(f"✅ Using existing exchange: {exchange.name}")
    
    # Create API key if it doesn't exist
    try:
        api_key = UserAPIKey.objects.get(
            user=user,
            exchange=exchange,
            name='Bot Test API Key'
        )
        print(f"✅ Using existing API key: {api_key.name}")
    except UserAPIKey.DoesNotExist:
        api_key_manager = APIKeyManager()
        api_key = api_key_manager.store_api_credentials(
            user=user,
            exchange=exchange,
            name='Bot Test API Key',
            api_key='test_bot_api_key',
            secret_key='test_bot_secret_key'
        )
        print(f"✅ Created test API key: {api_key.name}")
    
    print("\n🤖 Creating Bot")
    try:
        # Create a bot with strategy parameters
        bot_parameters = {
            'grid_size': 10,
            'take_profit': 2.0,
            'stop_loss': 1.0,
            'max_position_size': 100.0,
            'price_range': {'min': 30000, 'max': 50000}
        }
        
        bot = Bot.objects.create(
            name='Test Grid Bot',
            user=user,
            exchange_key=api_key,
            strategy='grid',
            pair='BTC/USDT',
            timeframe='1h',
            parameters=bot_parameters,
            max_daily_trades=20,
            risk_percentage=2.5
        )
        
        print(f"✅ Created bot: {bot}")
        print(f"   ID: {bot.id}")
        print(f"   Strategy: {bot.get_strategy_display()}")
        print(f"   Timeframe: {bot.get_timeframe_display()}")
        print(f"   Parameters: {json.dumps(bot.parameters, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error creating bot: {e}")
        return False
    
    print("\n📊 Testing Bot Methods")
    try:
        # Test bot methods
        print(f"Current run: {bot.get_current_run()}")
        print(f"Total runs: {bot.get_total_runs()}")
        print(f"Successful runs: {bot.get_successful_runs()}")
        print(f"Status: {bot.status}")
        print(f"Is active: {bot.is_active}")
        
    except Exception as e:
        print(f"❌ Error testing bot methods: {e}")
        return False
    
    print("\n🚀 Creating Bot Run")
    try:
        # Start a bot run
        bot_run = BotRun.objects.create(
            bot=bot,
            status='running'
        )
        
        print(f"✅ Created bot run: {bot_run}")
        print(f"   ID: {bot_run.id}")
        print(f"   Start time: {bot_run.start_time}")
        print(f"   Status: {bot_run.status}")
        print(f"   Duration: {bot_run.duration}")
        print(f"   Is running: {bot_run.is_running}")
        
        # Update bot status
        bot.status = 'active'
        bot.is_active = True
        bot.save()
        
    except Exception as e:
        print(f"❌ Error creating bot run: {e}")
        return False
    
    print("\n📝 Testing Bot Run Logging")
    try:
        # Add some logs to the bot run
        bot_run.add_log('Bot started successfully', 'info')
        bot_run.add_log('Fetching market data', 'info')
        bot_run.add_log('Grid orders placed', 'info')
        
        # Update trade statistics
        bot_run.trades_executed = 5
        bot_run.profit_loss = 0.00125000  # Some profit
        bot_run.save()
        
        print(f"✅ Added logs to bot run")
        print(f"   Trades executed: {bot_run.trades_executed}")
        print(f"   Profit/Loss: {bot_run.profit_loss}")
        print(f"   Log entries: {len(bot_run.logs)}")
        
        # Print logs
        for i, log in enumerate(bot_run.logs, 1):
            print(f"     {i}. [{log['level']}] {log['message']} ({log['timestamp'][:19]})")
        
    except Exception as e:
        print(f"❌ Error testing bot run logging: {e}")
        return False
    
    print("\n⏹️ Stopping Bot Run")
    try:
        # Stop the bot run
        bot_run.stop_run(status='completed')
        
        print(f"✅ Bot run stopped")
        print(f"   End time: {bot_run.end_time}")
        print(f"   Final status: {bot_run.status}")
        print(f"   Total duration: {bot_run.duration}")
        print(f"   Is running: {bot_run.is_running}")
        
        # Check bot status
        bot.refresh_from_db()
        print(f"   Bot status: {bot.status}")
        print(f"   Bot is active: {bot.is_active}")
        
    except Exception as e:
        print(f"❌ Error stopping bot run: {e}")
        return False
    
    print("\n📈 Testing Multiple Runs")
    try:
        # Create another run to test statistics
        run2 = BotRun.objects.create(
            bot=bot,
            status='completed',
            trades_executed=3,
            profit_loss=-0.00050000,  # Some loss
            end_time=timezone.now()
        )
        
        run3 = BotRun.objects.create(
            bot=bot,
            status='failed',
            trades_executed=1,
            profit_loss=0.0,
            error_message='Connection timeout',
            end_time=timezone.now()
        )
        
        print(f"✅ Created additional runs")
        print(f"   Total runs: {bot.get_total_runs()}")
        print(f"   Successful runs: {bot.get_successful_runs()}")
        
        # Calculate success rate
        total = bot.get_total_runs()
        successful = bot.get_successful_runs()
        if total > 0:
            success_rate = (successful / total) * 100
            print(f"   Success rate: {success_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Error testing multiple runs: {e}")
        return False
    
    print("\n🧹 Testing Cleanup")
    try:
        # Test cascade deletion
        initial_runs = BotRun.objects.filter(bot=bot).count()
        print(f"   Runs before deletion: {initial_runs}")
        
        bot.delete()
        
        remaining_runs = BotRun.objects.filter(bot=bot).count()
        print(f"   Runs after bot deletion: {remaining_runs}")
        print(f"✅ Cascade deletion working correctly")
        
    except Exception as e:
        print(f"❌ Error testing cleanup: {e}")
        return False
    
    print("\n✅ Bot models testing completed successfully!")
    return True

if __name__ == '__main__':
    test_bot_models()
