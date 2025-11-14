from django.db import models
from parts.models import Part
from core.models import CustomUser

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    min_quantity = models.PositiveIntegerField(default=0)  # Reorder threshold

    class Meta:
        unique_together = ('part', 'location')

    def __str__(self):
        return f"{self.part.name} at {self.location.name}"

TRANSACTION_TYPE_CHOICES = (
    ('IN', 'Stock In'),
    ('OUT', 'Stock Out'),
    ('TRANSFER', 'Transfer'),
)

class StockTransaction(models.Model):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    destination_location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_destination'
    )

    def __str__(self):
        return f"{self.transaction_type} - {self.inventory_item} ({self.quantity})"

class Equipment(models.Model):
    name = models.CharField(max_length=200)
    part = models.ForeignKey(Part, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    last_maintenance_date = models.DateField(blank=True, null=True)
    next_maintenance_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
