# inventory/admin.py
from django.contrib import admin
from .models import Location, InventoryItem, StockTransaction, Equipment

admin.site.register(Location)
admin.site.register(InventoryItem)
admin.site.register(StockTransaction)
admin.site.register(Equipment)
