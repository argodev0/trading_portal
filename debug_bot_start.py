#!/usr/bin/env python
"""
Debug script to find the 'bool' object is not callable error.
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

from bots.models import Bot, BotRun
from django.contrib.auth import get_user_model
from exchanges.models import Exchange, UserAPIKey

User = get_user_model()

def debug_bot_start():
    """Debug the bot start process step by step."""
    
    print("🔍 Debugging Bot Start Process")
    print("=" * 40)
    
    # Get existing test bot
    try:
        bot = Bot.objects.first()
        if bot:
            print(f"✅ Found test bot: {bot.name}")
            print(f"   Bot ID: {bot.id}")
            print(f"   Bot status: {bot.status}")
            print(f"   Bot is_active field: {bot.is_active}")
            
            # Test the has_active_runs method
            print(f"   Bot has_active_runs(): {bot.has_active_runs()}")
            
            # Test getting current run
            current_run = bot.get_current_run()
            print(f"   Current run: {current_run}")
            
            # Try creating a BotRun
            print("\n🔧 Testing BotRun creation...")
            bot_run = BotRun.objects.create(
                bot=bot,
                status='starting',
                run_parameters={'test': True},
                notes='Debug test run'
            )
            print(f"✅ Created BotRun: {bot_run.id}")
            
            # Test if bot now has active runs
            print(f"   Bot has_active_runs() after creation: {bot.has_active_runs()}")
            
            # Clean up
            bot_run.delete()
            print("🧹 Cleaned up test BotRun")
            
        else:
            print("❌ No bots found in database")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_bot_start()
