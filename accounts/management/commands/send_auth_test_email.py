from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.services import send_templated_email


class Command(BaseCommand):
    help = "Send a test authentication email using the configured SMTP backend."

    def add_arguments(self, parser):
        parser.add_argument("--to", required=True, help="Recipient email address.")

    def handle(self, *args, **options):
        recipient = options["to"].strip().lower()
        if not recipient:
            raise CommandError("A recipient email address is required.")

        context = {
            "site_name": settings.SITE_NAME,
            "support_email": settings.SUPPORT_EMAIL,
            "user": type("EmailPreviewUser", (), {"full_name": "", "email": recipient})(),
            "activation_url": f"{settings.FRONTEND_BASE_URL}/verify-email/example/token/",
            "login_url": f"{settings.FRONTEND_BASE_URL}/login/",
        }
        send_templated_email(
            subject_template="accounts/emails/verification_subject.txt",
            text_template="accounts/emails/verification_email.txt",
            html_template="accounts/emails/verification_email.html",
            context=context,
            recipient_list=[recipient],
        )
        self.stdout.write(self.style.SUCCESS(f"Sent test authentication email to {recipient}."))
