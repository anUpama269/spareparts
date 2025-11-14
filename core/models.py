from django.db import models
from django.contrib.auth.models import AbstractUser

# User roles
ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('inventory_manager', 'Inventory Manager'),
    ('technician', 'Technician'),
    ('procurement_officer', 'Procurement Officer'),
)

class CustomUser(AbstractUser):
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    access_permissions = models.ManyToManyField(
        'AccessPermission', blank=True, related_name='users'
    )
    # email already included in AbstractUser
    # is_staff, is_superuser already included

    def __str__(self):
        return f"{self.username} ({self.role})"

    def has_access(self, code):
        """Check a direct custom permission without using Django groups."""
        if not self.is_authenticated or not self.is_active:
            return False
        if self.is_superuser:
            return True
        prefetched = getattr(self, '_prefetched_objects_cache', {}).get('access_permissions')
        if prefetched is not None:
            return any(permission.code == code for permission in prefetched)
        return self.access_permissions.filter(code=code).exists()


class AccessPermission(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ('module', 'name')

    def __str__(self):
        return f"{self.module}: {self.name}"

class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    object_type = models.CharField(max_length=50, blank=True, null=True)
    object_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
