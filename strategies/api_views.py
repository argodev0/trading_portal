"""
API views for the strategies app.
"""

import time
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.utils import timezone

from .models import GeneratedStrategy, StrategyGenerationLog
from .services import AIStrategyGenerator, StrategyGeneratorError
from .serializers import (
    GenerateStrategyRequestSerializer,
    GeneratedStrategySerializer,
    GeneratedStrategyListSerializer,
    StrategyGenerationLogSerializer,
    StrategyValidationSerializer,
    StrategyValidationResponseSerializer
)

logger = logging.getLogger(__name__)


class StrategyPagination(PageNumberPagination):
    """Custom pagination for strategy listings."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class GenerateStrategyAPIView(APIView):
    """
    API endpoint for generating new trading strategies using AI.
    
    POST /api/strategies/generate/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Generate a new trading strategy based on user prompt."""
        serializer = GenerateStrategyRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        prompt = serializer.validated_data['prompt']
        strategy_name = serializer.validated_data.get('name', '')
        strategy_type = serializer.validated_data.get('strategy_type', 'custom')
        validate_code = serializer.validated_data.get('validate_code', True)
        
        # Initialize generation log
        generation_log = StrategyGenerationLog.objects.create(
            user=request.user,
            prompt=prompt,
            status='failure'  # Will be updated on success
        )
        
        start_time = time.time()
        
        try:
            # Generate strategy using AI
            logger.info(f"Generating strategy for user {request.user.email}")
            generator = AIStrategyGenerator()
            generated_code = generator.generate_strategy_code(prompt)
            
            processing_time = time.time() - start_time
            
            # Update generation log with raw response
            generation_log.ai_response_raw = str(generated_code)
            generation_log.extracted_code = generated_code
            generation_log.processing_time_seconds = processing_time
            generation_log.ai_model_used = 'gemini-1.5-pro'
            
            # Validate generated code if requested
            validation_results = None
            if validate_code:
                validation_results = generator.validate_strategy_code(generated_code)
            
            # Create strategy record
            with transaction.atomic():
                strategy = GeneratedStrategy.objects.create(
                    user=request.user,
                    name=strategy_name or f"Generated Strategy {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                    original_prompt=prompt,
                    generated_code=generated_code,
                    strategy_type=strategy_type,
                    status='validated' if validation_results and validation_results.get('valid') else 'draft',
                    validation_results=validation_results,
                    ai_model_version='gemini-1.5-pro',
                    generation_metadata={
                        'processing_time_seconds': processing_time,
                        'prompt_length': len(prompt),
                        'code_length': len(generated_code)
                    }
                )
                
                # Update generation log with success
                generation_log.strategy = strategy
                generation_log.status = 'success'
                generation_log.save()
            
            # Serialize response
            strategy_serializer = GeneratedStrategySerializer(strategy)
            
            return Response({
                'success': True,
                'message': 'Strategy generated successfully',
                'data': strategy_serializer.data,
                'generation_log_id': str(generation_log.id),
                'processing_time_seconds': processing_time
            }, status=status.HTTP_201_CREATED)
            
        except StrategyGeneratorError as e:
            # Update generation log with error
            generation_log.error_message = str(e)
            generation_log.processing_time_seconds = time.time() - start_time
            generation_log.save()
            
            logger.error(f"Strategy generation failed for user {request.user.email}: {str(e)}")
            
            return Response({
                'success': False,
                'error': 'Strategy generation failed',
                'message': str(e),
                'generation_log_id': str(generation_log.id)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            # Update generation log with unexpected error
            generation_log.error_message = f"Unexpected error: {str(e)}"
            generation_log.processing_time_seconds = time.time() - start_time
            generation_log.save()
            
            logger.error(f"Unexpected error during strategy generation: {str(e)}")
            
            return Response({
                'success': False,
                'error': 'Internal server error',
                'message': 'An unexpected error occurred during strategy generation',
                'generation_log_id': str(generation_log.id)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StrategyListAPIView(APIView):
    """
    API endpoint for listing user's generated strategies.
    
    GET /api/strategies/
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StrategyPagination
    
    def get(self, request):
        """List user's generated strategies."""
        strategies = GeneratedStrategy.objects.filter(user=request.user)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            strategies = strategies.filter(status=status_filter)
        
        # Filter by strategy type if provided
        type_filter = request.query_params.get('type')
        if type_filter:
            strategies = strategies.filter(strategy_type=type_filter)
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(strategies, request)
        
        if page is not None:
            serializer = GeneratedStrategyListSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data
            })
        
        serializer = GeneratedStrategyListSerializer(strategies, many=True)
        return Response({
            'success': True,
            'count': strategies.count(),
            'data': serializer.data
        })


class StrategyDetailAPIView(APIView):
    """
    API endpoint for retrieving, updating, or deleting a specific strategy.
    
    GET/PUT/DELETE /api/strategies/{id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, strategy_id, user):
        """Get strategy object for the authenticated user."""
        try:
            return GeneratedStrategy.objects.get(id=strategy_id, user=user)
        except GeneratedStrategy.DoesNotExist:
            return None
    
    def get(self, request, strategy_id):
        """Retrieve a specific strategy."""
        strategy = self.get_object(strategy_id, request.user)
        if not strategy:
            return Response({
                'success': False,
                'error': 'Strategy not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Increment usage count
        strategy.increment_usage()
        
        serializer = GeneratedStrategySerializer(strategy)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def put(self, request, strategy_id):
        """Update a specific strategy."""
        strategy = self.get_object(strategy_id, request.user)
        if not strategy:
            return Response({
                'success': False,
                'error': 'Strategy not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GeneratedStrategySerializer(strategy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Strategy updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, strategy_id):
        """Delete a specific strategy."""
        strategy = self.get_object(strategy_id, request.user)
        if not strategy:
            return Response({
                'success': False,
                'error': 'Strategy not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        strategy_name = strategy.name
        strategy.delete()
        
        return Response({
            'success': True,
            'message': f'Strategy "{strategy_name}" deleted successfully'
        })


class ValidateStrategyAPIView(APIView):
    """
    API endpoint for validating strategy code.
    
    POST /api/strategies/validate/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Validate strategy code."""
        serializer = StrategyValidationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        code = serializer.validated_data['code']
        
        try:
            generator = AIStrategyGenerator()
            validation_results = generator.validate_strategy_code(code)
            
            response_serializer = StrategyValidationResponseSerializer(data=validation_results)
            if response_serializer.is_valid():
                return Response({
                    'success': True,
                    'validation_results': response_serializer.validated_data
                })
            
            return Response({
                'success': True,
                'validation_results': validation_results
            })
            
        except Exception as e:
            logger.error(f"Strategy validation failed: {str(e)}")
            return Response({
                'success': False,
                'error': 'Validation failed',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StrategyGenerationLogsAPIView(APIView):
    """
    API endpoint for viewing strategy generation logs.
    
    GET /api/strategies/generation-logs/
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StrategyPagination
    
    def get(self, request):
        """List user's strategy generation logs."""
        logs = StrategyGenerationLog.objects.filter(user=request.user)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            logs = logs.filter(status=status_filter)
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(logs, request)
        
        if page is not None:
            serializer = StrategyGenerationLogSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data
            })
        
        serializer = StrategyGenerationLogSerializer(logs, many=True)
        return Response({
            'success': True,
            'count': logs.count(),
            'data': serializer.data
        })
