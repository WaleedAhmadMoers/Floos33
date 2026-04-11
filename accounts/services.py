from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def get_app_base_url():
    return settings.FRONTEND_BASE_URL.rstrip("/")


def get_app_domain():
    return urlsplit(get_app_base_url()).netloc


def app_uses_https():
    return urlsplit(get_app_base_url()).scheme == "https"


def build_app_url(path):
    return f"{get_app_base_url()}{path}"


def render_email_subject(template_name, context):
    subject = render_to_string(template_name, context)
    return "".join(subject.splitlines()).strip()


def send_templated_email(
    *,
    subject_template,
    text_template,
    html_template,
    context,
    recipient_list,
    from_email=None,
    fail_silently=False,
):
    subject = render_email_subject(subject_template, context)
    text_body = render_to_string(text_template, context)
    html_body = render_to_string(html_template, context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    email.attach_alternative(html_body, "text/html")
    return email.send(fail_silently=fail_silently)


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
        "support_email": settings.SUPPORT_EMAIL,
    }
    return send_templated_email(
        subject_template="accounts/emails/verification_subject.txt",
        text_template="accounts/emails/verification_email.txt",
        html_template="accounts/emails/verification_email.html",
        context=context,
        recipient_list=[user.email],
    )


def send_password_changed_email(user, *, fail_silently=True):
    context = {
        "user": user,
        "site_name": settings.SITE_NAME,
        "support_email": settings.SUPPORT_EMAIL,
        "login_url": build_app_url(reverse("accounts:login")),
    }
    return send_templated_email(
        subject_template="accounts/emails/password_changed_subject.txt",
        text_template="accounts/emails/password_changed_email.txt",
        html_template="accounts/emails/password_changed_email.html",
        context=context,
        recipient_list=[user.email],
        fail_silently=fail_silently,
    )


def send_welcome_email(user, *, fail_silently=True):
    context = {
        "user": user,
        "site_name": settings.SITE_NAME,
        "support_email": settings.SUPPORT_EMAIL,
        "login_url": build_app_url(reverse("accounts:login")),
    }
    return send_templated_email(
        subject_template="accounts/emails/welcome_subject.txt",
        text_template="accounts/emails/welcome_email.txt",
        html_template="accounts/emails/welcome_email.html",
        context=context,
        recipient_list=[user.email],
        fail_silently=fail_silently,
    )
