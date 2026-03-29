from django import template

register = template.Library()


@register.simple_tag
def query_without(querydict, *keys):
    """
    Return a querystring (prefixed with '?') with the given keys removed.
    """
    q = querydict.copy()
    for k in keys:
        q.pop(k, None)
    qs = q.urlencode()
    return f"?{qs}" if qs else ""
