from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.contrib.auth.views import PasswordResetCompleteView, PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView

from .forms import AccountPasswordChangeForm, AccountPasswordResetForm, AccountSetPasswordForm
from .forms import AccountSettingsForm, BuyerVerificationRequestForm, LoginForm
from .forms import SellerVerificationRequestForm, SignupForm
from .models import BuyerVerificationRequest, SellerVerificationRequest


class RedirectToNextMixin:
    success_url = reverse_lazy("core:home")

    def get_success_url(self):
        redirect_to = self.request.POST.get("next") or self.request.GET.get("next")
        if redirect_to and url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return redirect_to
        return str(self.success_url)


class AccountContextMixin:
    def get_seller_request(self):
        return SellerVerificationRequest.objects.filter(user=self.request.user).first()

    def get_buyer_request(self):
        return BuyerVerificationRequest.objects.filter(user=self.request.user).first()

    def get_user_company(self):
        try:
            return self.request.user.company
        except ObjectDoesNotExist:
            return None

    def get_account_context(self):
        return {
            "seller_request": self.get_seller_request(),
            "buyer_request": self.get_buyer_request(),
            "user_company": self.get_user_company(),
        }


class SignupView(RedirectToNextMixin, FormView):
    template_name = "accounts/signup.html"
    form_class = SignupForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        auth_login(self.request, user)
        messages.success(self.request, "Account created and you are now signed in.")
        return redirect(self.get_success_url())


class LoginView(RedirectToNextMixin, FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        messages.success(self.request, "Signed in successfully.")
        return redirect(self.get_success_url())


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        auth_logout(request)
        messages.success(request, "Signed out successfully.")
        return redirect("core:home")

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, AccountContextMixin, TemplateView):
    template_name = "accounts/dashboard.html"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, **kwargs):
        from inquiries.models import Inquiry
        from rfqs.models import RFQ
        from stocklots.models import Favorite, Stocklot

        context = super().get_context_data(**kwargs)
        context.update(self.get_account_context())
        user_company = context.get("user_company")

        active_listings_qs = (
            user_company.stocklots.filter(status=Stocklot.Status.APPROVED, is_active=True) if user_company else []
        )
        sent_inquiries_qs = self.request.user.sent_inquiries.exclude(status=Inquiry.Status.CLOSED)
        received_inquiries_qs = (
            user_company.received_inquiries.exclude(status=Inquiry.Status.CLOSED) if user_company else []
        )
        my_rfqs_qs = self.request.user.rfqs.exclude(status=RFQ.Status.CLOSED)

        context["dashboard_metrics"] = {
            "active_listings": active_listings_qs.count() if user_company else 0,
            "saved_items": self.request.user.favorites.count(),
            "open_inquiries": sent_inquiries_qs.count() + (received_inquiries_qs.count() if user_company else 0),
            "rfqs": my_rfqs_qs.count(),
        }
        context["dashboard_recent_activity"] = sorted(
            [
                *(
                    {
                        "kind": "Listing",
                        "title": stocklot.title,
                        "meta": stocklot.get_status_display(),
                        "timestamp": stocklot.updated_at,
                        "url": reverse("stocklots:edit", args=[stocklot.slug]),
                    }
                    for stocklot in (user_company.stocklots.all()[:3] if user_company else [])
                ),
                *(
                    {
                        "kind": "Saved",
                        "title": favorite.stocklot.title,
                        "meta": "Saved for review",
                        "timestamp": favorite.created_at,
                        "url": reverse("stocklots:detail", args=[favorite.stocklot.slug]),
                    }
                    for favorite in Favorite.objects.select_related("stocklot").filter(user=self.request.user)[:3]
                ),
                *(
                    {
                        "kind": "Inquiry",
                        "title": inquiry.display_subject,
                        "meta": inquiry.get_status_display(),
                        "timestamp": inquiry.updated_at,
                        "url": reverse("inquiries:detail", args=[inquiry.pk]),
                    }
                    for inquiry in list(self.request.user.sent_inquiries.select_related("stocklot")[:3])
                ),
                *(
                    {
                        "kind": "RFQ",
                        "title": rfq.title,
                        "meta": rfq.get_status_display(),
                        "timestamp": rfq.updated_at,
                        "url": reverse("rfqs:detail", args=[rfq.pk]),
                    }
                    for rfq in self.request.user.rfqs.select_related("category")[:3]
                ),
            ],
            key=lambda item: item["timestamp"],
            reverse=True,
        )[:6]
        return context


class SettingsView(LoginRequiredMixin, AccountContextMixin, UpdateView):
    form_class = AccountSettingsForm
    template_name = "accounts/settings.html"
    success_url = reverse_lazy("accounts:settings")
    login_url = reverse_lazy("accounts:login")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_account_context())
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account details updated.")
        return response


class SellerVerificationRequestView(LoginRequiredMixin, AccountContextMixin, FormView):
    template_name = "accounts/seller_verification_request.html"
    form_class = SellerVerificationRequestForm
    success_url = reverse_lazy("accounts:seller_request")
    login_url = reverse_lazy("accounts:login")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.get_seller_request()
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial.setdefault("contact_person_name", self.request.user.full_name)
        initial.setdefault("company_email", self.request.user.email)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_account_context())
        return context

    def form_valid(self, form):
        seller_request = self.get_seller_request()
        if self.request.user.is_seller or (
            seller_request and seller_request.status == SellerVerificationRequest.Status.APPROVED
        ):
            messages.info(self.request, "You are already approved as a seller.")
            return redirect(self.success_url)

        seller_request = form.save(commit=False)
        seller_request.user = self.request.user
        seller_request.status = SellerVerificationRequest.Status.PENDING
        seller_request.review_notes = ""
        seller_request.save()

        messages.success(
            self.request,
            "Seller verification request submitted. We will review it and notify you.",
        )
        return redirect(self.success_url)


class BuyerVerificationRequestView(LoginRequiredMixin, AccountContextMixin, FormView):
    template_name = "accounts/buyer_verification_request.html"
    form_class = BuyerVerificationRequestForm
    success_url = reverse_lazy("accounts:buyer_verification")
    login_url = reverse_lazy("accounts:login")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.get_buyer_request()
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial.setdefault("legal_full_name", self.request.user.full_name)
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_account_context())
        return context

    def form_valid(self, form):
        buyer_request = self.get_buyer_request()
        if buyer_request and buyer_request.status == BuyerVerificationRequest.Status.VERIFIED:
            messages.info(self.request, "You are already verified as a buyer.")
            return redirect(self.success_url)

        buyer_request = form.save(commit=False)
        buyer_request.user = self.request.user
        buyer_request.status = BuyerVerificationRequest.Status.PENDING
        buyer_request.review_notes = ""
        buyer_request.save()

        messages.success(
            self.request,
            "Buyer verification request submitted. We will review it and update you.",
        )
        return redirect(self.success_url)


class AccountPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/password_change_form.html"
    form_class = AccountPasswordChangeForm
    success_url = reverse_lazy("accounts:password_change_done")
    login_url = reverse_lazy("accounts:login")


class AccountPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"
    login_url = reverse_lazy("accounts:login")


class AccountPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset_form.html"
    email_template_name = "accounts/emails/password_reset_email.txt"
    subject_template_name = "accounts/emails/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")
    form_class = AccountPasswordResetForm


class AccountPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class AccountPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")
    form_class = AccountSetPasswordForm


class AccountPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
