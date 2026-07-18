from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from parts.mixins import RoleRequiredMixin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, WorkOrder
from inventory.models import InventoryItem, Location, StockTransaction
from .forms import SupplierForm, PurchaseOrderForm, PurchaseOrderItemForm, ReceivePurchaseOrderItemForm, WorkOrderForm

# ---------- Supplier Views ----------

class SupplierListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Supplier
    template_name = 'supplier_list.html'
    context_object_name = 'suppliers'
    allowed_roles = ['admin', 'procurement_officer']

class SupplierCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('procurement:supplier_list')
    allowed_roles = ['admin', 'procurement_officer']

class SupplierUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('procurement:supplier_list')
    allowed_roles = ['admin', 'procurement_officer']

class SupplierDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'supplier_confirm_delete.html'
    success_url = reverse_lazy('procurement:supplier_list')
    allowed_roles = ['admin', 'procurement_officer']


# ---------- Purchase Order Views ----------

class PurchaseOrderListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'purchaseorder_list.html'
    context_object_name = 'purchase_orders'
    allowed_roles = ['admin', 'procurement_officer']

    def get_queryset(self):
        return PurchaseOrder.objects.select_related(
            'supplier', 'created_by'
        ).prefetch_related('items__part').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.order_by('name')
        return context

class PurchaseOrderCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchaseorder_form.html'
    success_url = reverse_lazy('procurement:purchaseorder_list')
    allowed_roles = ['admin', 'procurement_officer']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class PurchaseOrderUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchaseorder_form.html'
    success_url = reverse_lazy('procurement:purchaseorder_list')
    allowed_roles = ['admin', 'procurement_officer']

class PurchaseOrderDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = PurchaseOrder
    template_name = 'purchaseorder_confirm_delete.html'
    success_url = reverse_lazy('procurement:purchaseorder_list')
    allowed_roles = ['admin', 'procurement_officer']


# ---------- Purchase Order Item Views ----------

class PurchaseOrderItemListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = PurchaseOrderItem
    template_name = 'purchaseorderitem_list.html'
    context_object_name = 'items'
    allowed_roles = ['admin', 'procurement_officer']

    def get_queryset(self):
        return PurchaseOrderItem.objects.select_related(
            'purchase_order__supplier', 'part'
        ).order_by('-purchase_order__created_at', 'part__name')

class PurchaseOrderItemCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = PurchaseOrderItem
    form_class = PurchaseOrderItemForm
    template_name = 'purchaseorderitem_form.html'
    allowed_roles = ['admin', 'procurement_officer']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchase_order'] = PurchaseOrder.objects.select_related('supplier').get(
            pk=self.kwargs['po_pk']
        )
        return context

    # Link to a specific PurchaseOrder from URL
    def form_valid(self, form):
        po = PurchaseOrder.objects.get(pk=self.kwargs['po_pk'])
        form.instance.purchase_order = po
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('procurement:purchaseorder_list')

class PurchaseOrderItemUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = PurchaseOrderItem
    form_class = PurchaseOrderItemForm
    template_name = 'purchaseorderitem_form.html'
    allowed_roles = ['admin', 'procurement_officer']

    def get_success_url(self):
        return reverse_lazy('procurement:purchaseorderitem_list')

class PurchaseOrderItemDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = PurchaseOrderItem
    template_name = 'purchaseorderitem_confirm_delete.html'
    allowed_roles = ['admin', 'procurement_officer']

    def get_success_url(self):
        return reverse_lazy('procurement:purchaseorderitem_list')


class PurchaseOrderItemReceiveView(LoginRequiredMixin, RoleRequiredMixin, View):
    permission_required = 'procurement.manage'

    @transaction.atomic
    def post(self, request, pk):
        item = get_object_or_404(
            PurchaseOrderItem.objects.select_for_update().select_related(
                'part', 'purchase_order'
            ),
            pk=pk,
        )
        form = ReceivePurchaseOrderItemForm(request.POST, item=item)
        if not form.is_valid():
            messages.error(request, form.errors['quantity'][0])
            return redirect('procurement:purchaseorder_list')

        item.received_quantity += form.cleaned_data['quantity']
        item.save(update_fields=['received_quantity'])

        inventory_item, _ = InventoryItem.objects.select_for_update().get_or_create(
            part=item.part,
            location=form.cleaned_data['location'],
            defaults={'quantity': 0, 'min_quantity': 0},
        )
        InventoryItem.objects.filter(pk=inventory_item.pk).update(
            quantity=F('quantity') + form.cleaned_data['quantity']
        )
        StockTransaction.objects.create(
            inventory_item=inventory_item,
            transaction_type='IN',
            quantity=form.cleaned_data['quantity'],
            performed_by=request.user,
        )

        order = item.purchase_order
        has_outstanding_items = order.items.filter(
            received_quantity__lt=F('quantity')
        ).exists()
        has_items = order.items.exists()
        order.received = has_items and not has_outstanding_items
        order.save(update_fields=['received'])

        messages.success(
            request,
            f'Received {form.cleaned_data["quantity"]} unit(s) of {item.part.name} into {form.cleaned_data["location"].name}.',
        )
        return redirect('procurement:purchaseorder_list')


# ---------- WorkOrder Views ----------

class WorkOrderListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = WorkOrder
    template_name = 'workorder_list.html'
    context_object_name = 'workorders'
    allowed_roles = ['admin', 'procurement_officer', 'technician']

class WorkOrderCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'workorder_form.html'
    success_url = reverse_lazy('procurement:workorder_list')
    allowed_roles = ['admin', 'procurement_officer']

class WorkOrderUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = WorkOrder
    form_class = WorkOrderForm
    template_name = 'workorder_form.html'
    success_url = reverse_lazy('procurement:workorder_list')
    allowed_roles = ['admin', 'procurement_officer']

class WorkOrderDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = WorkOrder
    template_name = 'workorder_confirm_delete.html'
    success_url = reverse_lazy('procurement:workorder_list')
    allowed_roles = ['admin', 'procurement_officer']
