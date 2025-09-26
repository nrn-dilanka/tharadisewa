from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from django.http import HttpResponse
from .models import Product
from shop.models import Shop
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductListSerializer,
    ProductUpdateSerializer,
    ProductQRCodeSerializer,
    ProductStatsSerializer,
    ShopProductsSerializer,
    BulkProductCreateSerializer
)
import json

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products with full CRUD operations
    """
    
    queryset = Product.objects.select_related('shop__customer').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shop', 'shop__customer', 'is_active']
    search_fields = ['name', 'description', 'sku', 'shop__name', 'shop__customer__username']
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
        else:
            return ProductSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = super().get_queryset()
        
        # Filter by shop
        shop_id = self.request.query_params.get('shop_id')
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(shop__customer_id=customer_id)
        
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
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        return queryset
    
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
            'data': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """
        Create a new product
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            response_serializer = ProductSerializer(product)
            return Response({
                'success': True,
                'message': 'Product created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Failed to create product',
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
            response_serializer = ProductSerializer(product)
            return Response({
                'success': True,
                'message': 'Product updated successfully',
                'data': response_serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update product',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a product
        """
        instance = self.get_object()
        instance.delete()
        return Response({
            'success': True,
            'message': 'Product deleted successfully'
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
    
    @action(detail=True, methods=['get'])
    def qr_code_info(self, request, pk=None):
        """
        Get QR code information for a product
        """
        product = self.get_object()
        serializer = ProductQRCodeSerializer(product)
        return Response({
            'success': True,
            'message': 'QR code information retrieved successfully',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """
        Toggle active/inactive status of a product
        """
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        
        serializer = ProductSerializer(product)
        return Response({
            'success': True,
            'message': f'Product {"activated" if product.is_active else "deactivated"} successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_shop(self, request):
        """
        Get all products for a specific shop
        """
        shop_id = request.query_params.get('shop_id')
        if not shop_id:
            return Response({
                'success': False,
                'message': 'shop_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Shop not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        products = Product.objects.filter(shop=shop)
        
        # Apply additional filters
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            products = products.filter(is_active=is_active.lower() == 'true')
        
        serializer = ProductListSerializer(products, many=True)
        
        return Response({
            'success': True,
            'message': f'Products for shop "{shop.name}" retrieved successfully',
            'data': {
                'shop': {
                    'id': shop.id,
                    'name': shop.name,
                    'customer_name': shop.customer.get_full_name(),
                    'full_address': shop.full_address
                },
                'products': serializer.data,
                'product_count': len(serializer.data)
            }
        })
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """
        Get all products for a specific customer (across all their shops)
        """
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response({
                'success': False,
                'message': 'customer_id parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(shop__customer_id=customer_id)
        
        # Apply additional filters
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            products = products.filter(is_active=is_active.lower() == 'true')
        
        serializer = ProductListSerializer(products, many=True)
        
        # Group by shop
        shops_data = {}
        for product_data in serializer.data:
            shop_id = product_data['shop']
            if shop_id not in shops_data:
                shops_data[shop_id] = {
                    'shop_id': shop_id,
                    'shop_name': product_data['shop_name'],
                    'products': []
                }
            shops_data[shop_id]['products'].append(product_data)
        
        return Response({
            'success': True,
            'message': f'Products for customer retrieved successfully',
            'data': {
                'shops': list(shops_data.values()),
                'total_products': len(serializer.data)
            }
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple products at once
        """
        serializer = BulkProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            products = result['products']
            
            response_serializer = ProductListSerializer(products, many=True)
            return Response({
                'success': True,
                'message': f'{len(products)} products created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Failed to create products',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get comprehensive product statistics
        """
        # Get all products
        all_products = Product.objects.all()
        
        # Basic counts
        total_products = all_products.count()
        active_products = all_products.filter(is_active=True).count()
        inactive_products = total_products - active_products
        
        # Price-related stats
        products_with_price = all_products.filter(price__isnull=False).count()
        products_without_price = total_products - products_with_price
        
        # Stock-related stats
        products_in_stock = all_products.filter(stock_quantity__gt=0).count()
        products_out_of_stock = total_products - products_in_stock
        
        # Shop-related stats
        shops_with_products = Shop.objects.filter(products__isnull=False).distinct().count()
        total_shops = Shop.objects.count()
        shops_without_products = total_shops - shops_with_products
        
        # Financial stats
        price_stats = all_products.filter(price__isnull=False).aggregate(
            average_price=Avg('price')
        )
        
        # Calculate total stock value
        total_stock_value = None
        products_with_price_and_stock = all_products.filter(
            price__isnull=False,
            stock_quantity__gt=0
        )
        if products_with_price_and_stock.exists():
            total_stock_value = sum([
                product.price * product.stock_quantity 
                for product in products_with_price_and_stock
            ])
        
        stats_data = {
            'total_products': total_products,
            'active_products': active_products,
            'inactive_products': inactive_products,
            'products_with_price': products_with_price,
            'products_without_price': products_without_price,
            'products_in_stock': products_in_stock,
            'products_out_of_stock': products_out_of_stock,
            'shops_with_products': shops_with_products,
            'shops_without_products': shops_without_products,
            'average_price': price_stats['average_price'],
            'total_stock_value': total_stock_value
        }
        
        serializer = ProductStatsSerializer(stats_data)
        return Response({
            'success': True,
            'message': 'Product statistics retrieved successfully',
            'data': serializer.data
        })
    
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
        
        # Try to extract product ID from QR data
        try:
            if 'PRODUCT_ID:' in qr_data:
                # Parse the QR data format: PRODUCT_ID:uuid|NAME:name|...
                parts = qr_data.split('|')
                product_id = None
                for part in parts:
                    if part.startswith('PRODUCT_ID:'):
                        product_id = part.split(':', 1)[1]
                        break
                
                if product_id:
                    try:
                        product = Product.objects.get(id=product_id)
                        serializer = ProductSerializer(product)
                        return Response({
                            'success': True,
                            'message': 'Product found by QR code',
                            'data': serializer.data
                        })
                    except Product.DoesNotExist:
                        pass
            
            # If direct ID lookup failed, try searching by name or other fields
            products = Product.objects.filter(
                Q(name__icontains=qr_data) |
                Q(sku__icontains=qr_data)
            )
            
            if products.exists():
                serializer = ProductListSerializer(products, many=True)
                return Response({
                    'success': True,
                    'message': f'Found {products.count()} products matching QR data',
                    'data': serializer.data
                })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error processing QR data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'message': 'No products found for the provided QR data'
        }, status=status.HTTP_404_NOT_FOUND)

# Additional view for shop-product management
from rest_framework.views import APIView

class ShopProductsView(APIView):
    """
    View for managing products within a specific shop
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, shop_id):
        """
        Get all products for a specific shop with shop details
        """
        try:
            shop = Shop.objects.prefetch_related('products').get(id=shop_id)
        except Shop.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Shop not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Annotate with product count
        shop.product_count = shop.products.count()
        
        serializer = ShopProductsSerializer(shop)
        return Response({
            'success': True,
            'message': 'Shop products retrieved successfully',
            'data': serializer.data
        })
