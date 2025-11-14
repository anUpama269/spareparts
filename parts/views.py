from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from parts.mixins import RoleRequiredMixin
from .models import Part, Category, Brand
from .forms import PartForm, CategoryForm, BrandForm

# ---------- Parts ----------

class PartListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Part
    template_name = 'part_list.html'
    context_object_name = 'parts'
    allowed_roles = ['admin', 'inventory_manager']

class PartCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Part
    form_class = PartForm
    template_name = 'part_form.html'
    success_url = reverse_lazy('parts:part_list')
    allowed_roles = ['admin', 'inventory_manager']

class PartUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Part
    form_class = PartForm
    template_name = 'part_form.html'
    success_url = reverse_lazy('parts:part_list')
    allowed_roles = ['admin', 'inventory_manager']

class PartDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Part
    template_name = 'part_confirm_delete.html'
    success_url = reverse_lazy('part_list')
    allowed_roles = ['admin', 'inventory_manager']

# ---------- Category ----------

class CategoryListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    allowed_roles = ['admin', 'inventory_manager']

class CategoryCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('parts:category_list')
    allowed_roles = ['admin', 'inventory_manager']

class CategoryUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('parts:category_list')
    allowed_roles = ['admin', 'inventory_manager']

class CategoryDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('parts:category_list')
    allowed_roles = ['admin', 'inventory_manager']

# ---------- Brand ----------

class BrandListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Brand
    template_name = 'brand_list.html'
    context_object_name = 'brands'
    allowed_roles = ['admin', 'inventory_manager']

class BrandCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'brand_form.html'
    success_url = reverse_lazy('parts:brand_list')
    allowed_roles = ['admin', 'inventory_manager']

class BrandUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'brand_form.html'
    success_url = reverse_lazy('parts:brand_list')
    allowed_roles = ['admin', 'inventory_manager']

class BrandDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Brand
    template_name = 'brand_confirm_delete.html'
    success_url = reverse_lazy('brand_list')
    allowed_roles = ['admin', 'inventory_manager']
