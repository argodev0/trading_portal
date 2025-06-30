import jwt
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    """JWT authentication middleware for WebSocket connections"""
    
    async def __call__(self, scope, receive, send):
        # Get token from query parameters
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if token:
            try:
                # Decode JWT token
                payload = jwt.decode(
                    token, 
                    settings.SECRET_KEY, 
                    algorithms=['HS256']
                )
                user_id = payload.get('user_id')
                
                if user_id:
                    try:
                        user = await self.get_user(user_id)
                        scope['user'] = user
                    except User.DoesNotExist:
                        scope['user'] = AnonymousUser()
                else:
                    scope['user'] = AnonymousUser()
            except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, user_id):
        """Get user from database"""
        return User.objects.get(id=user_id)
