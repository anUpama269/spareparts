from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .middleware import get_current_user, get_request_context
from .models import AuditLog


TRACKED_MODELS = {
    'CustomUser', 'Role', 'AccessPermission', 'AuditReport',
    'Category', 'Brand', 'Part',
    'Location', 'InventoryItem', 'StockTransaction', 'Equipment',
    'Supplier', 'PurchaseOrder', 'PurchaseOrderItem', 'WorkOrder',
}
SENSITIVE_FIELDS = {'password'}


def _is_tracked(instance):
    return (
        instance.__class__.__name__ in TRACKED_MODELS
        and instance.__class__.__module__ != '__fake__'
    )


def _actor():
    user = get_current_user()
    return user if user and user.pk else None


def _json_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def _snapshot(instance):
    values = {}
    for field in instance._meta.concrete_fields:
        if field.name in SENSITIVE_FIELDS:
            continue
        values[field.name] = _json_value(getattr(instance, field.attname))
    return values


def _request_details(extra=None):
    request_context = get_request_context() or {}
    details = {
        key: request_context[key]
        for key in ('method', 'path')
        if request_context.get(key)
    }
    if extra:
        details.update(extra)
    return details


def _create_log(*, user, action, instance=None, details=None):
    request_context = get_request_context() or {}
    AuditLog.objects.create(
        user=user,
        action=action,
        object_type=instance.__class__.__name__ if instance else None,
        object_id=instance.pk if instance else None,
        ip_address=request_context.get('ip_address'),
        details=_request_details(details),
    )


@receiver(pre_save)
def capture_previous_values(sender, instance, raw=False, **kwargs):
    if raw or not _is_tracked(instance) or not instance.pk:
        return
    previous = sender.objects.filter(pk=instance.pk).first()
    instance._audit_previous_values = _snapshot(previous) if previous else {}


@receiver(post_save)
def record_model_save(sender, instance, created, raw=False, update_fields=None, **kwargs):
    if raw or not _is_tracked(instance):
        return
    if not get_request_context():
        return
    if sender.__name__ == 'CustomUser' and update_fields == frozenset({'last_login'}):
        return

    current = _snapshot(instance)
    if created:
        change_details = {'created_values': current}
        verb = 'Created'
    else:
        previous = getattr(instance, '_audit_previous_values', {})
        changes = {
            field: {'from': previous.get(field), 'to': value}
            for field, value in current.items()
            if previous.get(field) != value
        }
        change_details = {'changes': changes}
        verb = 'Updated'

    _create_log(
        user=_actor(),
        action=f'{verb} {sender._meta.verbose_name}: {instance}',
        instance=instance,
        details=change_details,
    )


@receiver(post_delete)
def record_model_delete(sender, instance, **kwargs):
    if not _is_tracked(instance):
        return
    if not get_request_context():
        return
    actor = _actor()
    if sender.__name__ == 'CustomUser' and actor == instance:
        actor = None
    _create_log(
        user=actor,
        action=f'Deleted {sender._meta.verbose_name}: {instance}',
        instance=instance,
        details={'deleted_values': _snapshot(instance)},
    )


@receiver(user_logged_in)
def record_login(sender, request, user, **kwargs):
    _create_log(user=user, action='Signed in')


@receiver(user_logged_out)
def record_logout(sender, request, user, **kwargs):
    if user and user.pk:
        _create_log(user=user, action='Signed out')
