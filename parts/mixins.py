from django.core.exceptions import PermissionDenied


class RoleRequiredMixin:
    """Compatibility name for the project's direct-permission RBAC guard."""

    permission_required = None

    permission_modules = {
        'part': 'parts', 'category': 'parts', 'brand': 'parts',
        'inventoryitem': 'inventory', 'location': 'locations',
        'stocktransaction': 'transactions', 'equipment': 'equipment',
        'supplier': 'procurement', 'purchaseorder': 'procurement',
        'purchaseorderitem': 'procurement', 'workorder': 'workorders',
        'auditlog': 'audit',
    }

    def get_permission_required(self):
        if self.permission_required:
            return self.permission_required
        model_name = self.model._meta.model_name
        module = self.permission_modules.get(model_name, model_name)
        action = 'view' if self.__class__.__name__.endswith(('ListView', 'DetailView')) else 'manage'
        return f'{module}.{action}'

    def dispatch(self, request, *args, **kwargs):
        if self.get_permission_required() == 'users.manage' and not request.user.is_superuser:
            raise PermissionDenied("Only a super admin can manage users and permissions.")
        if request.user.is_authenticated and request.user.has_access(self.get_permission_required()):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied("You do not have permission to access this page.")
