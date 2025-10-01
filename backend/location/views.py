from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from .models import CustomerLocation
from shop.models import Shop
from .serializers import (
    CustomerLocationSerializer,
    CustomerLocationCreateSerializer,
    CustomerLocationUpdateSerializer,
    ShopWithLocationsSerializer,
    NearbyLocationSerializer
)


class CustomerLocationListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list and create customer locations
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomerLocationCreateSerializer
        return CustomerLocationSerializer
    
    def get_queryset(self):
        """
        Filter locations based on query parameters
        """
        queryset = CustomerLocation.objects.select_related('shop__customer').all()
        
        # Filter by shop
        shop_id = self.request.query_params.get('shop_id', None)
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        # Filter by customer (through shop)
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            queryset = queryset.filter(shop__customer_id=customer_id)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by primary status
        is_primary = self.request.query_params.get('is_primary', None)
        if is_primary is not None:
            queryset = queryset.filter(is_primary=is_primary.lower() == 'true')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(location_name__icontains=search) |
                Q(address_description__icontains=search) |
                Q(shop__name__icontains=search) |
                Q(shop__customer__first_name__icontains=search) |
                Q(shop__customer__last_name__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create a new customer location
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            location = serializer.save()
            return Response({
                'success': True,
                'message': 'Customer location created successfully',
                'data': CustomerLocationSerializer(location).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Location creation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """
        List locations with custom response format
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'message': 'Locations retrieved successfully',
                'data': paginated_response.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Locations retrieved successfully',
            'data': serializer.data
        })


class CustomerLocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific customer location
    """
    queryset = CustomerLocation.objects.select_related('shop__customer').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CustomerLocationUpdateSerializer
        return CustomerLocationSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific location
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Location retrieved successfully',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """
        Update a specific location
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            location = serializer.save()
            return Response({
                'success': True,
                'message': 'Location updated successfully',
                'data': CustomerLocationSerializer(location).data
            })
        
        return Response({
            'success': False,
            'message': 'Location update failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific location
        """
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Location deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class ShopLocationsView(APIView):
    """
    API endpoint to get all locations for a specific shop
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, shop_id):
        """
        Get all locations for a specific shop
        """
        try:
            shop = Shop.objects.get(id=shop_id)
            locations = CustomerLocation.objects.filter(
                shop=shop
            ).order_by('-is_primary', '-created_at')
            
            serializer = CustomerLocationSerializer(locations, many=True)
            return Response({
                'success': True,
                'message': 'Shop locations retrieved successfully',
                'data': {
                    'shop': {
                        'id': shop.id,
                        'name': shop.name,
                        'customer_name': shop.customer.full_name,
                        'full_address': shop.full_address
                    },
                    'locations': serializer.data,
                    'location_count': locations.count()
                }
            })
        
        except Shop.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Shop not found'
            }, status=status.HTTP_404_NOT_FOUND)


class NearbyLocationsView(APIView):
    """
    API endpoint to find nearby locations
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get locations within a certain radius
        """
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius_km = request.query_params.get('radius_km', 5)
        
        if not latitude or not longitude:
            return Response({
                'success': False,
                'message': 'Latitude and longitude parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius_km = float(radius_km)
        except ValueError:
            return Response({
                'success': False,
                'message': 'Invalid coordinate or radius values'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get nearby locations
        nearby_locations = CustomerLocation.get_nearby_locations(
            latitude, longitude, radius_km
        )
        
        serializer = NearbyLocationSerializer(
            nearby_locations, 
            many=True,
            context={
                'search_latitude': latitude,
                'search_longitude': longitude
            }
        )
        
        return Response({
            'success': True,
            'message': f'Found {nearby_locations.count()} locations within {radius_km}km',
            'data': {
                'search_coordinates': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius_km': radius_km
                },
                'locations': serializer.data,
                'location_count': nearby_locations.count()
            }
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_primary_location(request, location_id):
    """
    Set a location as primary for the shop
    """
    try:
        location = CustomerLocation.objects.get(id=location_id)
        
        # Set this location as primary (will automatically unset others)
        location.is_primary = True
        location.save()
        
        return Response({
            'success': True,
            'message': 'Location set as primary successfully',
            'data': CustomerLocationSerializer(location).data
        })
    
    except CustomerLocation.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Location not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_location_status(request, location_id):
    """
    Toggle active/inactive status of a location
    """
    try:
        location = CustomerLocation.objects.get(id=location_id)
        location.is_active = not location.is_active
        location.save()
        
        status_text = "activated" if location.is_active else "deactivated"
        
        return Response({
            'success': True,
            'message': f'Location {status_text} successfully',
            'data': CustomerLocationSerializer(location).data
        })
    
    except CustomerLocation.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Location not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def location_statistics(request):
    """
    Get location statistics
    """
    total_locations = CustomerLocation.objects.count()
    active_locations = CustomerLocation.objects.filter(is_active=True).count()
    primary_locations = CustomerLocation.objects.filter(is_primary=True).count()
    shops_with_locations = Shop.objects.filter(customer_locations__isnull=False).distinct().count()
    shops_without_locations = Shop.objects.filter(customer_locations__isnull=True).count()
    
    return Response({
        'success': True,
        'data': {
            'total_locations': total_locations,
            'active_locations': active_locations,
            'inactive_locations': total_locations - active_locations,
            'primary_locations': primary_locations,
            'shops_with_locations': shops_with_locations,
            'shops_without_locations': shops_without_locations,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_locations(request):
    """
    Bulk create locations for multiple shops
    """
    locations_data = request.data.get('locations', [])
    
    if not locations_data:
        return Response({
            'success': False,
            'message': 'No locations data provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    created_locations = []
    errors = []
    
    for i, location_data in enumerate(locations_data):
        serializer = CustomerLocationCreateSerializer(data=location_data)
        if serializer.is_valid():
            location = serializer.save()
            created_locations.append(CustomerLocationSerializer(location).data)
        else:
            errors.append({
                'index': i,
                'errors': serializer.errors
            })
    
    return Response({
        'success': len(errors) == 0,
        'message': f'Created {len(created_locations)} locations successfully',
        'data': {
            'created_locations': created_locations,
            'errors': errors
        }
    }, status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_207_MULTI_STATUS)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def locations_within_bounds(request):
    """
    Get locations within geographic bounds (bounding box)
    """
    min_lat = request.query_params.get('min_latitude')
    max_lat = request.query_params.get('max_latitude')
    min_lon = request.query_params.get('min_longitude')
    max_lon = request.query_params.get('max_longitude')
    
    if not all([min_lat, max_lat, min_lon, max_lon]):
        return Response({
            'success': False,
            'message': 'All bounding box parameters are required: min_latitude, max_latitude, min_longitude, max_longitude'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        min_lat, max_lat = float(min_lat), float(max_lat)
        min_lon, max_lon = float(min_lon), float(max_lon)
    except ValueError:
        return Response({
            'success': False,
            'message': 'Invalid coordinate values'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    locations = CustomerLocation.objects.filter(
        latitude__range=(min_lat, max_lat),
        longitude__range=(min_lon, max_lon),
        is_active=True
    ).select_related('shop__customer')
    
    serializer = CustomerLocationSerializer(locations, many=True)
    
    return Response({
        'success': True,
        'message': f'Found {locations.count()} locations within bounds',
        'data': {
            'bounds': {
                'min_latitude': min_lat,
                'max_latitude': max_lat,
                'min_longitude': min_lon,
                'max_longitude': max_lon
            },
            'locations': serializer.data,
            'location_count': locations.count()
        }
    })
