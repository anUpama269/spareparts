from django.test import TestCase
from django.urls import reverse

from .forms import UserForm
from .models import AccessPermission, CustomUser, Role


class CustomRBACTests(TestCase):
    def test_superuser_has_every_custom_permission(self):
        user = CustomUser.objects.create_superuser(username='root', password='test-pass')
        self.assertTrue(user.has_access('anything.manage'))

    def test_direct_permission_controls_access(self):
        user = CustomUser.objects.create_user(username='operator', password='test-pass')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('parts:part_list')).status_code, 403)
        user.access_permissions.add(AccessPermission.objects.get(code='parts.view'))
        self.assertEqual(self.client.get(reverse('parts:part_list')).status_code, 200)

    def test_non_superuser_cannot_manage_permission_assignments(self):
        user = CustomUser.objects.create_user(username='admin-label', password='test-pass')
        user.access_permissions.add(AccessPermission.objects.get(code='users.manage'))
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('core:user_list')).status_code, 403)

    def test_user_form_assigns_role_without_showing_permissions(self):
        form = UserForm()

        self.assertIn('role', form.fields)
        self.assertNotIn('access_permissions', form.fields)

    def test_role_permissions_are_dynamic(self):
        permission = AccessPermission.objects.get(code='parts.view')
        role = Role.objects.create(name='Parts Reader', code='parts-reader')
        role.permissions.add(permission)
        user = CustomUser.objects.create_user(username='role-user', password='test-pass', role=role)
        self.assertTrue(user.has_access('parts.view'))
        self.assertFalse(user.has_access('parts.manage'))

    def test_permission_added_to_role_is_automatically_inherited(self):
        role = Role.objects.create(name='Store Operator', code='store-operator')
        user = CustomUser.objects.create_user(
            username='store-user', password='test-pass', role=role
        )
        permission = AccessPermission.objects.get(code='inventory.view')

        self.assertFalse(user.has_access('inventory.view'))
        role.permissions.add(permission)

        self.assertTrue(user.has_access('inventory.view'))
        self.assertIn(permission, user.get_effective_access_permissions())

    def test_permission_removed_from_role_is_automatically_revoked(self):
        permission = AccessPermission.objects.get(code='inventory.view')
        role = Role.objects.create(name='Temporary Operator', code='temporary-operator')
        role.permissions.add(permission)
        user = CustomUser.objects.create_user(
            username='temporary-user', password='test-pass', role=role
        )

        role.permissions.remove(permission)

        self.assertFalse(user.has_access('inventory.view'))

    def test_codes_are_automatically_created(self):
        role = Role.objects.create(name='Regional Store Manager')
        permission = AccessPermission.objects.create(
            name='Approve Returns', module='Inventory'
        )
        self.assertEqual(role.code, 'regional-store-manager')
        self.assertEqual(permission.code, 'inventory.approve.returns')
