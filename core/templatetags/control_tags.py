from django import template

register = template.Library()


@register.filter
def attr(obj, name):
    """Safe getattr for templates."""
    try:
        return getattr(obj, name)
    except Exception:
        return ""
