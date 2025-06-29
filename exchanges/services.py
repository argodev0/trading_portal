"""
Encryption services for the exchanges app
"""
import os
import json
import base64
import time
import ccxt
from typing import Dict, Tuple, Any, List
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)

class APIKeyManager:
    """
    Manage API keys for different exchanges
    """

    def __init__(self, exchange_id: str, api_key: str, secret: str, password: str = None):
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.secret = secret
        self.password = password
        self.exchange = self._initialize_exchange()

    def _initialize_exchange(self):
        """
        Initialize the exchange class from ccxt
        """
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            return exchange_class({
                'apiKey': self.api_key,
                'secret': self.secret,
                'password': self.password,
            })
        except Exception as e:
            logger.error(f"Error initializing exchange {self.exchange_id}: {str(e)}")
            raise

    def fetch_balance(self):
        """
        Fetch balance from the exchange
        """
        try:
            balance = self.exchange.fetch_balance()
            logger.info(f"Balance for {self.exchange_id}: {balance}")
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance from {self.exchange_id}: {str(e)}")
            raise

    def update_api_credentials(self, user_api_key: 'UserAPIKey', api_key: str, secret_key: str) -> 'UserAPIKey':
        """
        Update existing API credentials with new encrypted values
        
        Args:
            user_api_key: UserAPIKey instance to update
            api_key (str): New public API key
            secret_key (str): New secret API key
            
        Returns:
            UserAPIKey: Updated UserAPIKey instance
        """
        # Encrypt new credentials
        encrypted_blob, nonce = self.encryptor.encrypt(api_key, secret_key)
        
        # Update the instance
        user_api_key.api_key_public_part = api_key
        user_api_key.encrypted_credentials = encrypted_blob
        user_api_key.nonce = nonce
        user_api_key.save()
        
        return user_api_key

    def get_exchange_client(self, user_api_key: 'UserAPIKey'):
        """
        Create a ccxt exchange client using stored API credentials
        
        Args:
            user_api_key: UserAPIKey instance
            
        Returns:
            ccxt.Exchange: Configured exchange client
        """
        # Get decrypted credentials
        credentials = self.retrieve_api_credentials(user_api_key)
        
        # Map exchange names to ccxt classes
        exchange_map = {
            'binance': ccxt.binance,
            'coinbase': ccxt.coinbase,
            'kraken': ccxt.kraken,
            'okx': ccxt.okx,
            'bybit': ccxt.bybit,
            'kucoin': ccxt.kucoin,
            # Add more exchanges as needed
        }
        
        exchange_name = user_api_key.exchange.name.lower()
        if exchange_name not in exchange_map:
            raise ValueError(f"Exchange {exchange_name} not supported")
        
        # Create exchange client
        exchange_class = exchange_map[exchange_name]
        client = exchange_class({
            'apiKey': credentials['api_key'],
            'secret': credentials['secret_key'],
            'sandbox': False,  # Set to True for testing
            'enableRateLimit': True,
        })
        
        return client

    def fetch_user_balances(self, user) -> List[Dict[str, Any]]:
        """
        Fetch balances from all exchanges for a user
        
        Args:
            user: User instance
            
        Returns:
            List[Dict]: List of balance data from all exchanges
        """
        from .models import UserAPIKey
        
        all_balances = []
        user_api_keys = UserAPIKey.objects.filter(user=user, is_active=True)
        
        for user_api_key in user_api_keys:
            try:
                # Get exchange client
                client = self.get_exchange_client(user_api_key)
                
                # Fetch balance
                balance = client.fetch_balance()
                
                # Format balance data
                for currency, amounts in balance.items():
                    if currency == 'info':  # Skip raw API response
                        continue
                    
                    free = amounts.get('free', 0)
                    used = amounts.get('used', 0)
                    total = amounts.get('total', 0)
                    
                    if total > 0:  # Only include currencies with balance
                        all_balances.append({
                            'exchange': user_api_key.exchange.name,
                            'exchangeName': user_api_key.exchange.name,
                            'walletType': 'Spot',  # Default to spot
                            'asset': currency,
                            'free': float(free) if free else 0.0,
                            'used': float(used) if used else 0.0,
                            'total': float(total) if total else 0.0,
                            'value': float(total) if total else 0.0,  # For compatibility
                        })
                        
            except Exception as e:
                logger.error(f"Error fetching balance for {user_api_key.exchange.name}: {e}")
                # Continue with other exchanges even if one fails
                continue
        
        return all_balances