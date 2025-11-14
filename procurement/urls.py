from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_add'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

    # Purchase Orders
    path('purchaseorders/', views.PurchaseOrderListView.as_view(), name='purchaseorder_list'),
    path('purchaseorders/add/', views.PurchaseOrderCreateView.as_view(), name='purchaseorder_add'),
    path('purchaseorders/<int:pk>/edit/', views.PurchaseOrderUpdateView.as_view(), name='purchaseorder_edit'),
    path('purchaseorders/<int:pk>/delete/', views.PurchaseOrderDeleteView.as_view(), name='purchaseorder_delete'),

    # Purchase Order Items (nested under PO)
    path('purchaseorders/<int:po_pk>/items/add/', views.PurchaseOrderItemCreateView.as_view(), name='purchaseorderitem_add'),
# Purchase Order Items List
    path('purchaseorderitems/', views.PurchaseOrderItemListView.as_view(), name='purchaseorderitem_list'),

    path('purchaseorderitems/<int:pk>/edit/', views.PurchaseOrderItemUpdateView.as_view(), name='purchaseorderitem_edit'),
    path('purchaseorderitems/<int:pk>/delete/', views.PurchaseOrderItemDeleteView.as_view(), name='purchaseorderitem_delete'),

    # Work Orders
    path('workorders/', views.WorkOrderListView.as_view(), name='workorder_list'),
    path('workorders/add/', views.WorkOrderCreateView.as_view(), name='workorder_add'),
    path('workorders/<int:pk>/edit/', views.WorkOrderUpdateView.as_view(), name='workorder_edit'),
    path('workorders/<int:pk>/delete/', views.WorkOrderDeleteView.as_view(), name='workorder_delete'),
]
