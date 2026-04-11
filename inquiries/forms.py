from django import forms

from .models import Inquiry


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": (
                        "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
                        "shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
                    ),
                    "placeholder": "Optional subject",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": (
                        "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
                        "shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
                    ),
                    "rows": 5,
                    "placeholder": "Write a clear, concise message about the stocklot.",
                }
            ),
        }
        labels = {
            "subject": "Subject (optional)",
            "message": "Message",
        }
