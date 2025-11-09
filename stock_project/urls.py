"""
URL configuration for stock_project project.

This file defines the URL routing for the project, including:
- Admin panel
- Language switching (i18n)
- App URLs (inventory)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

# رابط تغيير اللغة (يجب أن يكون خارج i18n_patterns)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# الروابط الأساسية داخل النمط متعدد اللغات
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),  # روابط التطبيق الرئيسي
    path('sales/', include('sales.urls')),  # 👈 ربط التطبيق الجديد
    path('accounts/', include('accounts.urls')),  # 👈 ربط تطبيق الحسابات
    path('products/', include('products.urls')),  # 👈 ربط تطبيق المنتجات
    path("companies/", include("companies.urls")),  # 👈 ربط تطبيق الشركات
)

# إضافة دعم الملفات الثابتة والإعلامية في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
