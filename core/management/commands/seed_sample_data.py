from datetime import date, timedelta

from django.core.management.base import BaseCommand

from core.models import AccessPermission, AuditReport, CustomUser, Role
from inventory.models import Equipment, InventoryItem, Location, StockTransaction
from parts.models import Brand, Category, Part
from procurement.models import PurchaseOrder, PurchaseOrderItem, Supplier, WorkOrder


class Command(BaseCommand):
    help = 'Create a repeatable set of sample records for local development and demos.'

    SAMPLE_PASSWORD = 'SamplePass123!'

    def handle(self, *args, **options):
        roles = self._roles()
        users = self._users(roles)

        mechanical, _ = Category.objects.get_or_create(name='Mechanical')
        electrical, _ = Category.objects.get_or_create(name='Electrical')
        acme, _ = Brand.objects.get_or_create(name='Acme Industrial')
        vertex, _ = Brand.objects.get_or_create(name='Vertex Components')

        bearing, _ = Part.objects.update_or_create(
            part_number='BRG-6205',
            defaults={'name': 'Deep Groove Bearing 6205', 'category': mechanical, 'brand': acme, 'description': 'General-purpose sealed bearing.', 'barcode': '8901000006205'},
        )
        belt, _ = Part.objects.update_or_create(
            part_number='BLT-A42',
            defaults={'name': 'Industrial V-Belt A42', 'category': mechanical, 'brand': vertex, 'description': 'Heavy-duty drive belt.', 'barcode': '8901000000042'},
        )
        relay, _ = Part.objects.update_or_create(
            part_number='RLY-24V-08',
            defaults={'name': '24V Control Relay', 'category': electrical, 'brand': vertex, 'description': 'Eight-pin industrial control relay.', 'barcode': '8901000024008'},
        )

        main_store, _ = Location.objects.get_or_create(name='Main Store', defaults={'address': 'Plant 1, Ground Floor'})
        maintenance, _ = Location.objects.get_or_create(name='Maintenance Crib', defaults={'address': 'Plant 1, Workshop'})
        bearing_stock, _ = InventoryItem.objects.update_or_create(part=bearing, location=main_store, defaults={'quantity': 84, 'min_quantity': 20})
        belt_stock, _ = InventoryItem.objects.update_or_create(part=belt, location=main_store, defaults={'quantity': 2, 'min_quantity': 15})
        InventoryItem.objects.update_or_create(part=relay, location=maintenance, defaults={'quantity': 32, 'min_quantity': 10})

        Equipment.objects.update_or_create(
            name='Assembly Line Conveyor A',
            defaults={'part': bearing, 'location': maintenance, 'last_maintenance_date': date.today() - timedelta(days=25), 'next_maintenance_date': date.today() + timedelta(days=65)},
        )
        supplier, _ = Supplier.objects.update_or_create(
            name='Southern Industrial Supplies',
            defaults={'contact_person': 'Priya Raman', 'email': 'orders@example.test', 'phone': '9876500010', 'address': 'Chennai, Tamil Nadu'},
        )
        purchase_order, _ = PurchaseOrder.objects.get_or_create(supplier=supplier, created_by=users['procurement'], received=False)
        PurchaseOrderItem.objects.update_or_create(purchase_order=purchase_order, part=belt, defaults={'quantity': 40, 'received_quantity': 0})
        WorkOrder.objects.update_or_create(
            title='Inspect conveyor drive assembly',
            defaults={'description': 'Check bearing noise, belt tension, and alignment.', 'assigned_to': users['technician'], 'purchase_order': purchase_order, 'status': 'In Progress'},
        )

        if not StockTransaction.objects.filter(inventory_item=bearing_stock, performed_by=users['inventory'], quantity=24).exists():
            StockTransaction.objects.create(inventory_item=bearing_stock, transaction_type='IN', quantity=24, performed_by=users['inventory'])
        if not StockTransaction.objects.filter(inventory_item=belt_stock, performed_by=users['inventory'], quantity=3).exists():
            StockTransaction.objects.create(inventory_item=belt_stock, transaction_type='OUT', quantity=3, performed_by=users['inventory'])

        AuditReport.objects.get_or_create(
            title='Quarterly inventory controls review',
            defaults={'scope': 'Main Store and Maintenance Crib', 'findings': 'Cycle counts were accurate overall. V-belt stock is below its reorder threshold.', 'recommendations': 'Approve the open replenishment order and schedule weekly counts for critical drive components.', 'status': 'submitted', 'created_by': users['auditor']},
        )
        self.stdout.write(self.style.SUCCESS('Sample data is ready.'))
        self.stdout.write('Sample users (password for each: SamplePass123!):')
        self.stdout.write('  Ten staff accounts were created (usernames end in .sample).')

    def _roles(self):
        permission_codes = {
            'auditor': ['audit.view', 'audit.reports.add'],
            'inventory_manager': ['parts.view', 'inventory.view', 'inventory.manage', 'locations.view', 'transactions.view', 'transactions.manage', 'equipment.view'],
            'procurement_officer': ['parts.view', 'inventory.view', 'procurement.view', 'procurement.manage'],
            'technician': ['parts.view', 'inventory.view', 'equipment.view', 'workorders.view', 'workorders.manage'],
        }
        names = {'auditor': 'Auditor', 'inventory_manager': 'Inventory Manager', 'procurement_officer': 'Procurement Officer', 'technician': 'Technician'}
        roles = {}
        for code, permission_list in permission_codes.items():
            role, _ = Role.objects.get_or_create(code=code, defaults={'name': names[code]})
            permissions = AccessPermission.objects.filter(code__in=permission_list)
            role.permissions.add(*permissions)
            roles[code] = role
        return roles

    def _users(self, roles):
        specs = {
            'auditor': ('ananya.iyer.sample', 'Ananya', 'Iyer', roles['auditor']),
            'auditor_2': ('rohan.mehta.sample', 'Rohan', 'Mehta', roles['auditor']),
            'inventory': ('kavya.nair.sample', 'Kavya', 'Nair', roles['inventory_manager']),
            'inventory_2': ('arjun.rao.sample', 'Arjun', 'Rao', roles['inventory_manager']),
            'inventory_3': ('meera.shah.sample', 'Meera', 'Shah', roles['inventory_manager']),
            'procurement': ('vikram.singh.sample', 'Vikram', 'Singh', roles['procurement_officer']),
            'procurement_2': ('divya.patel.sample', 'Divya', 'Patel', roles['procurement_officer']),
            'technician': ('sanjay.kumar.sample', 'Sanjay', 'Kumar', roles['technician']),
            'technician_2': ('neha.joshi.sample', 'Neha', 'Joshi', roles['technician']),
            'technician_3': ('imran.khan.sample', 'Imran', 'Khan', roles['technician']),
        }
        users = {}
        for key, (username, first_name, last_name, role) in specs.items():
            email_name = username.removesuffix('.sample')
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{email_name}@example.test',
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'is_active': True,
                },
            )
            if created:
                user.set_password(self.SAMPLE_PASSWORD)
            user.first_name = first_name
            user.last_name = last_name
            user.email = f'{email_name}@example.test'
            user.role = role
            user.is_active = True
            user.save()
            users[key] = user
        return users
