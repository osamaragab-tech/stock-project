from django.contrib import admin
from .models import Sale, SaleItem, SaleReturn, SaleReturnItem

admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(SaleReturn)
admin.site.register(SaleReturnItem)
