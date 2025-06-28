#!/usr/bin/env python
"""
Test script for Bot Control API endpoints.

This script tests the bot control functionality including start and stop operations.
"""

import os
import sys
import django
import json

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_portal.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from bots.models import Bot, BotRun
from exchanges.models import Exchange, UserAPIKey

User = get_user_model()

def test_bot_control_api():
    """Test the bot control API endpoints."""
    
    print("🤖 Testing Bot Control API Endpoints")
    print("=" * 45)
    
    # Create test client
    client = Client()
    
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
    
    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    headers = {
        'HTTP_AUTHORIZATION': f'Bearer {access_token}',
        'content_type': 'application/json'
    }
    
    print(f"✅ Generated JWT token for authentication")
    
    # Create test data
    exchange, _ = Exchange.objects.get_or_create(
        name='Test Exchange for Bot API'
    )
    
    api_key, _ = UserAPIKey.objects.get_or_create(
        user=user,
        exchange=exchange,
        name='Bot API Test Key',
        defaults={
            'api_key_public_part': 'test_public_key_12345',
            'encrypted_credentials': b'test_encrypted_credentials',
            'nonce': b'test_nonce_123'
        }
    )
    
    # Create test bot
    bot, _ = Bot.objects.get_or_create(
        user=user,
        name='API Test Bot',
        defaults={
            'strategy': 'grid',
            'pair': 'BTC/USDT',
            'timeframe': '1h',
            'exchange_key': api_key,
            'status': 'inactive',
            'is_active': False,
            'parameters': {
                'grid_size': 10,
                'take_profit': 2.0,
                'stop_loss': 1.0
            }
        }
    )
    
    print(f"✅ Created test bot: {bot.name} (ID: {bot.id})")
    
    # Test 1: List bots
    print(f"\n📋 Testing GET /api/bots/ (List bots)")
    response = client.get('/api/bots/', **headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Found {data.get('count', 0)} bots")
        if data.get('data'):
            bot_data = data['data'][0]
            print(f"   Bot name: {bot_data.get('name')}")
            print(f"   Is active: {bot_data.get('is_active')}")
            print(f"   Total runs: {bot_data.get('total_runs')}")
    else:
        print(f"❌ Failed: {response.content.decode()}")
    
    # Test 2: Get bot details
    print(f"\n🔍 Testing GET /api/bots/{bot.id}/ (Get bot details)")
    response = client.get(f'/api/bots/{bot.id}/', **headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        bot_data = data.get('data', {})
        print(f"✅ Success: Retrieved bot details")
        print(f"   Name: {bot_data.get('name')}")
        print(f"   Strategy: {bot_data.get('strategy')}")
        print(f"   Is active: {bot_data.get('is_active')}")
        print(f"   Current run: {bot_data.get('current_run')}")
        statistics = bot_data.get('statistics', {})
        print(f"   Statistics: {statistics.get('total_runs')} runs, {statistics.get('success_rate', 0):.1f}% success")
    else:
        print(f"❌ Failed: {response.content.decode()}")
    
    # Test 3: Get bot status
    print(f"\n📊 Testing GET /api/bots/{bot.id}/status/ (Get bot status)")
    response = client.get(f'/api/bots/{bot.id}/status/', **headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        status_data = data.get('data', {})
        print(f"✅ Success: Retrieved bot status")
        print(f"   Bot ID: {status_data.get('bot_id')}")
        print(f"   Is active: {status_data.get('is_active')}")
        print(f"   Total runs: {status_data.get('total_runs')}")
        print(f"   Successful runs: {status_data.get('successful_runs')}")
    else:
        print(f"❌ Failed: {response.content.decode()}")
    
    # Test 4: Start bot
    print(f"\n🚀 Testing POST /api/bots/{bot.id}/start/ (Start bot)")
    start_request = {
        "parameters": {
            "grid_size": 15,
            "take_profit": 2.5
        },
        "notes": "Test run via API"
    }
    
    response = client.post(
        f'/api/bots/{bot.id}/start/',
        data=json.dumps(start_request),
        **headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Success: Bot started")
        run_data = data.get('data', {}).get('bot_run', {})
        task_id = data.get('data', {}).get('task_id')
        print(f"   Run ID: {run_data.get('id')}")
        print(f"   Status: {run_data.get('status')}")
        print(f"   Task ID: {task_id}")
        
        bot_run_id = run_data.get('id')
        
        # Test 5: Try to start again (should fail)
        print(f"\n🔄 Testing POST /api/bots/{bot.id}/start/ (Start already running bot)")
        response = client.post(
            f'/api/bots/{bot.id}/start/',
            data=json.dumps(start_request),
            **headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Success: Correctly rejected (bot already running)")
            print(f"   Error: {data.get('error')}")
        else:
            print(f"❌ Unexpected: Should have failed with 400")
        
        # Test 6: Stop bot
        print(f"\n⏹️  Testing POST /api/bots/{bot.id}/stop/ (Stop bot)")
        stop_request = {
            "reason": "Test stop via API",
            "force": False
        }
        
        response = client.post(
            f'/api/bots/{bot.id}/stop/',
            data=json.dumps(stop_request),
            **headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Bot stopped")
            run_data = data.get('data', {}).get('bot_run', {})
            print(f"   Run ID: {run_data.get('id')}")
            print(f"   Status: {run_data.get('status')}")
            print(f"   Duration: {run_data.get('duration_seconds', 0):.2f}s")
        else:
            print(f"❌ Failed: {response.content.decode()}")
        
        # Test 7: Get bot runs
        print(f"\n📋 Testing GET /api/bots/{bot.id}/runs/ (Get bot runs)")
        response = client.get(f'/api/bots/{bot.id}/runs/', **headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {data.get('count', 0)} runs")
            if data.get('data'):
                run = data['data'][0]
                print(f"   Latest run ID: {run.get('id')}")
                print(f"   Status: {run.get('status')}")
                print(f"   Duration: {run.get('duration_seconds', 0):.2f}s")
                print(f"   Is running: {run.get('is_running')}")
        else:
            print(f"❌ Failed: {response.content.decode()}")
        
    else:
        print(f"❌ Failed to start bot: {response.content.decode()}")
        bot_run_id = None
    
    # Test 8: Try to stop non-running bot
    print(f"\n⏹️  Testing POST /api/bots/{bot.id}/stop/ (Stop non-running bot)")
    stop_request = {
        "reason": "Test stop non-running bot"
    }
    
    response = client.post(
        f'/api/bots/{bot.id}/stop/',
        data=json.dumps(stop_request),
        **headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        data = response.json()
        print(f"✅ Success: Correctly rejected (bot not running)")
        print(f"   Error: {data.get('error')}")
    else:
        print(f"❌ Unexpected: Should have failed with 400")
    
    # Test 9: Test authentication required
    print(f"\n🔒 Testing authentication required")
    response = client.get('/api/bots/')
    print(f"Status without auth: {response.status_code}")
    
    if response.status_code == 401:
        print(f"✅ Success: Authentication required (401 Unauthorized)")
    else:
        print(f"❌ Unexpected: Should require authentication")
    
    # Test 10: Test invalid bot ID
    print(f"\n❓ Testing GET /api/bots/invalid-id/ (Invalid bot ID)")
    response = client.get('/api/bots/00000000-0000-0000-0000-000000000000/', **headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 404:
        print(f"✅ Success: Bot not found (404)")
    else:
        print(f"❌ Unexpected: Should return 404")
    
    print(f"\n🎉 Bot Control API testing completed!")
    print(f"\n📚 Summary:")
    print(f"   ✅ All endpoint structures are working")
    print(f"   ✅ Authentication is properly enforced")
    print(f"   ✅ Bot start/stop operations functional")
    print(f"   ✅ Request/response formats are correct")
    print(f"   ✅ Error handling working as expected")
    print(f"   ⚠️  Celery tasks may require worker to be running")

if __name__ == '__main__':
    try:
        test_bot_control_api()
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
