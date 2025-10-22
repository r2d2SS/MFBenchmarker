from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Product, MarginSetting, ScrapedData
import json
from datetime import date


# Views with real database data
def margin_set(request):
    """Main dashboard view"""
    
    # Handle margin update form
    if request.method == 'POST' and 'new_margin' in request.POST:
        try:
            admin_user = User.objects.get(username='admin')
            new_margin = int(request.POST.get('new_margin', 40))
            
            # Create new margin setting
            MarginSetting.objects.create(
                user=admin_user,
                margin_percentage=new_margin,
                is_active=True
            )
        except (User.DoesNotExist, ValueError):
            pass  # Handle silently for demo
    
    # Get current margin setting
    current_margin = MarginSetting.get_current_margin()
    
    # Get some stats
    from .models import Brand
    total_products = Product.objects.count()
    brands_count = Brand.objects.count()
    in_stock_count = Product.objects.filter(stock_status='instock').count()
    out_of_stock_count = Product.objects.filter(stock_status='outofstock').count()
    never_sold_count = Product.objects.filter(stock_status='neversold').count()
    
    context = {
        'current_margin': current_margin,
        'margin': current_margin,  # For the form
        'total_products': total_products,
        'brands_count': brands_count,
        'in_stock_count': in_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'never_sold_count': never_sold_count,
        'message': 'MF Benchmarker - Portfolio Demo with Real Data'
    }
    return render(request, 'main/margin_set.html', context)


def inStock(request):
    """In stock products view"""
    # Get in-stock products
    in_stock_products = Product.objects.filter(stock_status='instock').select_related('brand')
    
    # Format data for template
    products_data = []
    for index, product in enumerate(in_stock_products):
        # Get competitor prices for this product
        scraped_prices = ScrapedData.objects.filter(product=product).select_related('competitor')
        competitor_prices = {}
        for price_data in scraped_prices:
            competitor_prices[price_data.competitor.code] = float(price_data.price)
        
        products_data.append({
            'index': index,
            'sku': product.sku,
            'marca': product.brand.name,
            'TA': competitor_prices.get('TA'),
            'CO': competitor_prices.get('CI'),
            'IH': competitor_prices.get('IR'),
            'CH': competitor_prices.get('CH'),
            'NT': competitor_prices.get('NT'),
            'cost': float(product.cost_with_tax) if product.cost_with_tax else None
        })
    
    context = {'d': products_data}
    return render(request, 'main/in_stock.html', context)


def outOfStock(request):
    """Out of stock products view"""
    # Get out-of-stock products
    out_of_stock_products = Product.objects.filter(stock_status='outofstock').select_related('brand')
    
    # Format data for template
    products_data = []
    for index, product in enumerate(out_of_stock_products):
        # Get competitor prices for this product
        scraped_prices = ScrapedData.objects.filter(product=product).select_related('competitor')
        competitor_prices = {}
        for price_data in scraped_prices:
            competitor_prices[price_data.competitor.code] = float(price_data.price)
        
        products_data.append({
            'index': index,
            'sku': product.sku,
            'marca': product.brand.name,
            'TA': competitor_prices.get('TA'),
            'CO': competitor_prices.get('CI'),
            'IH': competitor_prices.get('IR'),
            'CH': competitor_prices.get('CH'),
            'NT': competitor_prices.get('NT'),
            'cost': float(product.cost_with_tax) if product.cost_with_tax else None
        })
    
    context = {'d': products_data}
    return render(request, 'main/out_of_stock.html', context)


def neverSold(request):
    """Never sold products view"""
    # Get never sold products
    never_sold_products = Product.objects.filter(stock_status='neversold').select_related('brand')
    
    # Format data for template
    products_data = []
    for index, product in enumerate(never_sold_products):
        # Get competitor prices for this product
        scraped_prices = ScrapedData.objects.filter(product=product).select_related('competitor')
        competitor_prices = {}
        for price_data in scraped_prices:
            competitor_prices[price_data.competitor.code] = float(price_data.price)
        
        products_data.append({
            'index': index,
            'Product': product.name,
            'ProductType': 'Single Cigar',  # Default type
            'IH': competitor_prices.get('IR'),
            'CH': competitor_prices.get('CH'),
            'NT': competitor_prices.get('NT'),
            'PrecioAComprar': float(product.cost_with_tax) if product.cost_with_tax else None
        })
    
    context = {'d': products_data}
    return render(request, 'main/never_sold.html', context)


def in_export(request):
    """Export in stock data - simplified for development"""
    return HttpResponse("In Stock Export - Feature available in production mode with database")


def out_export(request):
    """Export out of stock data - simplified for development"""
    return HttpResponse("Out of Stock Export - Feature available in production mode with database")


def n_export(request):
    """Export never sold data - simplified for development"""
    return HttpResponse("Never Sold Export - Feature available in production mode with database")