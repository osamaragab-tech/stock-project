from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('', views.companies_list, name='companies_list'),
    path('new/', views.create_company, name='create_company'),
    path('<int:pk>/edit/', views.edit_company, name='edit_company'),
    path('<int:pk>/delete/', views.delete_company, name='delete_company'),
    path('<int:pk>/activate/', views.activate_company, name='activate_company'),  # ✅ جديد
    path('close/', views.close_company, name='close_company'),
]
