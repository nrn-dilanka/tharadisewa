from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import get_resolver
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([AllowAny])
def test_connection(request):
    """
    Simple test endpoint to verify API connectivity
    """
    return Response({
        'status': 'success',
        'message': 'API connection successful',
        'server_time': timezone.now().isoformat(),
        'debug_info': {
            'host': request.get_host(),
            'method': request.method,
            'path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint
    """
    return Response({
        'status': 'healthy',
        'service': 'TharadiSewa API',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_urls(request):
    """
    Debug endpoint to list all available URLs
    """
    try:
        resolver = get_resolver()
        url_patterns = []
        
        def extract_patterns(patterns, prefix=''):
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                    extract_patterns(pattern.url_patterns, prefix + str(pattern.pattern))
                else:
                    url_patterns.append(prefix + str(pattern.pattern))
        
        extract_patterns(resolver.url_patterns)
        
        return Response({
            'status': 'success',
            'message': 'Available API endpoints',
            'urls': url_patterns[:50],  # Limit to first 50 to avoid overwhelming
            'total_count': len(url_patterns)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to list URLs: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)