from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    LoginSerializer,
    UserProfileSerializer
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer that includes user info"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['account_tier'] = user.account_tier
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user info to response
        data['user'] = {
            'id': str(self.user.id),
            'username': self.user.username,
            'email': self.user.email,
            'account_tier': self.user.account_tier,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view"""
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh view"""
    pass


class UserRegistrationView(generics.CreateAPIView):
    """API view for user registration"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API view for user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    """API view for logout (blacklist refresh token)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'message': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)
            else:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def protected_view(request):
    """Test view to verify JWT authentication"""
    return Response({
        'message': 'Hello, authenticated user!',
        'user': {
            'id': str(request.user.id),
            'username': request.user.username,
            'account_tier': request.user.account_tier,
        }
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_info(request):
    """API information endpoint"""
    return Response({
        'message': 'Trading Portal API',
        'version': '1.0',
        'authentication': 'JWT',
        'endpoints': {
            'token_obtain': '/api/auth/token/',
            'token_refresh': '/api/auth/token/refresh/',
            'register': '/api/auth/register/',
            'profile': '/api/auth/profile/',
            'logout': '/api/auth/logout/',
            'protected': '/api/auth/protected/',
        }
    })
