from django import forms
from .models import Part, Category, Brand

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'part_number', 'category', 'brand', 'description', 'barcode', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
        }
