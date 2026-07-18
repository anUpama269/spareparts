from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


def unique_code(model, value, instance_pk=None, separator='-'):
    """Build a readable unique code without exposing identifiers in forms."""
    base = slugify(value) or 'item'
    code = base
    counter = 2
    queryset = model.objects.all()
    if instance_pk:
        queryset = queryset.exclude(pk=instance_pk)
    while queryset.filter(code=code).exists():
        code = f'{base}{separator}{counter}'
        counter += 1
    return code


class AccessPermission(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ('module', 'name')

    def __str__(self):
        return f"{self.module}: {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            module_code = slugify(self.module).replace('-', '.') or 'general'
            name_code = slugify(self.name).replace('-', '.') or 'permission'
            base = f'{module_code}.{name_code}'
            self.code = base
            counter = 2
            while AccessPermission.objects.exclude(pk=self.pk).filter(code=self.code).exists():
                self.code = f'{base}.{counter}'
                counter += 1
        super().save(*args, **kwargs)


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    permissions = models.ManyToManyField(
        AccessPermission, blank=True, related_name='roles'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = unique_code(Role, self.name, self.pk)
        super().save(*args, **kwargs)


class CustomUser(AbstractUser):
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    access_permissions = models.ManyToManyField(
        AccessPermission, blank=True, related_name='users'
    )

    def __str__(self):
        role_name = self.role.name if self.role else 'No role'
        return f"{self.username} ({role_name})"

    def get_effective_access_permissions(self):
        """Return permissions assigned directly or inherited from the user's role."""
        permissions = AccessPermission.objects.filter(users=self)
        if self.role_id:
            permissions = permissions | AccessPermission.objects.filter(roles=self.role)
        return permissions.distinct()

    def has_access(self, code):
        """Check role and direct custom permissions without Django groups."""
        if not self.is_authenticated or not self.is_active:
            return False
        if self.is_superuser:
            return True
        return self.get_effective_access_permissions().filter(code=code).exists()


class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    object_type = models.CharField(max_length=50, blank=True, null=True)
    object_id = models.IntegerField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"


class AuditReport(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    )

    title = models.CharField(max_length=200)
    scope = models.CharField(max_length=255)
    findings = models.TextField()
    recommendations = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name='audit_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title
