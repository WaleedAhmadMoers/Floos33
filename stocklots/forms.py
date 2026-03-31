from django import forms

from .models import Category, Stocklot


COUNTRY_CHOICES = [
    ("AT", "Austria"),
    ("BE", "Belgium"),
    ("BG", "Bulgaria"),
    ("HR", "Croatia"),
    ("CY", "Cyprus"),
    ("CZ", "Czech Republic"),
    ("DK", "Denmark"),
    ("EE", "Estonia"),
    ("FI", "Finland"),
    ("FR", "France"),
    ("DE", "Germany"),
    ("GR", "Greece"),
    ("HU", "Hungary"),
    ("IE", "Ireland"),
    ("IT", "Italy"),
    ("LV", "Latvia"),
    ("LT", "Lithuania"),
    ("LU", "Luxembourg"),
    ("MT", "Malta"),
    ("NL", "Netherlands"),
    ("PL", "Poland"),
    ("PT", "Portugal"),
    ("RO", "Romania"),
    ("SK", "Slovakia"),
    ("SI", "Slovenia"),
    ("ES", "Spain"),
    ("SE", "Sweden"),
    ("CH", "Switzerland"),
    ("AE", "United Arab Emirates"),
    ("SA", "Saudi Arabia"),
    ("CN", "China"),
    ("UK", "United Kingdom"),
    ("US", "United States"),
]


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


class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.full_name


class StocklotForm(BaseStyledFormMixin, forms.ModelForm):
    category = CategoryChoiceField(queryset=Category.objects.none(), label="Category")
    location_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="Country")

    class Meta:
        model = Stocklot
        fields = (
            "title",
            "category",
            "description",
            "condition",
            "quantity",
            "moq",
            "unit_type",
            "price",
            "currency",
            "location_country",
            "location_city",
            "is_active",
        )
        labels = {
            "title": "Title",
            "description": "Description",
            "condition": "Condition",
            "quantity": "Quantity",
            "moq": "Minimum order quantity",
            "unit_type": "Unit type",
            "price": "Price",
            "currency": "Currency",
            "location_country": "Country",
            "location_city": "City",
            "is_active": "Active",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(is_active=True).select_related("parent").order_by(
            "parent__name",
            "name",
        )
        self.fields["category"].empty_label = "Choose a category"

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ("title", "description", "location_city"):
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()
        return cleaned_data
