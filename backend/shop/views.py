from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from .models import Shop
from customer.models import Customer
from .serializers import (
    ShopSerializer,
    ShopCreateSerializer,
    ShopUpdateSerializer,
    ShopWithLocationsSerializer,
    CustomerWithShopsSerializer
)


class ShopListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list and create shops
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ShopCreateSerializer
        return ShopSerializer
    
    def get_queryset(self):
        """
        Filter shops based on query parameters
        """
        queryset = Shop.objects.select_related('customer').all()
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id', None)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by postal code
        postal_code = self.request.query_params.get('postal_code', None)
        if postal_code:
            queryset = queryset.filter(postal_code=postal_code)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(address_line_1__icontains=search) |
                Q(address_line_2__icontains=search) |
                Q(address_line_3__icontains=search) |
                Q(city__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer__username__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create a new shop
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            shop = serializer.save()
            return Response({
                'success': True,
                'message': 'Shop created successfully',
                'data': ShopSerializer(shop).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Shop creation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """
        List shops with custom response format
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'message': 'Shops retrieved successfully',
                'data': paginated_response.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Shops retrieved successfully',
            'data': serializer.data
        })


class ShopDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific shop
    """
    queryset = Shop.objects.select_related('customer').all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ShopUpdateSerializer
        return ShopSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific shop
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Shop retrieved successfully',
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """
        Update a specific shop
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            shop = serializer.save()
            return Response({
                'success': True,
                'message': 'Shop updated successfully',
                'data': ShopSerializer(shop).data
            })
        
        return Response({
            'success': False,
            'message': 'Shop update failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific shop
        """
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Shop deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class CustomerShopsView(APIView):
    """
    API endpoint to get all shops for a specific customer
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, customer_id):
        """
        Get all shops for a specific customer
        """
        try:
            customer = Customer.objects.get(id=customer_id)
            shops = Shop.objects.filter(customer=customer).order_by('-created_at')
            
            serializer = ShopSerializer(shops, many=True)
            return Response({
                'success': True,
                'message': 'Customer shops retrieved successfully',
                'data': {
                    'customer': {
                        'id': customer.id,
                        'customer_id': customer.customer_id,
                        'full_name': customer.full_name,
                        'username': customer.username
                    },
                    'shops': serializer.data,
                    'shop_count': shops.count()
                }
            })
        
        except Customer.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ShopsWithLocationsView(generics.ListAPIView):
    """
    API endpoint to list shops with their locations
    """
    queryset = Shop.objects.select_related('customer').prefetch_related('customer_locations').all()
    serializer_class = ShopWithLocationsSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """
        List shops with their locations
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'message': 'Shops with locations retrieved successfully',
                'data': paginated_response.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Shops with locations retrieved successfully',
            'data': serializer.data
        })


class CustomersWithShopsView(generics.ListAPIView):
    """
    API endpoint to list customers with their shops
    """
    queryset = Customer.objects.prefetch_related('shops').all()
    serializer_class = CustomerWithShopsSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """
        List customers with their shops
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            return Response({
                'success': True,
                'message': 'Customers with shops retrieved successfully',
                'data': paginated_response.data
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Customers with shops retrieved successfully',
            'data': serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_shop_status(request, shop_id):
    """
    Toggle active/inactive status of a shop
    """
    try:
        shop = Shop.objects.get(id=shop_id)
        shop.is_active = not shop.is_active
        shop.save()
        
        status_text = "activated" if shop.is_active else "deactivated"
        
        return Response({
            'success': True,
            'message': f'Shop {status_text} successfully',
            'data': ShopSerializer(shop).data
        })
    
    except Shop.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Shop not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shop_statistics(request):
    """
    Get shop statistics
    """
    total_shops = Shop.objects.count()
    active_shops = Shop.objects.filter(is_active=True).count()
    customers_with_shops = Customer.objects.filter(shops__isnull=False).distinct().count()
    customers_without_shops = Customer.objects.filter(shops__isnull=True).count()
    
    # Shops by city
    shops_by_city = Shop.objects.values('city').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return Response({
        'success': True,
        'data': {
            'total_shops': total_shops,
            'active_shops': active_shops,
            'inactive_shops': total_shops - active_shops,
            'customers_with_shops': customers_with_shops,
            'customers_without_shops': customers_without_shops,
            'shops_by_city': list(shops_by_city)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shops_by_city(request, city_name):
    """
    Get shops in a specific city
    """
    shops = Shop.objects.filter(
        city__icontains=city_name,
        is_active=True
    ).select_related('customer')
    
    serializer = ShopSerializer(shops, many=True)
    
    return Response({
        'success': True,
        'message': f'Shops in {city_name} retrieved successfully',
        'data': {
            'city': city_name,
            'shop_count': shops.count(),
            'shops': serializer.data
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def shops_by_postal_code(request, postal_code):
    """
    Get shops in a specific postal code area
    """
    shops = Shop.objects.filter(
        postal_code=postal_code,
        is_active=True
    ).select_related('customer')
    
    serializer = ShopSerializer(shops, many=True)
    
    return Response({
        'success': True,
        'message': f'Shops in postal code {postal_code} retrieved successfully',
        'data': {
            'postal_code': postal_code,
            'shop_count': shops.count(),
            'shops': serializer.data
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_shops(request):
    """
    Bulk create shops for multiple customers
    """
    shops_data = request.data.get('shops', [])
    
    if not shops_data:
        return Response({
            'success': False,
            'message': 'No shops data provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    created_shops = []
    errors = []
    
    for i, shop_data in enumerate(shops_data):
        serializer = ShopCreateSerializer(data=shop_data)
        if serializer.is_valid():
            shop = serializer.save()
            created_shops.append(ShopSerializer(shop).data)
        else:
            errors.append({
                'index': i,
                'errors': serializer.errors
            })
    
    return Response({
        'success': len(errors) == 0,
        'message': f'Created {len(created_shops)} shops successfully',
        'data': {
            'created_shops': created_shops,
            'errors': errors
        }
    }, status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_207_MULTI_STATUS)
