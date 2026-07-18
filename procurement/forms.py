from django import forms
from .models import Supplier, PurchaseOrder, PurchaseOrderItem, WorkOrder
from parts.models import Part
from inventory.models import Location
from core.models import CustomUser

# ---------- Supplier Form ----------

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']


# ---------- Purchase Order Form ----------

class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'received']  # created_by will be set in the view

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.created_by = user
        if commit:
            instance.save()
        return instance


# ---------- Purchase Order Item Form ----------

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['part', 'quantity', 'received_quantity']
        # purchase_order is set in view automatically

    def save(self, commit=True, purchase_order=None):
        instance = super().save(commit=False)
        if purchase_order:
            instance.purchase_order = purchase_order
        if commit:
            instance.save()
        return instance


class ReceivePurchaseOrderItemForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)
    location = forms.ModelChoiceField(queryset=Location.objects.none())

    def __init__(self, *args, item, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
        self.fields['quantity'].widget.attrs.update({
            'class': 'form-control form-control-sm',
            'max': item.remaining_quantity,
            'aria-label': f'Quantity received for {item.part.name}',
        })
        self.fields['location'].queryset = Location.objects.order_by('name')
        self.fields['location'].widget.attrs.update({
            'class': 'form-select form-select-sm',
            'aria-label': f'Receiving location for {item.part.name}',
        })

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity > self.item.remaining_quantity:
            raise forms.ValidationError(
                f'Only {self.item.remaining_quantity} unit(s) remain outstanding.'
            )
        return quantity


# ---------- Work Order Form ----------

class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['title', 'description', 'assigned_to', 'purchase_order', 'status']

    # Optionally, restrict purchase_order choices for dropdown if needed
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only include purchase orders that are not received yet
        self.fields['purchase_order'].queryset = PurchaseOrder.objects.filter(received=False)
