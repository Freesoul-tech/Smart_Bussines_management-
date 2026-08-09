from django import template

register = template.Library()


@register.filter
def dict_get(value, key):
    if value is None:
        return ''
    return value.get(key, '#')
