from django.test import TestCase
from django.urls import reverse

from .forms import UserForm
from .models import AccessPermission, AuditLog, AuditReport, CustomUser, Role


class CustomRBACTests(TestCase):
    def test_sign_in_is_automatically_added_to_activity_log(self):
        user = CustomUser.objects.create_user(
            username='activity-user', password='test-pass'
        )

        self.client.login(username='activity-user', password='test-pass')

        self.assertTrue(AuditLog.objects.filter(
            user=user, action='Signed in'
        ).exists())

    def test_anonymous_protected_page_redirects_to_namespaced_login(self):
        response = self.client.get(reverse('core:role_list'))

        self.assertRedirects(
            response,
            f"{reverse('core:login')}?next={reverse('core:role_list')}",
        )

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

    def test_auditor_can_create_report_but_cannot_manage_users(self):
        role = Role.objects.get(code='auditor')
        auditor = CustomUser.objects.create_user(
            username='auditor', password='test-pass', role=role
        )
        self.client.force_login(auditor)

        response = self.client.post(reverse('core:auditreport_add'), {
            'title': 'Stock controls review',
            'scope': 'Main warehouse',
            'findings': 'Counts matched the system records.',
            'recommendations': 'Continue monthly cycle counts.',
            'status': 'submitted',
        })

        self.assertRedirects(response, reverse('core:auditreport_list'))
        report = AuditReport.objects.get(title='Stock controls review')
        self.assertEqual(report.created_by, auditor)
        self.assertEqual(self.client.get(reverse('core:user_list')).status_code, 403)

    def test_auditor_dashboard_has_audit_workspace(self):
        role = Role.objects.get(code='auditor')
        auditor = CustomUser.objects.create_user(
            username='dashboard-auditor', password='test-pass', role=role
        )
        AuditReport.objects.create(
            title='Dashboard controls review',
            scope='Warehouse controls',
            findings='No exceptions found.',
            status='submitted',
            created_by=auditor,
        )
        self.client.force_login(auditor)

        response = self.client.get(reverse('core:dashboard'))

        self.assertContains(response, 'Audit workspace')
        self.assertContains(response, 'Dashboard controls review')
        self.assertEqual(response.context['audit_report_submitted'], 1)

    def test_auditor_can_view_report_as_printable_document(self):
        role = Role.objects.get(code='auditor')
        auditor = CustomUser.objects.create_user(
            username='document-auditor', password='test-pass', role=role,
            first_name='Document', last_name='Auditor'
        )
        report = AuditReport.objects.create(
            title='Procurement compliance review',
            scope='Purchase orders and receiving',
            findings='All sampled purchase orders had supporting line items.',
            recommendations='Continue quarterly sampling.',
            status='submitted',
            created_by=auditor,
        )
        self.client.force_login(auditor)

        response = self.client.get(reverse('core:auditreport_detail', args=[report.pk]))

        self.assertContains(response, 'Procurement compliance review')
        self.assertContains(response, 'All sampled purchase orders')
        self.assertContains(response, 'Print / Save PDF')

    def test_user_without_report_permission_cannot_create_report(self):
        user = CustomUser.objects.create_user(username='reader', password='test-pass')
        user.access_permissions.add(AccessPermission.objects.get(code='audit.view'))
        self.client.force_login(user)

        self.assertEqual(self.client.get(reverse('core:auditreport_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('core:auditreport_add')).status_code, 403)
