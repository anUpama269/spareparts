from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0002_accesspermission')]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Admin'),
                    ('inventory_manager', 'Inventory Manager'),
                    ('technician', 'Technician'),
                    ('procurement_officer', 'Procurement Officer'),
                ],
                default='technician',
                max_length=30,
            ),
        ),
    ]
