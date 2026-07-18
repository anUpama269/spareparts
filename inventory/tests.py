from django.test import TestCase
from django.urls import reverse

from core.models import AccessPermission, CustomUser
from parts.models import Brand, Category, Part
from .models import InventoryItem, Location


class DynamicInventoryPagesTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='manager', password='test-pass'
        )
        category = Category.objects.create(name='Hydraulics')
        brand = Brand.objects.create(name='Dynamic Brand')
        self.part = Part.objects.create(
            name='Dynamic Pump', part_number='DP-001', category=category, brand=brand
        )
        self.location = Location.objects.create(name='Live Warehouse')
        self.item = InventoryItem.objects.create(
            part=self.part, location=self.location, quantity=4, min_quantity=5
        )
        self.client.force_login(self.user)
        self.user.access_permissions.add(AccessPermission.objects.get(code='inventory.view'))

    def test_inventory_list_renders_database_values(self):
        response = self.client.get(reverse('inventory:inventoryitem_list'))
        self.assertContains(response, 'Dynamic Pump')
        self.assertContains(response, 'Live Warehouse')
        self.assertContains(response, 'Low stock')

    def test_inventory_filters_use_database_fields(self):
        response = self.client.get(
            reverse('inventory:inventoryitem_list'), {'stock_status': 'in_stock'}
        )
        self.assertNotContains(response, 'Dynamic Pump')

    def test_inventory_detail_is_for_requested_record(self):
        response = self.client.get(
            reverse('inventory:inventoryitem_detail', args=[self.item.pk])
        )
        self.assertContains(response, 'DP-001')
        self.assertContains(response, 'Reorder level')

    def test_dashboard_critical_stock_alert_uses_two_unit_boundary(self):
        self.item.quantity = 2
        self.item.save(update_fields=['quantity'])
        response = self.client.get(reverse('core:dashboard'))

        self.assertIn(self.item, response.context['out_of_stock_items'])
        self.assertContains(response, 'Critical Stock Alert')

        self.item.quantity = 3
        self.item.save(update_fields=['quantity'])
        response = self.client.get(reverse('core:dashboard'))

        self.assertNotIn(self.item, response.context['out_of_stock_items'])
