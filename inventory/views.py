from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from parts.mixins import RoleRequiredMixin
from django.db.models import F, Q, Sum
from parts.models import Category, Brand

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

    def get_queryset(self):
        queryset = InventoryItem.objects.select_related(
            'part__category', 'part__brand', 'location'
        )
        search = self.request.GET.get('search', '').strip()
        category = self.request.GET.get('category', '')
        brand = self.request.GET.get('brand', '')
        status = self.request.GET.get('stock_status', '')
        if search:
            queryset = queryset.filter(
                Q(part__name__icontains=search) |
                Q(part__part_number__icontains=search) |
                Q(location__name__icontains=search)
            )
        if category:
            queryset = queryset.filter(part__category_id=category)
        if brand:
            queryset = queryset.filter(part__brand_id=brand)
        if status == 'out_of_stock':
            queryset = queryset.filter(quantity=0)
        elif status == 'low_stock':
            queryset = queryset.filter(quantity__gt=0, quantity__lte=F('min_quantity'))
        elif status == 'in_stock':
            queryset = queryset.filter(quantity__gt=F('min_quantity'))
        return queryset.order_by('part__name', 'location__name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_items = InventoryItem.objects.select_related('part', 'location')
        context['out_of_stock_items'] = all_items.filter(quantity=0)
        context['low_stock_items'] = all_items.filter(
            quantity__gt=0, quantity__lte=F('min_quantity')
        )
        context['categories'] = Category.objects.order_by('name')
        context['brands'] = Brand.objects.order_by('name')
        context['total_quantity'] = all_items.aggregate(total=Sum('quantity'))['total'] or 0
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

    def form_valid(self, form):
        form.instance.performed_by = self.request.user
        return super().form_valid(form)


class StockTransactionUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = StockTransaction
    form_class = StockTransactionForm
    template_name = 'stocktransaction_form.html'
    success_url = reverse_lazy('inventory:stocktransaction_list')
    allowed_roles = ['inventory_manager']


class StockTransactionDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = StockTransaction
    template_name = 'stocktransaction_delete.html'
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
