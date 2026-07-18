from django.test import TestCase
from django.urls import reverse

from core.models import AccessPermission, AuditLog, CustomUser
from parts.models import Brand, Category, Part
from inventory.models import InventoryItem, Location, StockTransaction

from .models import PurchaseOrder, PurchaseOrderItem, Supplier


class PurchaseOrderDisplayTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='buyer', password='test-pass'
        )
        self.user.access_permissions.add(
            AccessPermission.objects.get(code='procurement.view'),
            AccessPermission.objects.get(code='procurement.manage'),
        )
        supplier = Supplier.objects.create(name='Reliable Bearings Ltd')
        part = Part.objects.create(
            name='Roller Bearing',
            part_number='RB-204',
            category=Category.objects.create(name='Bearings'),
            brand=Brand.objects.create(name='Motion Works'),
        )
        self.order = PurchaseOrder.objects.create(
            supplier=supplier, created_by=self.user
        )
        self.item = PurchaseOrderItem.objects.create(
            purchase_order=self.order,
            part=part,
            quantity=20,
            received_quantity=7,
        )
        self.location = Location.objects.create(name='Receiving Bay')
        self.inventory_item = InventoryItem.objects.create(
            part=part, location=self.location, quantity=10, min_quantity=2
        )
        self.client.force_login(self.user)

    def test_purchase_order_list_shows_procured_item_and_quantities(self):
        response = self.client.get(reverse('procurement:purchaseorder_list'))

        self.assertContains(response, 'Roller Bearing')
        self.assertContains(response, 'RB-204')
        self.assertContains(response, 'Reliable Bearings Ltd')
        self.assertContains(response, '>13<', html=False)

    def test_add_item_page_is_linked_to_purchase_order(self):
        response = self.client.get(reverse(
            'procurement:purchaseorderitem_add', args=[self.order.pk]
        ))

        self.assertContains(response, f'Add item to PO-{self.order.pk:05d}')

    def test_remaining_quantity_never_becomes_negative(self):
        self.item.received_quantity = 25

        self.assertEqual(self.item.remaining_quantity, 0)

    def test_receiving_stock_increments_received_quantity(self):
        response = self.client.post(
            reverse('procurement:purchaseorderitem_receive', args=[self.item.pk]),
            {'quantity': 5, 'location': self.location.pk},
        )

        self.assertRedirects(response, reverse('procurement:purchaseorder_list'))
        self.item.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.item.received_quantity, 12)
        self.assertFalse(self.order.received)
        self.inventory_item.refresh_from_db()
        self.assertEqual(self.inventory_item.quantity, 15)
        self.assertTrue(StockTransaction.objects.filter(
            inventory_item=self.inventory_item,
            transaction_type='IN',
            quantity=5,
            performed_by=self.user,
        ).exists())
        activity = AuditLog.objects.get(
            user=self.user,
            object_type='PurchaseOrderItem',
            action__startswith='Updated purchase order item',
        )
        self.assertEqual(
            activity.details['changes']['received_quantity'],
            {'from': 7, 'to': 12},
        )
        self.assertEqual(activity.details['method'], 'POST')
        self.assertEqual(activity.ip_address, '127.0.0.1')

    def test_receiving_final_balance_marks_order_received(self):
        self.client.post(
            reverse('procurement:purchaseorderitem_receive', args=[self.item.pk]),
            {'quantity': 13, 'location': self.location.pk},
        )

        self.item.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.item.received_quantity, 20)
        self.assertTrue(self.order.received)

    def test_cannot_receive_more_than_outstanding_quantity(self):
        self.client.post(
            reverse('procurement:purchaseorderitem_receive', args=[self.item.pk]),
            {'quantity': 14, 'location': self.location.pk},
        )

        self.item.refresh_from_db()
        self.assertEqual(self.item.received_quantity, 7)
