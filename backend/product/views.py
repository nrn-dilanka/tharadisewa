from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg, F
from django.http import HttpResponse
from .models import Product
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductListSerializer,
    ProductUpdateSerializer,
    ProductQRCodeSerializer,
    ProductStatsSerializer,
    BulkProductCreateSerializer
)
import json

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products with full CRUD operations
    """
    
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'stock_quantity', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ProductUpdateSerializer
        elif self.action == 'list':
            return ProductListSerializer
        elif self.action == 'regenerate_qr_code':
            return ProductQRCodeSerializer
        elif self.action == 'stats':
            return ProductStatsSerializer
        elif self.action == 'bulk_create':
            return BulkProductCreateSerializer
        else:
            return ProductSerializer

    def get_queryset(self):
        """
        Override get_queryset to provide filtering options
        """
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by stock status
        in_stock = self.request.query_params.get('in_stock')
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(stock_quantity__gt=0)
            else:
                queryset = queryset.filter(stock_quantity=0)
        
        return queryset

    def perform_create(self, serializer):
        """
        Customize product creation
        """
        product = serializer.save()
        # QR code generation is handled in the model's save method
        return product

    def list(self, request, *args, **kwargs):
        """
        List all products with filtering and pagination
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'success': True,
                'message': 'Products retrieved successfully',
                'data': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Products retrieved successfully',
            'data': serializer.data,
            'total_count': queryset.count()
        })

    def create(self, request, *args, **kwargs):
        """
        Create a new product
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = self.perform_create(serializer)
            return Response({
                'success': True,
                'message': 'Product created successfully',
                'data': ProductSerializer(product).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific product
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Product retrieved successfully',
            'data': serializer.data
        })

    def update(self, request, *args, **kwargs):
        """
        Update a product
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            product = serializer.save()
            return Response({
                'success': True,
                'message': 'Product updated successfully',
                'data': ProductSerializer(product).data
            })
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a product
        """
        instance = self.get_object()
        product_name = instance.name
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': f'Product "{product_name}" deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def regenerate_qr_code(self, request, pk=None):
        """
        Regenerate QR code for a specific product
        """
        product = self.get_object()
        
        try:
            product.regenerate_qr_code()
            serializer = ProductQRCodeSerializer(product)
            return Response({
                'success': True,
                'message': 'QR code regenerated successfully',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to regenerate QR code: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        Toggle product active status
        """
        product = self.get_object()
        product.is_active = not product.is_active
        product.save(update_fields=['is_active'])
        
        serializer = ProductSerializer(product)
        return Response({
            'success': True,
            'message': f'Product {"activated" if product.is_active else "deactivated"} successfully',
            'data': serializer.data
        })

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple products at once
        """
        serializer = BulkProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            products_data = serializer.validated_data['products']
            created_products = []
            errors = []
            
            for product_data in products_data:
                product_serializer = ProductCreateSerializer(data=product_data)
                if product_serializer.is_valid():
                    product = product_serializer.save()
                    created_products.append(product)
                else:
                    errors.append({
                        'product_data': product_data,
                        'errors': product_serializer.errors
                    })
            
            return Response({
                'success': True,
                'message': f'Successfully created {len(created_products)} products',
                'data': {
                    'created_products': ProductListSerializer(created_products, many=True).data,
                    'created_count': len(created_products),
                    'error_count': len(errors),
                    'errors': errors
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get comprehensive product statistics
        """
        try:
            total_products = Product.objects.count()
            active_products = Product.objects.filter(is_active=True).count()
            in_stock_products = Product.objects.filter(stock_quantity__gt=0).count()
            out_of_stock_products = Product.objects.filter(stock_quantity=0).count()
            
            # Calculate averages
            avg_price = Product.objects.filter(price__isnull=False).aggregate(Avg('price'))['price__avg'] or 0
            avg_stock = Product.objects.aggregate(Avg('stock_quantity'))['stock_quantity__avg'] or 0
            total_stock_value = Product.objects.filter(
                price__isnull=False, 
                stock_quantity__isnull=False
            ).aggregate(
                total=Sum(F('price') * F('stock_quantity'))
            )['total'] or 0
            
            # Low stock products (less than 10 items)
            low_stock_products = Product.objects.filter(
                stock_quantity__lt=10, 
                stock_quantity__gt=0
            ).count()
            
            return Response({
                'success': True,
                'message': 'Product statistics retrieved successfully',
                'data': {
                    'total_products': total_products,
                    'active_products': active_products,
                    'inactive_products': total_products - active_products,
                    'in_stock_products': in_stock_products,
                    'out_of_stock_products': out_of_stock_products,
                    'low_stock_products': low_stock_products,
                    'average_price': round(float(avg_price), 2),
                    'average_stock_quantity': round(float(avg_stock), 2),
                    'total_inventory_value': round(float(total_stock_value), 2),
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to retrieve statistics: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def search_by_qr(self, request):
        """
        Search product by QR code data
        """
        qr_data = request.query_params.get('qr_data')
        if not qr_data:
            return Response({
                'success': False,
                'message': 'qr_data parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse QR data to extract product ID
        try:
            # Expected format: "PRODUCT_ID:uuid|NAME:product_name"
            if 'PRODUCT_ID:' in qr_data:
                product_id_part = qr_data.split('PRODUCT_ID:')[1].split('|')[0]
                product = get_object_or_404(Product, id=product_id_part)
                
                serializer = ProductSerializer(product)
                return Response({
                    'success': True,
                    'message': 'Product found successfully',
                    'data': serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid QR code format'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Product not found or invalid QR code: {str(e)}'
            }, status=status.HTTP_404_NOT_FOUND)