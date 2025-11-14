# core/admin.py
from django.contrib import admin
from .models import CustomUser, AuditLog

admin.site.register(CustomUser)
admin.site.register(AuditLog)
