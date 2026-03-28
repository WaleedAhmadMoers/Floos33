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


class ConversationStartForm(forms.ModelForm):
    class Meta:
        model = RFQMessage
        fields = ["price", "currency", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].required = False


class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = RFQMessage
        fields = ["message", "price"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].required = False
