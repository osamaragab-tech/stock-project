from django.contrib import admin
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'sku', 'on_hand', 'price', 'total_value')
	search_fields = ('name', 'sku')
	list_filter = ('product_type', 'category')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'parent')