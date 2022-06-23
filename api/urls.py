# stores the urls local to this app


from django.urls import path
from .views import base, inStock, outOfStock, neverSold, out_export, in_export, n_export, margin_set
# blank urls calls the main function we created with the Hello
urlpatterns = [
    path('', margin_set),
    path('inStock', inStock),
    path('outOfStock', outOfStock),
    path('neverSold', neverSold),
    path('outOfStockExport', out_export),
    path('inStockExport', in_export),
    path('neverSoldExport', n_export),
]
