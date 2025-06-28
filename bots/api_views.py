"""
API views for the bots app.

This module provides REST API endpoints for managing trading bots,
including starting and stopping bot operations.
"""

import logging
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from celery import current_app

from .models import Bot, BotRun
from .tasks import run_bot_instance
from .serializers import (
    BotSerializer,
    BotListSerializer,
    BotRunSerializer,
    BotStartRequestSerializer,
    BotStopRequestSerializer
)

logger = logging.getLogger(__name__)


class BotPagination(PageNumberPagination):
    """Custom pagination for bot listings."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BotListAPIView(APIView):
    """
    API endpoint for listing user's trading bots.
    
    GET /api/bots/
    """
    permission_classes = [IsAuthenticated]
    pagination_class = BotPagination
    
    def get(self, request):
        """List user's trading bots."""
        bots = Bot.objects.filter(user=request.user)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            # Filter by whether bot is currently active
            if status_filter == 'active':
                bots = bots.filter(id__in=[
                    bot.id for bot in bots if bot.has_active_runs()
                ])
            elif status_filter == 'inactive':
                bots = bots.filter(id__in=[
                    bot.id for bot in bots if not bot.has_active_runs()
                ])
        
        # Filter by strategy if provided
        strategy_filter = request.query_params.get('strategy')
        if strategy_filter:
            bots = bots.filter(strategy=strategy_filter)
        
        # Filter by exchange if provided
        exchange_filter = request.query_params.get('exchange')
        if exchange_filter:
            bots = bots.filter(exchange_key__exchange__id=exchange_filter)
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(bots, request)
        
        if page is not None:
            serializer = BotListSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data
            })
        
        serializer = BotListSerializer(bots, many=True)
        return Response({
            'success': True,
            'count': bots.count(),
            'data': serializer.data
        })


