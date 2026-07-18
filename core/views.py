from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from parts.mixins import RoleRequiredMixin

from .forms import UserForm, RoleForm, AccessPermissionForm, AuditReportForm
from core.models import CustomUser, AuditLog, AuditReport, Role, AccessPermission
from inventory.models import Location, InventoryItem, StockTransaction, Equipment
from procurement.models import Supplier, PurchaseOrder, PurchaseOrderItem, WorkOrder


# ------------------------------
# AUTHENTICATION
# ------------------------------

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
            'out_of_stock_items': InventoryItem.objects.filter(
                quantity__lte=2
            ).select_related('part', 'location').order_by('quantity')[:10],
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
    if user.has_access('audit.view'):
        report_summary = AuditReport.objects.aggregate(
            total=Count('id'),
            drafts=Count('id', filter=Q(status='draft')),
            submitted=Count('id', filter=Q(status='submitted')),
        )
        context.update({
            'audit_report_total': report_summary['total'],
            'audit_report_drafts': report_summary['drafts'],
            'audit_report_submitted': report_summary['submitted'],
            'recent_audit_reports': AuditReport.objects.select_related('created_by')[:5],
            'recent_audit_logs': AuditLog.objects.select_related('user').order_by('-timestamp')[:6],
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

    def get_queryset(self):
        return super().get_queryset().prefetch_related('permissions', 'users')


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

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        username = self.request.GET.get('user', '').strip()
        action = self.request.GET.get('action', '').strip()
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        if username:
            queryset = queryset.filter(user__username__icontains=username)
        if action:
            queryset = queryset.filter(action__icontains=action)
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)
        return queryset


class AuditReportListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = AuditReport
    template_name = 'auditreport_list.html'
    context_object_name = 'reports'
    permission_required = 'audit.view'
    paginate_by = 25

    def get_queryset(self):
        return super().get_queryset().select_related('created_by')


class AuditReportDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = AuditReport
    template_name = 'auditreport_detail.html'
    context_object_name = 'report'
    permission_required = 'audit.view'

    def get_queryset(self):
        return super().get_queryset().select_related('created_by', 'created_by__role')


class AuditReportCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = AuditReport
    form_class = AuditReportForm
    template_name = 'auditreport_form.html'
    success_url = reverse_lazy('core:auditreport_list')
    permission_required = 'audit.reports.add'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Audit report created successfully.')
        return super().form_valid(form)


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
