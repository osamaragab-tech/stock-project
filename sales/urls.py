from django.urls import path
from . import views

app_name = "sales"  # <--- ده ضروري علشان يشتغل الـ namespace

urlpatterns = [
    path('', views.sales_dashboard, name='sales_dashboard'),
    path('<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('new/', views.new_sale, name='new_sale'),
    path('product_search/', views.product_search, name='product_search'),
    path('returns/new/', views.new_sale_return, name='new_sale_return'),
    path('returns/<int:return_id>/', views.sale_return_detail, name='sale_return_detail'),
    path("returns/", views.sale_returns_list, name="sale_returns_list"),
    path('get-product-by-barcode/', views.get_product_by_barcode, name='get_product_by_barcode'),
]
