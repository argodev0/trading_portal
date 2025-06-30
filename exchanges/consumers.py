import json
import asyncio
import logging
import ccxt
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .services import APIKeyManager

logger = logging.getLogger(__name__)

class BalanceConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time balance updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Check if user is authenticated
            if self.scope["user"] == AnonymousUser():
                await self.close()
                return
            
            self.user = self.scope["user"]
            self.group_name = f"balances_{self.user.id}"
            
            # Join balance updates group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Start balance monitoring
            asyncio.create_task(self.balance_monitor())
            
            logger.info(f"Balance WebSocket connected for user {self.user.username}")
            
        except Exception as e:
            logger.error(f"Error connecting balance WebSocket: {e}")
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            # Leave balance updates group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info(f"Balance WebSocket disconnected for user {self.user.username}")
        except Exception as e:
            logger.error(f"Error disconnecting balance WebSocket: {e}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'refresh_balances':
                # Trigger immediate balance refresh
                await self.send_balance_update()
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def balance_monitor(self):
        """Monitor balances and send updates"""
        while True:
            try:
                await self.send_balance_update()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Error in balance monitor: {e}")
                break
    
    async def send_balance_update(self):
        """Fetch and send current balance data"""
        try:
            # Fetch balances using the service
            balances = await self.get_user_balances()
            
            # Send balance update
            await self.send(text_data=json.dumps({
                'type': 'balance_update',
                'data': balances,
                'timestamp': datetime.now().isoformat()
            }))
            
        except Exception as e:
            logger.error(f"Error sending balance update: {e}")
    
    @database_sync_to_async
    def get_user_balances(self):
        """Get user balances (database sync to async)"""
        try:
            api_key_manager = APIKeyManager()
            return api_key_manager.fetch_user_balances(self.user)
        except Exception as e:
            logger.error(f"Error fetching user balances: {e}")
            return []
    
    # Handle group messages
    async def balance_broadcast(self, event):
        """Handle balance broadcast from group"""
        await self.send(text_data=json.dumps(event))


class PriceConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time price updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        try:
            # Join price updates group
            self.group_name = "prices"
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Start price monitoring
            asyncio.create_task(self.price_monitor())
            
            logger.info("Price WebSocket connected")
            
        except Exception as e:
            logger.error(f"Error connecting price WebSocket: {e}")
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            # Leave price updates group
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            logger.info("Price WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting price WebSocket: {e}")
    
    async def price_monitor(self):
        """Monitor crypto prices and send updates"""
        import ccxt
        
        while True:
            try:
                # Get prices from multiple exchanges
                prices = await self.get_crypto_prices()
                
                # Send price update
                await self.send(text_data=json.dumps({
                    'type': 'price_update',
                    'data': prices,
                    'timestamp': datetime.now().isoformat()
                }))
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in price monitor: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    async def get_crypto_prices(self):
        """Fetch current cryptocurrency prices"""
        try:
            # Initialize exchanges
            exchanges = {
                'binance': ccxt.binance({'enableRateLimit': True}),
                'kucoin': ccxt.kucoin({'enableRateLimit': True})
            }
            
            symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
            prices = {}
            
            for exchange_name, exchange in exchanges.items():
                try:
                    for symbol in symbols:
                        ticker = exchange.fetch_ticker(symbol)
                        key = f"{exchange_name}_{symbol.replace('/', '_')}"
                        prices[key] = {
                            'exchange': exchange_name.title(),
                            'symbol': symbol,
                            'price': ticker['last'],
                            'change': ticker.get('change'),
                            'percentage': ticker.get('percentage')
                        }
                except Exception as e:
                    logger.error(f"Error fetching prices from {exchange_name}: {e}")
                    continue
            
            return prices
            
        except Exception as e:
            logger.error(f"Error getting crypto prices: {e}")
            return {}
    
    # Handle group messages
    async def price_broadcast(self, event):
        """Handle price broadcast from group"""
        await self.send(text_data=json.dumps(event))
