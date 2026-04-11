from django import forms

from core.models import SupportMessage


FIELD_CLASS = (
    "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm "
    "text-slate-900 shadow-sm outline-none transition focus:border-brand-500 "
    "focus:ring-2 focus:ring-brand-100"
)


class SupportContactForm(forms.ModelForm):
    class Meta:
        model = SupportMessage
        fields = ("name", "email", "phone", "subject", "message")
        widgets = {
            "name": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "email": forms.EmailInput(attrs={"class": FIELD_CLASS, "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"class": FIELD_CLASS, "autocomplete": "tel"}),
            "subject": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "message": forms.Textarea(attrs={"class": f"min-h-[180px] {FIELD_CLASS}"}),
        }

    def __init__(self, *args, cms_text=None, **kwargs):
        super().__init__(*args, **kwargs)
        cms_text = cms_text or (lambda key, default="": default)

        field_config = {
            "name": {
                "label": cms_text("shared.name_label", "Name"),
                "placeholder": cms_text("contact.form_name_placeholder", "Your name"),
            },
            "email": {
                "label": cms_text("shared.email_label", "Email"),
                "placeholder": cms_text("contact.form_email_placeholder", "you@company.com"),
            },
            "phone": {
                "label": cms_text("contact.form_phone_label", "Phone"),
                "placeholder": cms_text("contact.form_phone_placeholder", "+49 1575 4967414"),
            },
            "subject": {
                "label": cms_text("shared.subject_label", "Subject"),
                "placeholder": cms_text("contact.form_subject_placeholder", "How can we help?"),
            },
            "message": {
                "label": cms_text("shared.message_label", "Message"),
                "placeholder": cms_text("contact.form_message_placeholder", "Tell us what you need and we will get back to you."),
            },
        }

        for field_name, config in field_config.items():
            self.fields[field_name].label = config["label"]
            self.fields[field_name].widget.attrs["placeholder"] = config["placeholder"]

        self.fields["phone"].required = False
        self.fields["subject"].required = False
