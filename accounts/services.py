from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def get_app_base_url():
    return settings.APP_BASE_URL.rstrip("/")


def get_app_domain():
    return urlsplit(get_app_base_url()).netloc


def app_uses_https():
    return urlsplit(get_app_base_url()).scheme == "https"


def build_app_url(path):
    return f"{get_app_base_url()}{path}"


def build_email_verification_url(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    path = reverse("accounts:verify_email", kwargs={"uidb64": uid, "token": token})
    return build_app_url(path)


def send_verification_email(user):
    context = {
        "user": user,
        "site_name": settings.SITE_NAME,
        "activation_url": build_email_verification_url(user),
    }
    subject = render_to_string("accounts/emails/verification_subject.txt", context).strip()
    message = render_to_string("accounts/emails/verification_email.txt", context)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
