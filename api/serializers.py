from rest_framework import serializers
from .models import Product, Brand, Supplier, ScrapedData, MarginSetting, ExchangeRate, Competitor


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'created_at']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'code', 'name', 'created_at']


class CompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competitor
        fields = ['id', 'code', 'name', 'website_url', 'is_active', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'simple_sku', 'name', 'brand', 'brand_name',
            'supplier', 'supplier_name', 'cost_with_tax', 'stock_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ScrapedDataSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    competitor_name = serializers.CharField(source='competitor.name', read_only=True)
    brand_name = serializers.CharField(source='product.brand.name', read_only=True)
    
    class Meta:
        model = ScrapedData
        fields = [
            'id', 'extraction_date', 'product', 'product_name', 'product_type',
            'competitor', 'competitor_name', 'price', 'brand_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class MarginSettingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MarginSetting
        fields = ['id', 'user', 'user_name', 'margin_percentage', 'created_at', 'is_active']
        read_only_fields = ['created_at', 'user']


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = ['id', 'from_currency', 'to_currency', 'rate', 'date', 'created_at']
        read_only_fields = ['created_at']


# Analytics Serializers
class PriceBenchmarkSerializer(serializers.Serializer):
    """Serializer for price benchmark analytics"""
    sku = serializers.CharField()
    brand = serializers.CharField()
    product_name = serializers.CharField()
    stock_status = serializers.CharField()
    
    # Supplier prices (calculated with margin)
    ta_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    co_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    dv_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    ge_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    lp_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    ra_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    la_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    cf_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    
    # Competitor prices
    ih_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    ch_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    nt_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    
    # Analysis fields
    min_competitor_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    max_competitor_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    avg_competitor_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    recommended_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)


class InventoryAnalyticsSerializer(serializers.Serializer):
    """Serializer for inventory analytics"""
    total_products = serializers.IntegerField()
    in_stock_count = serializers.IntegerField()
    out_of_stock_count = serializers.IntegerField()
    never_sold_count = serializers.IntegerField()
    
    # By brand breakdown
    brand_analytics = serializers.ListField(
        child=serializers.DictField()
    )
    
    # Recent scraping stats
    last_scrape_date = serializers.DateField()
    products_scraped_today = serializers.IntegerField()
    
    # Price trends
    average_price_change = serializers.DecimalField(max_digits=5, decimal_places=2)