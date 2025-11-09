from django.contrib import admin
from .models import  StockMovement,Transaction





@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'movement_type', 'date')  # استخدمنا movement_type بدل transaction_type
    list_filter = ('movement_type', 'date')


admin.site.register(Transaction)