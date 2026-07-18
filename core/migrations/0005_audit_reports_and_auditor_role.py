from django.db import migrations, models
import django.db.models.deletion


def create_auditor_role(apps, schema_editor):
    Permission = apps.get_model('core', 'AccessPermission')
    Role = apps.get_model('core', 'Role')
    view_permission, _ = Permission.objects.get_or_create(
        code='audit.view',
        defaults={'name': 'View audit records', 'module': 'Audit'},
    )
    add_permission, _ = Permission.objects.get_or_create(
        code='audit.reports.add',
        defaults={
            'name': 'Add audit reports',
            'module': 'Audit',
            'description': 'Create and submit audit reports.',
        },
    )
    role, _ = Role.objects.get_or_create(
        code='auditor',
        defaults={
            'name': 'Auditor',
            'description': 'Reviews activity and creates audit reports.',
        },
    )
    role.permissions.add(view_permission, add_permission)


class Migration(migrations.Migration):
    dependencies = [('core', '0004_dynamic_roles')]
    operations = [
        migrations.CreateModel(
            name='AuditReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('scope', models.CharField(max_length=255)),
                ('findings', models.TextField()),
                ('recommendations', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('submitted', 'Submitted')], default='draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='audit_reports', to='core.customuser')),
            ],
            options={'ordering': ('-created_at',)},
        ),
        migrations.RunPython(create_auditor_role, migrations.RunPython.noop),
    ]
