# core/admin.py
from django.contrib import admin
from .models import AuditReport, CustomUser, AuditLog, AccessPermission, Role

admin.site.register(CustomUser)
admin.site.register(AuditLog)
admin.site.register(AccessPermission)
admin.site.register(Role)
admin.site.register(AuditReport)
