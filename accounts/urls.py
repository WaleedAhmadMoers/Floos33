from django.urls import path

from .views import AccountPasswordChangeDoneView, AccountPasswordChangeView
from .views import AccountPasswordResetCompleteView, AccountPasswordResetConfirmView
from .views import AccountPasswordResetDoneView, AccountPasswordResetView
from .views import BuyerVerificationRequestView, DashboardView, LoginView, LogoutView
from .views import SellerVerificationRequestView, SettingsView, SignupView
from .views import VerificationInvalidView, VerificationSentView, VerificationSuccessView, VerifyEmailView

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify-email/sent/", VerificationSentView.as_view(), name="verification_sent"),
    path("verify-email/success/", VerificationSuccessView.as_view(), name="verification_success"),
    path("verify-email/invalid/", VerificationInvalidView.as_view(), name="verification_invalid"),
    path("verify-email/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/", AccountPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/sent/", AccountPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "password-reset/<uidb64>/<token>/",
        AccountPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        AccountPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("account/dashboard/", DashboardView.as_view(), name="dashboard"),
    path("account/settings/", SettingsView.as_view(), name="settings"),
    path("account/buyer-verification/", BuyerVerificationRequestView.as_view(), name="buyer_verification"),
    path("account/seller-request/", SellerVerificationRequestView.as_view(), name="seller_request"),
    path("account/password/change/", AccountPasswordChangeView.as_view(), name="password_change"),
    path("account/password/change/done/", AccountPasswordChangeDoneView.as_view(), name="password_change_done"),
]
