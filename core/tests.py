from django.test import TestCase
from django.urls import reverse

from .models import AccessPermission, CustomUser


class CustomRBACTests(TestCase):
    def test_superuser_has_every_custom_permission(self):
        user = CustomUser.objects.create_superuser(username='root', password='test-pass', role='admin')
        self.assertTrue(user.has_access('anything.manage'))

    def test_direct_permission_controls_access(self):
        user = CustomUser.objects.create_user(username='operator', password='test-pass', role='technician')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('parts:part_list')).status_code, 403)
        user.access_permissions.add(AccessPermission.objects.get(code='parts.view'))
        self.assertEqual(self.client.get(reverse('parts:part_list')).status_code, 200)

    def test_non_superuser_cannot_manage_permission_assignments(self):
        user = CustomUser.objects.create_user(username='admin-label', password='test-pass', role='admin')
        user.access_permissions.add(AccessPermission.objects.get(code='users.manage'))
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('core:user_list')).status_code, 403)
