from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, FormView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from parts.mixins import RoleRequiredMixin

from .forms import UserForm, SignupForm, RoleForm, AccessPermissionForm
from core.models import CustomUser, AuditLog, Role, AccessPermission
from inventory.models import Location, InventoryItem, StockTransaction, Equipment
from procurement.models import Supplier, PurchaseOrder, PurchaseOrderItem, WorkOrder


# ------------------------------
# AUTHENTICATION
# ------------------------------

class SignupView(FormView):
    template_name = 'signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('core:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        login(self.request, user)
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('core:dashboard')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('core:login')

    # Optional: allow GET logout (simpler)
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


# ------------------------------
# DASHBOARD (UNIFIED FOR ALL ROLES)
# ------------------------------

@login_required
def dashboard(request):
    user = request.user
    context = {'total_users': CustomUser.objects.count() if user.is_superuser else None}
    if user.has_access('inventory.view'):
        context.update({
            'total_locations': Location.objects.count(),
            'total_items': InventoryItem.objects.count(),
            'total_transactions': StockTransaction.objects.count(),
            'total_equipment': Equipment.objects.count(),
            'locations': Location.objects.all(),
            'items': InventoryItem.objects.select_related('part', 'location').all(),
            'equipment': Equipment.objects.select_related('part', 'location').all(),
            'recent_transactions': StockTransaction.objects.select_related(
                'inventory_item__part', 'performed_by'
            ).order_by('-timestamp')[:5],
            'out_of_stock_items': InventoryItem.objects.filter(quantity=0).select_related('part', 'location')[:10],
        })
    if user.has_access('procurement.view'):
        context.update({
            'suppliers': Supplier.objects.all(),
            'purchase_orders': PurchaseOrder.objects.select_related('supplier').all()[:10],
        })
    if user.has_access('workorders.view'):
        context.update({
            'tasks': WorkOrder.objects.filter(assigned_to=user).order_by('-created_at')[:10],
        })
    return render(request, 'dashboard.html', context)


# ------------------------------
# USER MANAGEMENT (ADMIN ONLY)
# ------------------------------

class UserListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = CustomUser
    template_name = 'user_list.html'
    context_object_name = 'users'
    permission_required = 'users.manage'
    ordering = ['-date_joined']


class UserCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = CustomUser
    form_class = UserForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('core:user_list')
    permission_required = 'users.manage'

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        messages.success(self.request, 'User created successfully!')
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('core:user_list')
    permission_required = 'users.manage'

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            raise PermissionDenied
        messages.success(self.request, 'User updated successfully!')
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'user_confirm_delete.html'
    success_url = reverse_lazy('core:user_list')
    permission_required = 'users.manage'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'User deleted successfully!')
        return super().delete(request, *args, **kwargs)


class RoleListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Role
    template_name = 'role_list.html'
    context_object_name = 'roles'
    permission_required = 'users.manage'


class RoleCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'role_form.html'
    success_url = reverse_lazy('core:role_list')
    permission_required = 'users.manage'


class RoleUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'role_form.html'
    success_url = reverse_lazy('core:role_list')
    permission_required = 'users.manage'


class RoleDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Role
    template_name = 'role_confirm_delete.html'
    success_url = reverse_lazy('core:role_list')
    permission_required = 'users.manage'


class PermissionListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = AccessPermission
    template_name = 'permission_list.html'
    context_object_name = 'access_permissions'
    permission_required = 'users.manage'


class PermissionCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = AccessPermission
    form_class = AccessPermissionForm
    template_name = 'permission_form.html'
    success_url = reverse_lazy('core:permission_list')
    permission_required = 'users.manage'


class PermissionUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = AccessPermission
    form_class = AccessPermissionForm
    template_name = 'permission_form.html'
    success_url = reverse_lazy('core:permission_list')
    permission_required = 'users.manage'


class PermissionDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = AccessPermission
    template_name = 'permission_confirm_delete.html'
    success_url = reverse_lazy('core:permission_list')
    permission_required = 'users.manage'


# ------------------------------
# AUDIT LOGS (ADMIN ONLY)
# ------------------------------

class AuditLogListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = AuditLog
    template_name = 'auditlog_list.html'
    context_object_name = 'logs'
    permission_required = 'audit.view'
    ordering = ['-timestamp']
    paginate_by = 50  # Add pagination for better performance


# ------------------------------
# STATIC PAGES
# ------------------------------

class LandingView(TemplateView):
    template_name = 'home.html'


class ContactView(TemplateView):
    template_name = 'contact.html'

    def post(self, request, *args, **kwargs):
        """Handle contact form submission"""
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        # Basic validation
        if not all([name, email, subject, message_text]):
            messages.error(request, 'Please fill in all required fields.')
            return self.get(request, *args, **kwargs)

        # Here you can:
        # 1. Save to database (create a ContactMessage model)
        # 2. Send email to admin
        # 3. Log the contact request

        # Example: Send email (configure email settings in settings.py)
        try:
            from django.core.mail import send_mail
            from django.conf import settings

            email_subject = f"Contact Form: {subject}"
            email_message = f"""
            Name: {name}
            Email: {email}
            Phone: {phone}
            Subject: {subject}

            Message:
            {message_text}
            """

            send_mail(
                email_subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],  # Add CONTACT_EMAIL in settings.py
                fail_silently=False,
            )

            messages.success(
                request,
                'Thank you for contacting us! We will get back to you soon.'
            )
        except Exception as e:
            # Log the error
            messages.error(
                request,
                'An error occurred while sending your message. Please try again later.'
            )

        return redirect('core:contact')
