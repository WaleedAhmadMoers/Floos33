from django import forms

from .models import InquiryReply


class InquiryReplyForm(forms.ModelForm):
    class Meta:
        model = InquiryReply
        fields = ["message", "attachment"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": (
                        "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
                        "shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
                    ),
                    "rows": 4,
                    "placeholder": "Write your reply...",
                }
            ),
            "attachment": forms.ClearableFileInput(
                attrs={
                    "class": (
                        "block w-full rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 "
                        "text-sm text-slate-600 file:mr-4 file:rounded-xl file:border-0 file:bg-slate-900 "
                        "file:px-4 file:py-2 file:text-sm file:font-bold file:text-white hover:file:bg-slate-800"
                    )
                }
            ),
        }
        labels = {"message": "Reply"}
