from django import template

register = template.Library()


@register.filter
def has_access(user, code):
    return bool(getattr(user, 'has_access', lambda unused: False)(code))
