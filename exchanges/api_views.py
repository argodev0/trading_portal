from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.http import Http404

from .models import Exchange, UserAPIKey
from .serializers import UserAPIKeyListSerializer, UserAPIKeyCreateSerializer
from .services import APIKeyManager


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
                
        except ValueError as e:
            return Response({
                'success': False,
                'error': 'Encryption failed',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to create API key',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAPIKeyDetailView(APIView):
    """
    API endpoint for managing individual API keys.
    
    GET: Retrieve a specific API key (without secrets)
    DELETE: Delete a specific API key
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk, user):
        """Get API key object for the authenticated user"""
        try:
            return UserAPIKey.objects.get(pk=pk, user=user)
        except UserAPIKey.DoesNotExist:
            raise Http404("API key not found")
    
    def get(self, request, pk):
        """Get details of a specific API key (without secrets)"""
        try:
            api_key = self.get_object(pk, request.user)
            serializer = UserAPIKeyListSerializer(api_key)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({
                'success': False,
                'error': 'API key not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to retrieve API key',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, pk):
        """Delete a specific API key"""
        try:
            api_key = self.get_object(pk, request.user)
            api_key_name = api_key.name
            api_key.delete()
            
            return Response({
                'success': True,
                'message': f'API key "{api_key_name}" deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({
                'success': False,
                'error': 'API key not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to delete API key',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
