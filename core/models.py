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
    # email already included in AbstractUser
    # is_staff, is_superuser already included

    def __str__(self):
        return f"{self.username} ({self.role})"

class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    object_type = models.CharField(max_length=50, blank=True, null=True)
    object_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"
