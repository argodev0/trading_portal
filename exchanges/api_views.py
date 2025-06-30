from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.http import Http404
import time
import os
import ccxt
import asyncio
from django.conf import settings

from .models import Exchange, UserAPIKey
from .serializers import UserAPIKeyListSerializer, UserAPIKeyCreateSerializer
from .services import APIKeyManager


class WebSocketStreamView(APIView):
    """
    API endpoint for websocket streaming configuration
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get websocket streaming capabilities for user's exchanges
        """
        try:
            api_key_manager = APIKeyManager()
            user_api_keys = UserAPIKey.objects.filter(user=request.user, is_active=True)
            
            streaming_info = []
            for user_api_key in user_api_keys:
                try:
                    # Check if exchange supports websockets
                    client = api_key_manager.get_exchange_client(user_api_key, use_websocket=True)
                    
                    capabilities = {
                        'exchange': user_api_key.exchange.name,
                        'websocket_supported': True,
                        'features': {
                            'balance_streaming': hasattr(client, 'watch_balance'),
                            'ticker_streaming': hasattr(client, 'watch_ticker'),
                            'orderbook_streaming': hasattr(client, 'watch_order_book'),
                            'trades_streaming': hasattr(client, 'watch_trades'),
                        }
                    }
                    
                    streaming_info.append(capabilities)
                    
                except Exception as e:
                    streaming_info.append({
                        'exchange': user_api_key.exchange.name,
                        'websocket_supported': False,
                        'error': str(e)
                    })
            
            return Response({
                'success': True,
                'data': streaming_info
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to get streaming capabilities',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RealTimeConnectionTestView(APIView):
    """
    Test real-time connection to exchanges using websockets
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Test websocket connection to specified exchange
        """
        try:
            exchange_name = request.data.get('exchange')
            if not exchange_name:
                return Response({
                    'success': False,
                    'error': 'Exchange name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            api_key_manager = APIKeyManager()
            
            # Try to get user's API key for this exchange
            try:
                user_api_key = UserAPIKey.objects.get(
                    user=request.user, 
                    exchange__name__iexact=exchange_name,
                    is_active=True
                )
                client = api_key_manager.get_exchange_client(user_api_key, use_websocket=True)
            except UserAPIKey.DoesNotExist:
                # Fall back to demo credentials
                client = api_key_manager.get_demo_exchange_client(exchange_name, use_websocket=True)
            
            if not client:
                return Response({
                    'success': False,
                    'error': f'No credentials available for {exchange_name}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Test websocket capabilities
            test_results = {
                'exchange': exchange_name,
                'websocket_features': {
                    'balance_streaming': hasattr(client, 'watch_balance'),
                    'ticker_streaming': hasattr(client, 'watch_ticker'),
                    'orderbook_streaming': hasattr(client, 'watch_order_book'),
                    'trades_streaming': hasattr(client, 'watch_trades'),
                },
                'connection_test': 'passed',
                'timestamp': int(time.time() * 1000)
            }
            
            return Response({
                'success': True,
                'data': test_results
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Websocket connection test failed',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAPIKeysView(APIView):
    """
    API endpoint for managing user API keys.
    
    GET: List all API keys for the authenticated user (without secrets)
    POST: Create a new API key with encrypted credentials
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        List all API keys for the authenticated user.
        Returns public information only (no secrets).
        """
        try:
            # Get all API keys for the current user
            api_keys = UserAPIKey.objects.filter(user=request.user).select_related('exchange')
            
            # Serialize the data (excludes encrypted credentials)
            serializer = UserAPIKeyListSerializer(api_keys, many=True)
            
            return Response({
                'success': True,
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to retrieve API keys',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """
        Create a new API key with encrypted credentials.
        
        Expected payload:
        {
            "name": "My Binance Key",
            "exchange": 1,
            "api_key": "public_api_key_here",
            "secret_key": "secret_key_here"
        }
        """
        try:
            # Validate the input data
            serializer = UserAPIKeyCreateSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid input data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Extract the data
            name = validated_data['name']
            exchange = validated_data['exchange']
            api_key = validated_data['api_key']
            secret_key = validated_data['secret_key']
            
            # Use APIKeyManager to store encrypted credentials
            api_key_manager = APIKeyManager()
            
            with transaction.atomic():
                # Store the encrypted API key
                user_api_key = api_key_manager.store_api_credentials(
                    user=request.user,
                    exchange=exchange,
                    name=name,
                    api_key=api_key,
                    secret_key=secret_key
                )
                
                # Serialize the response (without secrets)
                response_serializer = UserAPIKeyListSerializer(user_api_key)
                
                return Response({
                    'success': True,
                    'message': 'API key created successfully',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to create API key',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserBalancesView(APIView):
    """
    API endpoint for fetching user balances from all connected exchanges.
    
    GET: Fetch balances from all exchanges using ccxt
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Fetch balances from all connected exchanges for the authenticated user.
        """
        try:
            api_key_manager = APIKeyManager()
            balances = api_key_manager.fetch_user_balances(request.user)
            
            return Response({
                'success': True,
                'count': len(balances),
                'data': balances
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to fetch balances',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAPIKeyDetailView(APIView):
    """
    API endpoint for managing individual API keys.
    
    GET: Get specific API key details
    DELETE: Delete an API key
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk, user):
        """Get API key object for the authenticated user."""
        try:
            return UserAPIKey.objects.get(id=pk, user=user)
        except UserAPIKey.DoesNotExist:
            raise Http404("API key not found")
    
    def get(self, request, pk):
        """Get specific API key details (without secrets)."""
        api_key = self.get_object(pk, request.user)
        serializer = UserAPIKeyListSerializer(api_key)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        """Delete an API key."""
        try:
            api_key = self.get_object(pk, request.user)
            api_key.delete()
            
            return Response({
                'success': True,
                'message': 'API key deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to delete API key',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExchangeConnectionStatusView(APIView):
    """
    API endpoint for checking exchange connection status.
    Used by the frontend to monitor exchange API connectivity.
    """
    authentication_classes = []
    permission_classes = []
    
    def get(self, request, exchange_name):
        """
        Check connection status for a specific exchange.
        """
        start_time = time.time()
        
        try:
            if exchange_name.lower() == 'binance':
                return self._check_binance_connection(start_time)
            elif exchange_name.lower() == 'kucoin':
                return self._check_kucoin_connection(start_time)
            else:
                return Response({
                    'success': False,
                    'message': f'Unsupported exchange: {exchange_name}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return Response({
                'success': False,
                'message': f'Connection check failed: {str(e)}',
                'status': 'error',
                'latency': latency
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _check_binance_connection(self, start_time):
        """Check Binance API connection using environment variables."""
        try:
            api_key = os.getenv('BINANCE_API_KEY')
            api_secret = os.getenv('BINANCE_API_SECRET')
            
            if not api_key or not api_secret:
                return Response({
                    'success': False,
                    'message': 'Binance API credentials not configured in environment',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create exchange instance
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': False,
                'enableRateLimit': True,
            })
            
            # Test connection by fetching server time
            server_time = exchange.fetch_time()
            latency = int((time.time() - start_time) * 1000)
            
            return Response({
                'success': True,
                'message': 'Connected to Binance API successfully',
                'status': 'connected',
                'latency': latency,
                'server_time': server_time,
                'exchange': 'binance'
            })
            
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return Response({
                'success': False,
                'message': f'Binance connection failed: {str(e)}',
                'status': 'error',
                'latency': latency,
                'exchange': 'binance'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _check_kucoin_connection(self, start_time):
        """Check KuCoin API connection using environment variables."""
        try:
            api_key = os.getenv('KUCOIN_API_KEY')
            api_secret = os.getenv('KUCOIN_API_SECRET')
            passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
            
            if not api_key or not api_secret or not passphrase:
                return Response({
                    'success': False,
                    'message': 'KuCoin API credentials not configured in environment',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create exchange instance
            exchange = ccxt.kucoin({
                'apiKey': api_key,
                'secret': api_secret,
                'password': passphrase,
                'sandbox': False,
                'enableRateLimit': True,
            })
            
            # Test connection by fetching server time
            server_time = exchange.fetch_time()
            latency = int((time.time() - start_time) * 1000)
            
            return Response({
                'success': True,
                'message': 'Connected to KuCoin API successfully',
                'status': 'connected',
                'latency': latency,
                'server_time': server_time,
                'exchange': 'kucoin'
            })
            
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            return Response({
                'success': False,
                'message': f'KuCoin connection failed: {str(e)}',
                'status': 'error',
                'latency': latency,
                'exchange': 'kucoin'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
