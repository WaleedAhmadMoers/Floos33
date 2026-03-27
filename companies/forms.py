from django import forms

from .models import Company


class BaseStyledFormMixin:
    def _apply_widget_classes(self):
        for field in self.fields.values():
            existing_class = field.widget.attrs.get("class", "")
            classes = " ".join(part for part in [existing_class, "form-input"] if part).strip()
            field.widget.attrs["class"] = classes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_widget_classes()


class CompanyForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = Company
        fields = (
            "name",
            "legal_name",
            "description",
            "phone",
            "email",
            "country",
            "city",
            "address",
            "website",
            "registration_number",
            "vat_number",
        )
        labels = {
            "name": "اسم الشركة",
            "legal_name": "الاسم القانوني",
            "description": "وصف مختصر للشركة",
            "phone": "رقم الهاتف",
            "email": "البريد الإلكتروني التجاري",
            "country": "الدولة",
            "city": "المدينة",
            "address": "العنوان",
            "website": "الموقع الإلكتروني",
            "registration_number": "رقم السجل التجاري",
            "vat_number": "الرقم الضريبي أو VAT",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        cleaned_data = super().clean()
        for field_name in (
            "name",
            "legal_name",
            "description",
            "phone",
            "country",
            "city",
            "address",
            "registration_number",
            "vat_number",
        ):
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()

        website = cleaned_data.get("website")
        if isinstance(website, str):
            cleaned_data["website"] = website.strip()

        return cleaned_data
