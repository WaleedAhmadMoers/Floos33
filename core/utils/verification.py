from accounts.models import BuyerVerificationRequest, SellerVerificationRequest


def is_buyer_verified(user):
    req = getattr(user, "buyer_verification_request", None)
    return req and req.status == BuyerVerificationRequest.Status.VERIFIED


def is_seller_verified(user):
    req = getattr(user, "seller_verification_request", None)
    return req and req.status == SellerVerificationRequest.Status.APPROVED


def is_verified(user, role=None):
    """
    role: 'buyer', 'seller', or None (any).
    """
    if role == "buyer":
        return is_buyer_verified(user)
    if role == "seller":
        return is_seller_verified(user)
    return is_buyer_verified(user) or is_seller_verified(user)


BLOCK_MESSAGE = (
    "Your account is not verified yet. You can browse, but messaging, quotes, and deal actions are locked "
    "until admin approval."
)


def enforce_verified(request, role=None):
    """
    Return (allowed: bool, message: str or None)
    """
    ok = is_verified(request.user, role)
    return ok, None if ok else BLOCK_MESSAGE
