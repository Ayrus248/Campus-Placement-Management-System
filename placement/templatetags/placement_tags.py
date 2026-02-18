from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg=','):
    """Split string and strip whitespace from each item"""
    if value:
        return [item.strip() for item in value.split(arg)]
    return []