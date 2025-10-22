from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Min, Max, Count
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import pandas as pd
import json
from datetime import date, timedelta

from .models import (
    Product, Brand, Supplier, ScrapedData, 
    MarginSetting, ExchangeRate, Competitor
)
from .serializers import (
    ProductSerializer, BrandSerializer, SupplierSerializer,
    ScrapedDataSerializer, MarginSettingSerializer, ExchangeRateSerializer,
    CompetitorSerializer, PriceBenchmarkSerializer, InventoryAnalyticsSerializer
)
from .utils import generate_excel_report, calculate_benchmark_prices
from .forms import MarginForm


class BrandViewSet(viewsets.ModelViewSet):
    """ViewSet for managing brands"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for managing suppliers"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CompetitorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing competitors"""
    queryset = Competitor.objects.all()
    serializer_class = CompetitorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing products with advanced filtering"""
    queryset = Product.objects.select_related('brand', 'supplier').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by brand
        brand = self.request.query_params.get('brand', None)
        if brand:
            queryset = queryset.filter(brand__name__icontains=brand)
        
        # Filter by stock status
        stock_status = self.request.query_params.get('stock_status', None)
        if stock_status:
            queryset = queryset.filter(stock_status=stock_status)
            
        # Search by product name or SKU
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(sku__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """Get all in-stock products"""
        products = self.get_queryset().filter(stock_status='instock')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get all out-of-stock products"""
        products = self.get_queryset().filter(stock_status='outofstock')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ScrapedDataViewSet(viewsets.ModelViewSet):
    """ViewSet for managing scraped price data"""
    queryset = ScrapedData.objects.select_related('product', 'competitor').all()
    serializer_class = ScrapedDataSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            queryset = queryset.filter(extraction_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(extraction_date__lte=date_to)
            
        # Filter by competitor
        competitor = self.request.query_params.get('competitor', None)
        if competitor:
            queryset = queryset.filter(competitor__code=competitor)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest scraped data (today's data)"""
        today_data = self.get_queryset().filter(extraction_date=date.today())
        serializer = self.get_serializer(today_data, many=True)
        return Response(serializer.data)


class MarginSettingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing margin settings"""
    queryset = MarginSetting.objects.all()
    serializer_class = MarginSettingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active margin"""
        current_margin = MarginSetting.get_current_margin()
        return Response({'margin_percentage': current_margin})


class ExchangeRateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing exchange rates"""
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current exchange rate"""
        rate = ExchangeRate.get_current_rate()
        return Response({'rate': rate})


class AnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for analytics and reporting"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def inventory_summary(self, request):
        """Get comprehensive inventory analytics"""
        total_products = Product.objects.count()
        in_stock_count = Product.objects.filter(stock_status='instock').count()
        out_of_stock_count = Product.objects.filter(stock_status='outofstock').count()
        
        # Never sold products (products with no scraped data)
        never_sold_count = Product.objects.filter(scrapeddata__isnull=True).count()
        
        # Brand analytics
        brand_analytics = Brand.objects.annotate(
            product_count=Count('product'),
            in_stock_count=Count('product', filter=Q(product__stock_status='instock')),
            avg_price=Avg('product__scrapeddata__price')
        ).values('name', 'product_count', 'in_stock_count', 'avg_price')
        
        # Recent scraping stats
        last_scrape_date = ScrapedData.objects.aggregate(
            Max('extraction_date')
        )['extraction_date__max']
        
        products_scraped_today = ScrapedData.objects.filter(
            extraction_date=date.today()
        ).values('product').distinct().count()
        
        data = {
            'total_products': total_products,
            'in_stock_count': in_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'never_sold_count': never_sold_count,
            'brand_analytics': list(brand_analytics),
            'last_scrape_date': last_scrape_date,
            'products_scraped_today': products_scraped_today,
            'average_price_change': 0  # TODO: Implement price change calculation
        }
        
        serializer = InventoryAnalyticsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def price_benchmark(self, request):
        """Get price benchmark analysis"""
        stock_filter = request.query_params.get('stock_status', 'instock')
        brand_filter = request.query_params.get('brand', None)
        
        # Get benchmark data using the calculation logic
        benchmark_data = calculate_benchmark_prices(stock_filter, brand_filter)
        
        serializer = PriceBenchmarkSerializer(benchmark_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        """Export data to Excel format"""
        export_type = request.query_params.get('type', 'instock')
        
        if export_type == 'instock':
            products = Product.objects.filter(stock_status='instock')
        elif export_type == 'outstock':
            products = Product.objects.filter(stock_status='outofstock')
        else:
            products = Product.objects.filter(scrapeddata__isnull=True)
        
        # Generate Excel file
        excel_file = generate_excel_report(products, export_type)
        
        response = HttpResponse(
            excel_file.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{export_type}_benchmark.xlsx"'
        return response


# Legacy template views for backward compatibility
@login_required
def dashboard_view(request):
    """Main dashboard view"""
    context = {
        'total_products': Product.objects.count(),
        'in_stock_count': Product.objects.filter(stock_status='instock').count(),
        'out_of_stock_count': Product.objects.filter(stock_status='outofstock').count(),
        'current_margin': MarginSetting.get_current_margin()
    }
    return render(request, 'main/base.html', context)


def margin_set_view(request):
    """Margin setting view with form handling"""
    if request.method == 'POST':
        form = MarginForm(request.POST)
        if form.is_valid():
            margin = form.cleaned_data['new_margin']
            
            # Create new margin setting
            if request.user.is_authenticated:
                MarginSetting.objects.create(
                    user=request.user,
                    margin_percentage=margin
                )
                return render(request, 'main/new_margin.html', {'margin': margin})
            else:
                return render(request, 'main/new_margin_error.html', {'margin': margin})
    
    context = {'current_margin': MarginSetting.get_current_margin()}
    return render(request, 'main/margin_set.html', context)