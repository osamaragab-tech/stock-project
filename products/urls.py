from django.urls import path
from . import views
from . import views_barcode


app_name = 'products'

urlpatterns = [
    path('', views.products_list, name='products_list'),
    path('new/', views.new_product, name='new_product'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('print-barcode/<int:pk>/', views_barcode.print_barcode, name='print_barcode'),
    path('print-multiple-barcodes/', views_barcode.print_multiple_barcodes, name='print_multiple_barcodes'),
]
