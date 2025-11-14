from django.db import migrations, models


PERMISSIONS = (
    ('parts.view', 'View parts', 'Parts'), ('parts.manage', 'Manage parts', 'Parts'),
    ('inventory.view', 'View inventory', 'Inventory'), ('inventory.manage', 'Manage inventory', 'Inventory'),
    ('locations.view', 'View locations', 'Inventory'), ('locations.manage', 'Manage locations', 'Inventory'),
    ('transactions.view', 'View stock transactions', 'Inventory'), ('transactions.manage', 'Manage stock transactions', 'Inventory'),
    ('equipment.view', 'View equipment', 'Inventory'), ('equipment.manage', 'Manage equipment', 'Inventory'),
    ('procurement.view', 'View procurement', 'Procurement'), ('procurement.manage', 'Manage procurement', 'Procurement'),
    ('workorders.view', 'View work orders', 'Work orders'), ('workorders.manage', 'Manage work orders', 'Work orders'),
    ('audit.view', 'View audit log', 'Administration'), ('users.manage', 'Manage users and permissions', 'Administration'),
)


def create_permissions(apps, schema_editor):
    permission_model = apps.get_model('core', 'AccessPermission')
    for code, name, module in PERMISSIONS:
        permission_model.objects.get_or_create(code=code, defaults={'name': name, 'module': module})


class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='AccessPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=150)),
                ('module', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
            ],
            options={'ordering': ('module', 'name')},
        ),
        migrations.AddField(
            model_name='customuser', name='access_permissions',
            field=models.ManyToManyField(blank=True, related_name='users', to='core.accesspermission'),
        ),
        migrations.RunPython(create_permissions, migrations.RunPython.noop),
    ]
