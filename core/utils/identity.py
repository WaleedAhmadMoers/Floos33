from django.core.exceptions import ObjectDoesNotExist

from core.models import BuyerVisibilityGrant, CompanyVisibilityGrant


def can_view_company_identity(viewer, company):
    if company is None:
        return False
    if viewer is None or not viewer.is_authenticated:
        return False
    if viewer.is_staff or company.owner_id == viewer.id:
        return True
    if company.identity_status == company.IdentityStatus.REVEALED:
        return True
    # buyer-specific reveal: viewer is buyer user, target company is seller
    if BuyerVisibilityGrant.objects.filter(
        buyer=viewer,
        status=BuyerVisibilityGrant.Status.APPROVED,
        scope=BuyerVisibilityGrant.Scope.ALL,
    ).exists():
        return True
    if BuyerVisibilityGrant.objects.filter(
        buyer=viewer,
        target_company=company,
        status=BuyerVisibilityGrant.Status.APPROVED,
        scope=BuyerVisibilityGrant.Scope.SINGLE,
    ).exists():
        return True
    return False


def can_view_user_identity(viewer, target_user):
    if target_user is None:
        return False
    if viewer is None or not viewer.is_authenticated:
        return False
    if viewer.is_staff or viewer.id == target_user.id:
        return True
    if target_user.identity_status == target_user.IdentityStatus.REVEALED:
        return True
    viewer_company = None
    try:
        viewer_company = viewer.company
    except ObjectDoesNotExist:
        viewer_company = None
    # seller/company viewing buyer
    if viewer_company and CompanyVisibilityGrant.objects.filter(
        company=viewer_company,
        status=CompanyVisibilityGrant.Status.APPROVED,
        scope=CompanyVisibilityGrant.Scope.ALL,
    ).exists():
        return True
    if viewer_company and CompanyVisibilityGrant.objects.filter(
        company=viewer_company,
        target_buyer=target_user,
        status=CompanyVisibilityGrant.Status.APPROVED,
        scope=CompanyVisibilityGrant.Scope.SINGLE,
    ).exists():
        return True
    return False


def masked_company_label(company):
    return f"Seller ID #{2000 + company.id}"


def masked_user_label(user, role_hint="user"):
    role_label = "User"
    if role_hint == "seller":
        role_label = "Seller"
    elif role_hint == "buyer":
        role_label = "Buyer"
    return f"{role_label} ID #{1000 + user.id}"
