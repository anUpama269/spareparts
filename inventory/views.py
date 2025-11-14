from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from parts.mixins import RoleRequiredMixin
from django.db.models import F

from .models import Location, InventoryItem, StockTransaction, Equipment
from .forms import (
    LocationForm,
    InventoryItemForm,
    StockTransactionForm,
    EquipmentForm
)


# -----------------------------------------------------------------------
# LOCATION VIEWS (Inventory Manager + Superuser)
# -----------------------------------------------------------------------

class LocationListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Location
    template_name = 'location_list.html'
    context_object_name = 'locations'
    allowed_roles = ['inventory_manager']


class LocationCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'location_form.html'
    success_url = reverse_lazy('inventory:location_list')
    allowed_roles = ['inventory_manager']


class LocationUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'location_form.html'
    success_url = reverse_lazy('inventory:location_list')
    allowed_roles = ['inventory_manager']


class LocationDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Location
    template_name = 'location_confirm_delete.html'
    success_url = reverse_lazy('inventory:location_list')
    allowed_roles = ['inventory_manager']



# -----------------------------------------------------------------------
# INVENTORY ITEM VIEWS
# Full Access → Inventory Manager + Superuser
# View Only → Technician
# -----------------------------------------------------------------------

class InventoryItemListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = InventoryItem
    template_name = 'inventoryitem_list.html'
    context_object_name = 'items'
    allowed_roles = ['inventory_manager', 'technician']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['out_of_stock_items'] = InventoryItem.objects.filter(quantity__lte=0)
        context['low_stock_items'] = InventoryItem.objects.filter(
            quantity__gt=0, quantity__lte=F('min_quantity')
        )
        return context


class InventoryItemCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventoryitem_form.html'
    success_url = reverse_lazy('inventory:inventoryitem_list')
    allowed_roles = ['inventory_manager']


class InventoryItemUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventoryitem_form.html'
    success_url = reverse_lazy('inventory:inventoryitem_list')
    allowed_roles = ['inventory_manager']

class InventoryItemDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = InventoryItem
    template_name = 'inventoryitem_detail.html'  # create this template
    context_object_name = 'item'
    allowed_roles = ['inventory_manager', 'technician']

class InventoryItemDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventoryitem_confirm_delete.html'
    success_url = reverse_lazy('inventory:inventoryitem_list')
    allowed_roles = ['inventory_manager']



# -----------------------------------------------------------------------
# STOCK TRANSACTION
# Only Inventory Manager + Superuser
# -----------------------------------------------------------------------

class StockTransactionListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = StockTransaction
    template_name = 'stocktransaction_list.html'
    context_object_name = 'transactions'
    allowed_roles = ['inventory_manager']


class StockTransactionCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = StockTransaction
    form_class = StockTransactionForm
    template_name = 'stocktransaction_form.html'
    success_url = reverse_lazy('inventory:stocktransaction_list')
    allowed_roles = ['inventory_manager']


class StockTransactionUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = StockTransaction
    form_class = StockTransactionForm
    template_name = 'stocktransaction_form.html'
    success_url = reverse_lazy('inventory:stocktransaction_list')
    allowed_roles = ['inventory_manager']


class StockTransactionDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = StockTransaction
    template_name = 'stocktransaction_confirm_delete.html'
    success_url = reverse_lazy('inventory:stocktransaction_list')
    allowed_roles = ['inventory_manager']



# -----------------------------------------------------------------------
# EQUIPMENT VIEWS
# Full Access → Inventory Manager + Superuser
# View Only → Technician
# -----------------------------------------------------------------------

class EquipmentListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Equipment
    template_name = 'equipment_list.html'
    context_object_name = 'equipment_list'
    allowed_roles = ['inventory_manager', 'technician']


class EquipmentCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'equipment_form.html'
    success_url = reverse_lazy('inventory:equipment_list')
    allowed_roles = ['inventory_manager']


class EquipmentUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'equipment_form.html'
    success_url = reverse_lazy('inventory:equipment_list')
    allowed_roles = ['inventory_manager']


class EquipmentDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Equipment
    template_name = 'equipment_confirm_delete.html'
    success_url = reverse_lazy('inventory:equipment_list')
    allowed_roles = ['inventory_manager']

class EquipmentDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = Equipment
    template_name = 'equipment_detail.html'
    context_object_name = 'equipment'
    allowed_roles = ['inventory_manager', 'technician']