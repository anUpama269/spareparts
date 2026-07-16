from django.test import TestCase
from django.urls import reverse

from core.models import AccessPermission, CustomUser
from inventory.models import InventoryItem, Location
from .models import Brand, Category, Part


class DynamicPartPagesTests(TestCase):
    def test_part_stock_is_aggregated_from_inventory(self):
        user = CustomUser.objects.create_user(
            username='parts-manager', password='test-pass'
        )
        category = Category.objects.create(name='Electrical')
        brand = Brand.objects.create(name='Database Brand')
        part = Part.objects.create(
            name='Database Motor', part_number='DB-100', category=category, brand=brand
        )
        InventoryItem.objects.create(
            part=part, location=Location.objects.create(name='Store A'), quantity=7
        )
        self.client.force_login(user)
        user.access_permissions.add(AccessPermission.objects.get(code='parts.view'))
        response = self.client.get(reverse('parts:part_list'))
        self.assertContains(response, 'Database Motor')
        self.assertContains(response, '7 units')
