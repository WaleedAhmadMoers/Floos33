from django import forms

from .models import Category, Stocklot


class BaseStyledFormMixin:
    def _apply_widget_classes(self):
        for field in self.fields.values():
            existing_class = field.widget.attrs.get("class", "")
            classes = " ".join(part for part in [existing_class, "form-input"] if part).strip()
            field.widget.attrs["class"] = classes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_widget_classes()


class CategoryChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.full_name


class StocklotForm(BaseStyledFormMixin, forms.ModelForm):
    category = CategoryChoiceField(queryset=Category.objects.none(), label="التصنيف")

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
            "status",
            "is_active",
        )
        labels = {
            "title": "عنوان الستوك",
            "description": "وصف الستوك",
            "condition": "الحالة",
            "quantity": "الكمية",
            "moq": "الحد الأدنى للطلب",
            "unit_type": "نوع الوحدة",
            "price": "السعر",
            "currency": "العملة",
            "location_country": "دولة التواجد",
            "location_city": "مدينة التواجد",
            "status": "الحالة",
            "is_active": "نشط",
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
        self.fields["category"].empty_label = "اختر التصنيف المناسب"

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ("title", "description", "location_country", "location_city"):
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()
        return cleaned_data
