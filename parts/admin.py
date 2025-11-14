# parts/admin.py
from django.contrib import admin
from .models import Part, Category, Brand

# Simple registration
admin.site.register(Part)
admin.site.register(Category)
admin.site.register(Brand)
