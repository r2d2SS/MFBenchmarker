# API URLs for MF Benchmarker

from django.urls import path, include
# from rest_framework.routers import DefaultRouter  # Commented out for now

# Import simplified views for development
from .simple_views import inStock, outOfStock, neverSold, out_export, in_export, n_export, margin_set

# Basic URL patterns for now - we'll add the API later
urlpatterns = [
    # Main dashboard
    path('', margin_set, name='dashboard'),
    
    # Template views 
    path('inStock/', inStock, name='in_stock'),
    path('outOfStock/', outOfStock, name='out_of_stock'),  
    path('neverSold/', neverSold, name='never_sold'),
    path('outOfStockExport/', out_export, name='out_export'),
    path('inStockExport/', in_export, name='in_export'),
    path('neverSoldExport/', n_export, name='n_export'),
    
    # API endpoints will be added later
    # path('api/v1/', include(router.urls)),
]
