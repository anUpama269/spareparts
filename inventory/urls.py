from django.urls import path
from .views import (
    LocationListView, LocationCreateView, LocationUpdateView, LocationDeleteView,
    InventoryItemListView, InventoryItemCreateView, InventoryItemUpdateView, InventoryItemDeleteView,
    StockTransactionListView, StockTransactionCreateView, StockTransactionUpdateView, StockTransactionDeleteView,
    EquipmentListView, EquipmentCreateView, EquipmentUpdateView, EquipmentDeleteView,EquipmentDetailView, InventoryItemDetailView
)
app_name = 'inventory'

urlpatterns = [
    # ---------- LOCATION URLS ----------
    path('locations/', LocationListView.as_view(), name='location_list'),
    path('locations/add/', LocationCreateView.as_view(), name='location_add'),
    path('locations/edit/<int:pk>/', LocationUpdateView.as_view(), name='location_edit'),
    path('locations/delete/<int:pk>/', LocationDeleteView.as_view(), name='location_delete'),

    # ---------- INVENTORY ITEM URLS ----------
    path('items/', InventoryItemListView.as_view(), name='inventoryitem_list'),
    path('items/add/', InventoryItemCreateView.as_view(), name='inventoryitem_add'),
    path('items/edit/<int:pk>/', InventoryItemUpdateView.as_view(), name='inventoryitem_edit'),
    path('<int:pk>/', InventoryItemDetailView.as_view(), name='inventoryitem_detail'),

    path('items/delete/<int:pk>/', InventoryItemDeleteView.as_view(), name='inventoryitem_delete'),

    # ---------- STOCK TRANSACTION URLS ----------
    path('transactions/', StockTransactionListView.as_view(), name='stocktransaction_list'),
    path('transactions/add/', StockTransactionCreateView.as_view(), name='stocktransaction_add'),
    path('transactions/edit/<int:pk>/', StockTransactionUpdateView.as_view(), name='stocktransaction_edit'),
    path('transactions/delete/<int:pk>/', StockTransactionDeleteView.as_view(), name='stocktransaction_delete'),

    # ---------- EQUIPMENT URLS ----------
    path('equipment/', EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/add/', EquipmentCreateView.as_view(), name='equipment_add'),
    path('equipment/edit/<int:pk>/', EquipmentUpdateView.as_view(), name='equipment_edit'),
    path('equipment/delete/<int:pk>/', EquipmentDeleteView.as_view(), name='equipment_delete'),
    path('equipment/<int:pk>/', EquipmentDetailView.as_view(), name='equipment_detail'),

]
