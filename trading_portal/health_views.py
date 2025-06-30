from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """
    Simple health check endpoint for frontend connection testing.
    """
    return JsonResponse({
        'status': 'healthy',
        'message': 'API is running'
    })
