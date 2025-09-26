from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Max
from django.db import models
from datetime import datetime, timedelta
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import TechnicalModel
from .serializers import (
    TechnicalModelSerializer,
    TechnicalModelCreateSerializer,
    TechnicalModelListSerializer,
    TechnicalModelUpdateSerializer,
    TechnicalModelStatsSerializer,
    TechnicalModelSearchSerializer,
    TechnicalModelSummarySerializer,
    SpecificationSerializer,
    BrandListSerializer
)


class TechnicalModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing technical models
    Provides CRUD operations and additional technical model management endpoints
    """
    
    queryset = TechnicalModel.objects.select_related('product__shop')
    permission_classes = [IsAuthenticated]
    
    # Add filters if django-filter is available
    filter_backends = [SearchFilter, OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
        filterset_fields = {
            'brand': ['exact', 'icontains'],
            'model': ['exact', 'icontains'],
            'year_released': ['exact', 'gte', 'lte'],
            'country_of_origin': ['exact', 'icontains'],
            'manufacturer': ['exact', 'icontains'],
            'is_active': ['exact'],
            'is_discontinued': ['exact'],
            'product': ['exact'],
            'product__shop': ['exact'],
            'created_at': ['exact', 'gte', 'lte']
        }
    
    search_fields = [
        'brand',
        'model',
        'model_number',
        'series',
        'manufacturer',
        'country_of_origin',
        'product__name',
        'product__shop__name',
        'notes'
    ]
    
    ordering_fields = [
        'brand', 'model', 'year_released', 'created_at',
        'product__name', 'is_active'
    ]
    
    ordering = ['brand', 'model']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return TechnicalModelListSerializer
        elif self.action == 'create':
            return TechnicalModelCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TechnicalModelUpdateSerializer
        elif self.action == 'statistics':
            return TechnicalModelStatsSerializer
        elif self.action == 'search_models':
            return TechnicalModelSearchSerializer
        elif self.action == 'summary':
            return TechnicalModelSummarySerializer
        elif self.action in ['update_specifications', 'add_specification']:
            return SpecificationSerializer
        elif self.action == 'brands':
            return BrandListSerializer
        return TechnicalModelSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = self.queryset
        
        # Filter by product if specified
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filter by shop if specified
        shop_id = self.request.query_params.get('shop', None)
        if shop_id:
            queryset = queryset.filter(product__shop_id=shop_id)
        
        # Filter by brand if specified
        brand = self.request.query_params.get('brand', None)
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        # Filter by active status
        active_only = self.request.query_params.get('active_only', None)
        if active_only and active_only.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        
        # Filter by year range
        year_from = self.request.query_params.get('year_from', None)
        year_to = self.request.query_params.get('year_to', None)
        
        if year_from:
            try:
                queryset = queryset.filter(year_released__gte=int(year_from))
            except (ValueError, TypeError):
                pass
        
        if year_to:
            try:
                queryset = queryset.filter(year_released__lte=int(year_to))
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_product(self, request, product_id=None):
        """
        Get technical models for a specific product
        """
        if not product_id:
            product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'Product ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        models = self.get_queryset().filter(product_id=product_id)
        serializer = TechnicalModelListSerializer(models, many=True)
        
        return Response({
            'count': models.count(),
            'technical_models': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_shop(self, request, shop_id=None):
        """
        Get technical models for a specific shop
        """
        if not shop_id:
            shop_id = request.query_params.get('shop_id')
        
        if not shop_id:
            return Response(
                {'error': 'Shop ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        models = self.get_queryset().filter(product__shop_id=shop_id)
        serializer = TechnicalModelListSerializer(models, many=True)
        
        return Response({
            'count': models.count(),
            'technical_models': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_brand(self, request, brand_name=None):
        """
        Get technical models by brand
        """
        if not brand_name:
            brand_name = request.query_params.get('brand_name')
        
        if not brand_name:
            return Response(
                {'error': 'Brand name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        models = TechnicalModel.get_by_brand(brand_name)
        serializer = TechnicalModelListSerializer(models, many=True)
        
        return Response({
            'brand': brand_name,
            'count': models.count(),
            'technical_models': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active technical models
        """
        models = TechnicalModel.get_active_models()
        serializer = TechnicalModelListSerializer(models, many=True)
        
        return Response({
            'count': models.count(),
            'technical_models': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def discontinued(self, request):
        """
        Get all discontinued technical models
        """
        models = self.get_queryset().filter(is_discontinued=True)
        serializer = TechnicalModelListSerializer(models, many=True)
        
        return Response({
            'count': models.count(),
            'technical_models': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def search_models(self, request):
        """
        Search technical models
        """
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        models = TechnicalModel.search_models(query)
        serializer = TechnicalModelListSerializer(models, many=True)
        
        search_data = {
            'query': query,
            'total_results': models.count(),
            'results': serializer.data
        }
        
        search_serializer = TechnicalModelSearchSerializer(search_data)
        return Response(search_serializer.data)
    
    @action(detail=False, methods=['get'])
    def brands(self, request):
        """
        Get list of all brands with statistics
        """
        # Get brand statistics
        brand_stats = (
            self.get_queryset()
            .values('brand')
            .annotate(
                model_count=Count('id'),
                active_models=Count('id', filter=Q(is_active=True)),
                latest_year=Max('year_released')
            )
            .order_by('brand')
        )
        
        serializer = BrandListSerializer(brand_stats, many=True)
        return Response({
            'total_brands': brand_stats.count(),
            'brands': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get comprehensive technical model statistics
        """
        queryset = self.get_queryset()
        
        # Basic statistics
        total_models = queryset.count()
        active_models = queryset.filter(is_active=True).count()
        discontinued_models = queryset.filter(is_discontinued=True).count()
        
        # Brand statistics
        brands = queryset.values_list('brand', flat=True).distinct()
        total_brands = len(brands)
        
        models_by_brand = {}
        for brand in brands:
            count = queryset.filter(brand=brand).count()
            models_by_brand[brand] = count
        
        # Year statistics
        years = queryset.exclude(year_released__isnull=True).values_list('year_released', flat=True).distinct()
        models_by_year = {}
        for year in years:
            count = queryset.filter(year_released=year).count()
            models_by_year[str(year)] = count
        
        # Recent additions (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_additions = queryset.filter(created_at__gte=thirty_days_ago).count()
        
        stats_data = {
            'total_models': total_models,
            'active_models': active_models,
            'discontinued_models': discontinued_models,
            'total_brands': total_brands,
            'models_by_brand': models_by_brand,
            'models_by_year': models_by_year,
            'recent_additions': recent_additions
        }
        
        serializer = TechnicalModelStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Get formatted technical model summary
        """
        technical_model = self.get_object()
        summary_data = technical_model.get_technical_summary()
        
        serializer = TechnicalModelSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_discontinued(self, request, pk=None):
        """
        Mark a technical model as discontinued
        """
        technical_model = self.get_object()
        
        if technical_model.is_discontinued:
            return Response(
                {'message': 'Technical model is already marked as discontinued'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        technical_model.mark_as_discontinued()
        
        serializer = self.get_serializer(technical_model)
        return Response({
            'message': 'Technical model marked as discontinued successfully',
            'technical_model': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """
        Reactivate a technical model
        """
        technical_model = self.get_object()
        
        if technical_model.is_active and not technical_model.is_discontinued:
            return Response(
                {'message': 'Technical model is already active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        technical_model.reactivate()
        
        serializer = self.get_serializer(technical_model)
        return Response({
            'message': 'Technical model reactivated successfully',
            'technical_model': serializer.data
        })
    
    @action(detail=True, methods=['get', 'post'])
    def specifications(self, request, pk=None):
        """
        Get or update specifications for a technical model
        """
        technical_model = self.get_object()
        
        if request.method == 'GET':
            return Response({
                'specifications': technical_model.get_all_specifications()
            })
        
        elif request.method == 'POST':
            serializer = SpecificationSerializer(data=request.data)
            if serializer.is_valid():
                specifications = serializer.validated_data['specifications']
                technical_model.update_specifications(specifications)
                
                return Response({
                    'message': 'Specifications updated successfully',
                    'specifications': technical_model.get_all_specifications()
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_specification(self, request, pk=None):
        """
        Add a single specification to a technical model
        """
        technical_model = self.get_object()
        
        key = request.data.get('key')
        value = request.data.get('value')
        
        if not key:
            return Response(
                {'error': 'Specification key is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        technical_model.set_specification(key, value)
        technical_model.save()
        
        return Response({
            'message': f'Specification "{key}" added successfully',
            'specifications': technical_model.get_all_specifications()
        })
    
    @action(detail=True, methods=['delete'])
    def clear_specifications(self, request, pk=None):
        """
        Clear all specifications for a technical model
        """
        technical_model = self.get_object()
        technical_model.clear_specifications()
        
        return Response({
            'message': 'All specifications cleared successfully',
            'specifications': {}
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recently added technical models (last 30 days)
        """
        thirty_days_ago = datetime.now() - timedelta(days=30)
        models = self.get_queryset().filter(created_at__gte=thirty_days_ago)
        
        serializer = TechnicalModelListSerializer(models, many=True)
        return Response({
            'count': models.count(),
            'technical_models': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def bulk_discontinue(self, request):
        """
        Mark multiple technical models as discontinued
        """
        model_ids = request.data.get('model_ids', [])
        
        if not model_ids:
            return Response(
                {'error': 'Technical model IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        models = TechnicalModel.objects.filter(id__in=model_ids)
        updated_count = 0
        
        for model in models:
            if not model.is_discontinued:
                model.mark_as_discontinued()
                updated_count += 1
        
        return Response({
            'message': f'{updated_count} technical models marked as discontinued',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['post'])
    def bulk_reactivate(self, request):
        """
        Reactivate multiple technical models
        """
        model_ids = request.data.get('model_ids', [])
        
        if not model_ids:
            return Response(
                {'error': 'Technical model IDs are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        models = TechnicalModel.objects.filter(id__in=model_ids)
        updated_count = 0
        
        for model in models:
            if model.is_discontinued or not model.is_active:
                model.reactivate()
                updated_count += 1
        
        return Response({
            'message': f'{updated_count} technical models reactivated',
            'updated_count': updated_count
        })
