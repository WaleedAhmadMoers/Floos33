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


@register.filter
def split(value, delimiter="/"):
    """
    Split a string into a list so templates can access parts with filters like
    `last` or index-style lookups.
    """
    if value is None:
        return []
    # Normalize Windows backslashes to forward slashes before splitting.
    return str(value).replace("\\", "/").split(delimiter)
