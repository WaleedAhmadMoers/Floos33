from django import forms

from .models import Company


class BaseStyledFormMixin:
    def _apply_widget_classes(self):
        base_class = (
            "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
            "shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
        )
        checkbox_class = "h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-200"
        file_class = (
            "block w-full rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 "
            "text-sm text-slate-600 file:mr-4 file:rounded-xl file:border-0 file:bg-slate-900 "
            "file:px-4 file:py-2 file:text-sm file:font-bold file:text-white hover:file:bg-slate-800"
        )

        for field in self.fields.values():
            existing_class = field.widget.attrs.get("class", "").strip()
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = " ".join(part for part in [existing_class, checkbox_class] if part).strip()
                continue

            if isinstance(widget, forms.ClearableFileInput):
                widget.attrs["class"] = " ".join(part for part in [existing_class, file_class] if part).strip()
                continue

            widget.attrs["class"] = " ".join(part for part in [existing_class, base_class] if part).strip()

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
            "name": "Company name",
            "legal_name": "Legal name",
            "description": "Description",
            "phone": "Phone",
            "email": "Email",
            "country": "Country",
            "city": "City",
            "address": "Address",
            "website": "Website",
            "registration_number": "Registration number",
            "vat_number": "VAT number",
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
