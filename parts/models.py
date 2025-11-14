from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Part(models.Model):
    name = models.CharField(max_length=200)
    part_number = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='parts/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.part_number})"
