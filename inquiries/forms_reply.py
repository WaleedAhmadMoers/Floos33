from django import forms

from .models import InquiryReply


class InquiryReplyForm(forms.ModelForm):
    class Meta:
        model = InquiryReply
        fields = ["message", "attachment"]
        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 4,
                    "placeholder": "Write your reply...",
                }
            ),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-input"}),
        }
        labels = {"message": "Reply"}
