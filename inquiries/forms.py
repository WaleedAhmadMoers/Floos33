from django import forms

from .models import Inquiry


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-input", "placeholder": "Optional subject"}),
            "message": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 5,
                    "placeholder": "Write a clear, concise message about the stocklot.",
                }
            ),
        }
        labels = {
            "subject": "Subject (optional)",
            "message": "Message",
        }
