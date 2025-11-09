from django.urls import path
from . import views


app_name = 'inventory'


urlpatterns = [
path('', views.inventory_home, name='inventory_home'),
path('add/', views.add_movement, name='add_movement'),
path('report/', views.product_movement_report, name='movement_report'),
]