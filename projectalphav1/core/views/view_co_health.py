"""
WHAT: Health check endpoint for Railway deployment monitoring
WHY: Railway healthcheck needs a reliable endpoint to verify service is running
WHERE: Used by Railway healthcheck at /api/health/
HOW: Simple endpoint that returns 200 OK with basic status info

Docs reviewed:
* Django REST Framework views: https://www.django-rest-framework.org/api-guide/views/
* Railway healthchecks: https://docs.railway.com/deploy/healthchecks
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.conf import settings


@api_view(['GET'])
@permission_classes([AllowAny])  # No authentication required for health checks
def health_check(request):
    """
    Health check endpoint for deployment monitoring.
    
    Returns:
        - 200 OK: Service is healthy and database is accessible
        - 503 Service Unavailable: Database connection failed
    
    This endpoint:
    1. Tests database connectivity
    2. Returns service status
    3. Doesn't require authentication
    """
    try:
        # Test database connection by running a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return Response({
            'status': 'healthy',
            'database': 'connected',
            'debug': settings.DEBUG
        }, status=200)
    
    except Exception as e:
        # Return 503 if database is not accessible
        return Response({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }, status=503)

