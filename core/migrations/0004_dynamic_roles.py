from django.db import migrations, models
import django.db.models.deletion


ROLE_NAMES = {
    'admin': 'Admin',
    'inventory_manager': 'Inventory Manager',
    'technician': 'Technician',
    'procurement_officer': 'Procurement Officer',
}


def migrate_roles(apps, schema_editor):
    Role = apps.get_model('core', 'Role')
    User = apps.get_model('core', 'CustomUser')
    roles = {
        code: Role.objects.create(code=code, name=name)
        for code, name in ROLE_NAMES.items()
    }
    for user in User.objects.all():
        user.dynamic_role = roles.get(user.role)
        user.save(update_fields=['dynamic_role'])


class Migration(migrations.Migration):
    dependencies = [('core', '0003_customuser_role_default')]
    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('permissions', models.ManyToManyField(blank=True, related_name='roles', to='core.accesspermission')),
            ],
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='customuser', name='dynamic_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.role'),
        ),
        migrations.RunPython(migrate_roles, migrations.RunPython.noop),
        migrations.RemoveField(model_name='customuser', name='role'),
        migrations.RenameField(model_name='customuser', old_name='dynamic_role', new_name='role'),
        migrations.AlterField(
            model_name='customuser', name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='core.role'),
        ),
    ]
