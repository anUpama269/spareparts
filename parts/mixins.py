from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin:
    """
    Allows access only if:
    - User is superuser (admin)
    - User's role is in allowed_roles list
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):

        # 1. Superuser always allowed
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # 2. If user has a role & it's allowed -> allow
        if hasattr(request.user, "role") and request.user.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        # 3. Other wise → No access
        raise PermissionDenied("You do not have permission to access this page.")
