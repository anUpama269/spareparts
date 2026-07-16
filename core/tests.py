from django.test import TestCase
from django.urls import reverse

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

    def test_public_signup_cannot_choose_role_or_permissions(self):
        response = self.client.get(reverse('core:signup'))
        self.assertNotContains(response, 'name="role"')
        self.assertNotContains(response, 'name="access_permissions"')

        self.client.post(reverse('core:signup'), {
            'username': 'new-user', 'email': 'new@example.com',
            'phone': '', 'password': 'safe-test-password',
            'role': 'admin', 'access_permissions': AccessPermission.objects.first().pk,
        })
        user = CustomUser.objects.get(username='new-user')
        self.assertIsNone(user.role)
        self.assertFalse(user.access_permissions.exists())

    def test_role_permissions_are_dynamic(self):
        permission = AccessPermission.objects.get(code='parts.view')
        role = Role.objects.create(name='Parts Reader', code='parts-reader')
        role.permissions.add(permission)
        user = CustomUser.objects.create_user(username='role-user', password='test-pass', role=role)
        self.assertTrue(user.has_access('parts.view'))
        self.assertFalse(user.has_access('parts.manage'))

    def test_codes_are_automatically_created(self):
        role = Role.objects.create(name='Regional Store Manager')
        permission = AccessPermission.objects.create(
            name='Approve Returns', module='Inventory'
        )
        self.assertEqual(role.code, 'regional-store-manager')
        self.assertEqual(permission.code, 'inventory.approve.returns')
