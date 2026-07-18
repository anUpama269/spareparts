from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0005_audit_reports_and_auditor_role')]
    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='details',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
    ]
