from django import forms

from stocklots.models import Category, Stocklot
from rfqs.models import RFQ, RFQConversation, RFQMessage


class RFQForm(forms.ModelForm):
    class Meta:
        model = RFQ
        fields = [
            "title",
            "description",
            "category",
            "quantity",
            "unit_type",
            "target_price",
            "currency",
            "location_country",
            "location_city",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()
        self._apply_ui()

    def _apply_ui(self):
        base_class = (
            "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
            "shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
        )
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {base_class}".strip()


class ConversationStartForm(forms.ModelForm):
    class Meta:
        model = RFQMessage
        fields = ["price", "currency", "message", "attachment"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
            "attachment": forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].required = False
        self._apply_ui()

    def _apply_ui(self):
        base_class = (
            "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
            "shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
        )
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {base_class}".strip()
            if name == "message":
                field.widget.attrs["class"] += " min-h-32"


class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = RFQMessage
        fields = ["message", "price", "attachment"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 3}),
            "attachment": forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].required = False
        self._apply_ui()

    def _apply_ui(self):
        base_class = (
            "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
            "shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
        )
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {base_class}".strip()
            if name == "message":
                field.widget.attrs["class"] += " min-h-28"
