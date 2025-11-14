from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from parts.mixins import RoleRequiredMixin
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, WorkOrder
from .forms import SupplierForm, PurchaseOrderForm, PurchaseOrderItemForm, WorkOrderForm

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

class PurchaseOrderItemCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = PurchaseOrderItem
    form_class = PurchaseOrderItemForm
    template_name = 'purchaseorderitem_form.html'
    allowed_roles = ['admin', 'procurement_officer']

    # Link to a specific PurchaseOrder from URL
    def form_valid(self, form):
        po = PurchaseOrder.objects.get(pk=self.kwargs['po_pk'])
        form.instance.purchase_order = po
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('procurement:purchaseorderitem_list')

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
