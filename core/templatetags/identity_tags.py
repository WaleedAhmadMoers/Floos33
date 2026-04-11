from django import template

from core.utils.identity import can_view_company_identity, can_view_user_identity, masked_company_label, masked_user_label

register = template.Library()


@register.simple_tag(takes_context=True)
def display_company(context, company):
    viewer = context["request"].user if "request" in context else None
    if can_view_company_identity(viewer, company):
        return company.name
    return masked_company_label(company)


@register.simple_tag(takes_context=True)
def display_user(context, user_obj, role="user"):
    viewer = context["request"].user if "request" in context else None
    if can_view_user_identity(viewer, user_obj):
        return user_obj.full_name or user_obj.email
    return masked_user_label(user_obj, role_hint=role)
