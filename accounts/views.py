from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView
from django.contrib.auth.views import PasswordResetCompleteView, PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView

from core.cms import get_cms_map, get_cms_text
from core.context_processors import resolve_site_language

from .forms import AccountPasswordChangeForm, AccountPasswordResetForm, AccountSetPasswordForm
from .forms import AccountSettingsForm, BuyerVerificationRequestForm, LoginForm
from .forms import SellerVerificationRequestForm, SignupForm
from .models import BuyerVerificationRequest, SellerVerificationRequest, User
from .services import app_uses_https, get_app_domain, send_verification_email


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
        send_verification_email(user)
        self.request.session["pending_verification_email"] = user.email
        messages.success(
            self.request,
            "Account created. Please check your email and activate your account before logging in.",
        )
        return redirect("accounts:verification_sent")


class VerificationSentView(TemplateView):
    template_name = "accounts/verification_sent.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_verification_email"] = self.request.session.get("pending_verification_email", "")
        return context


class VerifyEmailView(View):
    def get(self, request, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(kwargs["uidb64"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, kwargs["token"]):
            messages.error(request, "This verification link is invalid or has expired.")
            return redirect("accounts:verification_invalid")

        updates = []
        if not user.email_verified:
            user.email_verified = True
            updates.append("email_verified")
        if not user.is_active:
            user.is_active = True
            updates.append("is_active")
        if updates:
            user.save(update_fields=updates)

        request.session.pop("pending_verification_email", None)
        messages.success(request, "Your email has been verified. You can now log in.")
        return redirect("accounts:verification_success")


class VerificationSuccessView(TemplateView):
    template_name = "accounts/verification_success.html"


class VerificationInvalidView(TemplateView):
    template_name = "accounts/verification_invalid.html"


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
        from core.models import Notification
        from inquiries.models import Inquiry
        from rfqs.models import RFQ, RFQConversation
        from stocklots.models import Favorite, Stocklot

        context = super().get_context_data(**kwargs)
        context.update(self.get_account_context())
        language_code = resolve_site_language(self.request)
        cms_blocks = get_cms_map(language_code)
        t = lambda key: get_cms_text(key, language_code, cms_blocks)
        user_company = context.get("user_company")
        buyer_request = context.get("buyer_request")
        seller_request = context.get("seller_request")

        company_stocklots_qs = user_company.stocklots.all() if user_company else Stocklot.objects.none()
        active_listings_qs = company_stocklots_qs.filter(status=Stocklot.Status.APPROVED, is_active=True)
        pending_listings_qs = company_stocklots_qs.filter(status=Stocklot.Status.PENDING_REVIEW)
        sent_inquiries_qs = self.request.user.sent_inquiries.select_related("stocklot").exclude(status=Inquiry.Status.CLOSED)
        received_inquiries_qs = (
            user_company.received_inquiries.select_related("stocklot", "buyer").exclude(status=Inquiry.Status.CLOSED)
            if user_company
            else Inquiry.objects.none()
        )
        my_rfqs_qs = self.request.user.rfqs.select_related("category")
        open_rfqs_qs = my_rfqs_qs.exclude(status=RFQ.Status.CLOSED)
        pending_rfqs_qs = open_rfqs_qs.filter(moderation_status=RFQ.ModerationStatus.PENDING_REVIEW)
        saved_listings_qs = Favorite.objects.select_related("stocklot").filter(
            user=self.request.user,
            stocklot__status=Stocklot.Status.APPROVED,
            stocklot__is_active=True,
        )
        saved_rfqs_qs = self.request.user.saved_rfqs.select_related("rfq")
        buyer_conversations_qs = RFQConversation.objects.filter(buyer=self.request.user)
        seller_conversations_qs = RFQConversation.objects.filter(seller_user=self.request.user)

        total_listings = company_stocklots_qs.count()
        active_listings = active_listings_qs.count()
        pending_listings = pending_listings_qs.count()
        saved_items = saved_listings_qs.count() + saved_rfqs_qs.count()
        sent_inquiries = sent_inquiries_qs.count()
        received_inquiries = received_inquiries_qs.count()
        open_inquiries = sent_inquiries + received_inquiries
        total_rfqs = my_rfqs_qs.count()
        open_rfqs = open_rfqs_qs.count()
        pending_rfqs = pending_rfqs_qs.count()
        buyer_conversations = buyer_conversations_qs.count()
        seller_conversations = seller_conversations_qs.count()
        open_threads = open_inquiries + buyer_conversations + seller_conversations
        unread_notifications = Notification.objects.filter(recipient=self.request.user, is_read=False).count()

        context["dashboard_metrics"] = {
            "active_listings": active_listings,
            "total_listings": total_listings,
            "pending_listings": pending_listings,
            "saved_items": saved_items,
            "open_inquiries": open_inquiries,
            "open_threads": open_threads,
            "rfqs": open_rfqs,
            "total_rfqs": total_rfqs,
            "pending_rfqs": pending_rfqs,
            "buyer_conversations": buyer_conversations,
            "seller_conversations": seller_conversations,
            "notifications": unread_notifications,
        }

        if self.request.user.is_seller:
            messages_url = reverse("inquiries:received")
        elif buyer_conversations:
            messages_url = reverse("rfqs:buyer_conversations")
        elif seller_conversations:
            messages_url = reverse("rfqs:seller_conversations")
        else:
            messages_url = reverse("inquiries:sent")
        context["dashboard_messages_url"] = messages_url
        context["dashboard_saved_items_url"] = reverse("core:saved")
        context["dashboard_company_url"] = (
            reverse("companies:profile") if user_company else reverse("companies:create")
        )

        profile_is_complete = bool(self.request.user.full_name and self.request.user.email_verified)
        company_is_complete = bool(
            user_company
            and user_company.name
            and user_company.description
            and user_company.email
            and user_company.phone
            and user_company.country
        )
        context["profile_is_complete"] = profile_is_complete
        context["company_is_complete"] = company_is_complete

        dashboard_attention = []
        if pending_listings:
            dashboard_attention.append(
                {
                    "title": t("dashboard.attention_listings_title"),
                    "value": pending_listings,
                    "body": t("dashboard.attention_listings_body"),
                    "url": reverse("stocklots:mine"),
                    "action_label": t("dashboard.attention_listings_action"),
                }
            )
        if pending_rfqs:
            dashboard_attention.append(
                {
                    "title": t("dashboard.attention_rfqs_title"),
                    "value": pending_rfqs,
                    "body": t("dashboard.attention_rfqs_body"),
                    "url": reverse("rfqs:my_rfqs"),
                    "action_label": t("dashboard.attention_rfqs_action"),
                }
            )
        if unread_notifications:
            dashboard_attention.append(
                {
                    "title": t("dashboard.attention_notifications_title"),
                    "value": unread_notifications,
                    "body": t("dashboard.attention_notifications_body"),
                    "url": reverse("core:notifications"),
                    "action_label": t("dashboard.attention_notifications_action"),
                }
            )
        if open_threads:
            dashboard_attention.append(
                {
                    "title": t("dashboard.attention_threads_title"),
                    "value": open_threads,
                    "body": t("dashboard.attention_threads_body"),
                    "url": messages_url,
                    "action_label": t("dashboard.attention_threads_action"),
                }
            )
        context["dashboard_attention"] = dashboard_attention[:4]

        dashboard_next_steps = []
        if not profile_is_complete:
            dashboard_next_steps.append(
                {
                    "title": t("dashboard.next_profile_title"),
                    "body": t("dashboard.next_profile_body"),
                    "url": reverse("accounts:settings"),
                    "action_label": t("dashboard.next_profile_action"),
                }
            )
        if not user_company:
            dashboard_next_steps.append(
                {
                    "title": t("dashboard.next_company_title"),
                    "body": t("dashboard.next_company_body"),
                    "url": reverse("companies:create"),
                    "action_label": t("dashboard.next_company_action"),
                }
            )
        if buyer_request is None or buyer_request.status in {
            BuyerVerificationRequest.Status.UNVERIFIED,
            BuyerVerificationRequest.Status.REJECTED,
        }:
            dashboard_next_steps.append(
                {
                    "title": t("dashboard.next_buyer_verification_title"),
                    "body": t("dashboard.next_buyer_verification_body"),
                    "url": reverse("accounts:buyer_verification"),
                    "action_label": t("dashboard.next_buyer_verification_action"),
                }
            )
        if not self.request.user.is_seller and not seller_request:
            dashboard_next_steps.append(
                {
                    "title": t("dashboard.next_seller_access_title"),
                    "body": t("dashboard.next_seller_access_body"),
                    "url": reverse("accounts:seller_request"),
                    "action_label": t("dashboard.next_seller_access_action"),
                }
            )
        elif seller_request and seller_request.status == SellerVerificationRequest.Status.REJECTED:
            dashboard_next_steps.append(
                {
                    "title": t("dashboard.next_seller_review_title"),
                    "body": t("dashboard.next_seller_review_body"),
                    "url": reverse("accounts:seller_request"),
                    "action_label": t("dashboard.next_seller_review_action"),
                }
            )
        if self.request.user.is_seller and total_listings == 0:
            dashboard_next_steps.append(
                {
                    "title": t("dashboard.next_first_listing_title"),
                    "body": t("dashboard.next_first_listing_body"),
                    "url": reverse("stocklots:create"),
                    "action_label": t("dashboard.next_first_listing_action"),
                }
            )
        if total_rfqs == 0:
            dashboard_next_steps.append(
                {
                    "title": t("dashboard.next_first_rfq_title"),
                    "body": t("dashboard.next_first_rfq_body"),
                    "url": reverse("rfqs:create"),
                    "action_label": t("dashboard.next_first_rfq_action"),
                }
            )
        if saved_items == 0:
            dashboard_next_steps.append(
                {
                    "title": t("dashboard.next_saved_title"),
                    "body": t("dashboard.next_saved_body"),
                    "url": reverse("stocklots:list"),
                    "action_label": t("dashboard.next_saved_action"),
                }
            )
        context["dashboard_spotlight_step"] = dashboard_next_steps[0] if dashboard_next_steps else None
        context["dashboard_secondary_steps"] = dashboard_next_steps[1:5]
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
        email_changed = "email" in form.changed_data
        response = super().form_valid(form)

        if email_changed:
            self.object.email_verified = False
            self.object.is_active = False
            self.object.save(update_fields=["email_verified", "is_active"])
            send_verification_email(self.object)
            auth_logout(self.request)
            self.request.session["pending_verification_email"] = self.object.email
            messages.info(
                self.request,
                "Your email address changed. Please verify the new address before logging in again.",
            )
            return redirect("accounts:verification_sent")

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

    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed.")
        return super().form_valid(form)


class AccountPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "accounts/password_change_done.html"
    login_url = reverse_lazy("accounts:login")


class AccountPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset_form.html"
    email_template_name = "accounts/emails/password_reset_email.txt"
    subject_template_name = "accounts/emails/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")
    form_class = AccountPasswordResetForm

    def form_valid(self, form):
        form.save(
            use_https=app_uses_https(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            email_template_name=self.email_template_name,
            subject_template_name=self.subject_template_name,
            request=self.request,
            domain_override=get_app_domain(),
            extra_email_context={"site_name": settings.SITE_NAME},
        )
        return FormView.form_valid(self, form)


class AccountPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class AccountPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")
    form_class = AccountSetPasswordForm


class AccountPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
