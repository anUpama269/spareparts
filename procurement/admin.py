# procurement/admin.py
from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, WorkOrder

admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(WorkOrder)