class BotDetailAPIView(APIView):
    """
    API endpoint for retrieving, updating, or deleting a specific bot.
    
    GET/PUT/DELETE /api/bots/{id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, bot_id, user):
        """Get bot object for the authenticated user."""
        try:
            return Bot.objects.get(id=bot_id, user=user)
        except Bot.DoesNotExist:
            return None
    
    def get(self, request, bot_id):
        """Retrieve a specific bot with detailed information."""
        bot = self.get_object(bot_id, request.user)
        if not bot:
            return Response({
                'success': False,
                'error': 'Bot not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BotSerializer(bot)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def put(self, request, bot_id):
        """Update a specific bot."""
        bot = self.get_object(bot_id, request.user)
        if not bot:
            return Response({
                'success': False,
                'error': 'Bot not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Don't allow updating a bot that's currently running
        if bot.has_active_runs():
            return Response({
                'success': False,
                'error': 'Cannot update a running bot. Stop the bot first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BotSerializer(bot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Bot updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, bot_id):
        """Delete a specific bot."""
        bot = self.get_object(bot_id, request.user)
        if not bot:
            return Response({
                'success': False,
                'error': 'Bot not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Don't allow deleting a bot that's currently running
        if bot.has_active_runs():
            return Response({
                'success': False,
                'error': 'Cannot delete a running bot. Stop the bot first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        bot_name = bot.name
        bot.delete()
        
        return Response({
            'success': True,
            'message': f'Bot "{bot_name}" deleted successfully'
        })


class BotStartAPIView(APIView):
    """
    API endpoint for starting a trading bot.
    
    POST /api/bots/{id}/start/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, bot_id, user):
        """Get bot object for the authenticated user."""
        try:
            return Bot.objects.get(id=bot_id, user=user)
        except Bot.DoesNotExist:
            return None
    
    def post(self, request, bot_id):
        """Start a trading bot by creating a new BotRun and launching Celery task."""
        bot = self.get_object(bot_id, request.user)
        if not bot:
            return Response({
                'success': False,
                'error': 'Bot not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if bot is already running
        if bot.has_active_runs():
            current_run = bot.get_current_run()
            return Response({
                'success': False,
                'error': 'Bot is already running',
                'current_run_id': str(current_run.id) if current_run else None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate request data
        serializer = BotStartRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create new bot run
            bot_run = BotRun.objects.create(
                bot=bot,
                start_time=timezone.now(),
                status='starting',
                run_parameters=serializer.validated_data.get('parameters', {}),
                notes=serializer.validated_data.get('notes', '')
            )
            
            logger.info(f"Created bot run {bot_run.id} for bot {bot.name}")
            
            # Launch Celery task
            task = run_bot_instance.delay(str(bot_run.id))
            
            # Update bot run with task ID
            bot_run.celery_task_id = task.id
            bot_run.status = 'running'
            bot_run.save()
            
            logger.info(f"Launched Celery task {task.id} for bot run {bot_run.id}")
            
            # Serialize response
            run_serializer = BotRunSerializer(bot_run)
            
            return Response({
                'success': True,
                'message': f'Bot "{bot.name}" started successfully',
                'data': {
                    'bot_run': run_serializer.data,
                    'task_id': task.id
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Failed to start bot {bot.name}: {str(e)}")
            
            # Clean up bot run if it was created
            try:
                if 'bot_run' in locals():
                    bot_run.status = 'error'
                    bot_run.end_time = timezone.now()
                    bot_run.error_message = str(e)
                    bot_run.save()
            except:
                pass
            
            return Response({
                'success': False,
                'error': 'Failed to start bot',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BotStopAPIView(APIView):
    """
    API endpoint for stopping a trading bot.
    
    POST /api/bots/{id}/stop/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, bot_id, user):
        """Get bot object for the authenticated user."""
        try:
            return Bot.objects.get(id=bot_id, user=user)
        except Bot.DoesNotExist:
            return None
    
    def post(self, request, bot_id):
        """Stop a trading bot by updating the BotRun record and terminating Celery task."""
        bot = self.get_object(bot_id, request.user)
        if not bot:
            return Response({
                'success': False,
                'error': 'Bot not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if bot is running
        if not bot.has_active_runs():
            return Response({
                'success': False,
                'error': 'Bot is not currently running'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate request data
        serializer = BotStopRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get current bot run
            current_run = bot.get_current_run()
            if not current_run:
                return Response({
                    'success': False,
                    'error': 'No active bot run found'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update bot run status
            current_run.status = 'stopping'
            current_run.notes = (current_run.notes or '') + f"\nStopped via API: {serializer.validated_data.get('reason', 'No reason provided')}"
            current_run.save()
            
            logger.info(f"Stopping bot run {current_run.id} for bot {bot.name}")
            
            # Terminate Celery task if it exists
            if current_run.celery_task_id:
                try:
                    current_app.control.revoke(current_run.celery_task_id, terminate=True)
                    logger.info(f"Revoked Celery task {current_run.celery_task_id}")
                except Exception as e:
                    logger.warning(f"Failed to revoke Celery task {current_run.celery_task_id}: {str(e)}")
            
            # Update final status
            current_run.status = 'stopped'
            current_run.end_time = timezone.now()
            current_run.save()
            
            logger.info(f"Bot run {current_run.id} stopped successfully")
            
            # Serialize response
            run_serializer = BotRunSerializer(current_run)
            
            return Response({
                'success': True,
                'message': f'Bot "{bot.name}" stopped successfully',
                'data': {
                    'bot_run': run_serializer.data
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to stop bot {bot.name}: {str(e)}")
            
            return Response({
                'success': False,
                'error': 'Failed to stop bot',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BotRunsAPIView(APIView):
    """
    API endpoint for listing bot runs.
    
    GET /api/bots/{id}/runs/
    """
    permission_classes = [IsAuthenticated]
    pagination_class = BotPagination
    
    def get_object(self, bot_id, user):
        """Get bot object for the authenticated user."""
        try:
            return Bot.objects.get(id=bot_id, user=user)
        except Bot.DoesNotExist:
            return None
    
    def get(self, request, bot_id):
        """List bot runs for a specific bot."""
        bot = self.get_object(bot_id, request.user)
        if not bot:
            return Response({
                'success': False,
                'error': 'Bot not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        runs = bot.runs.all()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            runs = runs.filter(status=status_filter)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            runs = runs.filter(start_time__gte=start_date)
        if end_date:
            runs = runs.filter(start_time__lte=end_date)
        
        # Paginate results
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(runs, request)
        
        if page is not None:
            serializer = BotRunSerializer(page, many=True)
            return paginator.get_paginated_response({
                'success': True,
                'data': serializer.data
            })
        
        serializer = BotRunSerializer(runs, many=True)
        return Response({
            'success': True,
            'count': runs.count(),
            'data': serializer.data
        })


class BotStatusAPIView(APIView):
    """
    API endpoint for getting bot status information.
    
    GET /api/bots/{id}/status/
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, bot_id, user):
        """Get bot object for the authenticated user."""
        try:
            return Bot.objects.get(id=bot_id, user=user)
        except Bot.DoesNotExist:
            return None
    
    def get(self, request, bot_id):
        """Get current status of a trading bot."""
        bot = self.get_object(bot_id, request.user)
        if not bot:
            return Response({
                'success': False,
                'error': 'Bot not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        current_run = bot.get_current_run()
        
        status_data = {
            'bot_id': str(bot.id),
            'bot_name': bot.name,
            'is_active': bot.has_active_runs(),
            'current_run': None,
            'total_runs': bot.get_total_runs(),
            'successful_runs': bot.get_successful_runs(),
            'last_run_at': None
        }
        
        if current_run:
            status_data['current_run'] = BotRunSerializer(current_run).data
        
        # Get last run information
        last_run = bot.runs.order_by('-start_time').first()
        if last_run:
            status_data['last_run_at'] = last_run.start_time
        
        return Response({
            'success': True,
            'data': status_data
        })
