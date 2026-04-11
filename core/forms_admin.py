from django import forms

from accounts.models import User
from companies.models import Company
from core.languages import translation_field_names
from core.models import DealTrigger
from stocklots.models import Stocklot
from rfqs.models import RFQ
from inquiries.models import Inquiry, InquiryReply
from rfqs.models import RFQMessage


class BaseAdminStyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = (
            "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 "
            "shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
        )
        checkbox_class = "h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-200"

        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "").strip()
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = " ".join(part for part in [existing, checkbox_class] if part).strip()
            else:
                field.widget.attrs["class"] = " ".join(part for part in [existing, base_class] if part).strip()


class AdminUserForm(BaseAdminStyledForm):
    class Meta:
        model = User
        fields = [
            "email",
            "full_name",
            "is_verified_user",
            "verified_user_note",
            "is_buyer",
            "is_seller",
            "is_active",
            "identity_status",
        ]


class AdminCompanyForm(BaseAdminStyledForm):
    class Meta:
        model = Company
        fields = [
            "name",
            "owner",
            "description",
            "phone",
            "email",
            "country",
            "city",
            "address",
            "website",
            "registration_number",
            "vat_number",
            "identity_status",
        ]


class AdminDealForm(BaseAdminStyledForm):
    class Meta:
        model = DealTrigger
        fields = [
            "deal_type",
            "inquiry",
            "rfq_conversation",
            "buyer",
            "seller_user",
            "seller_company",
            "buyer_accepted",
            "seller_accepted",
            "status",
            "progress_status",
        ]


class AdminStocklotForm(BaseAdminStyledForm):
    class Meta:
        model = Stocklot
        fields = [
            "original_language",
            "title",
            "description",
            "company",
            "category",
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
            "is_admin_verified",
            *translation_field_names(),
        ]


class AdminRFQForm(BaseAdminStyledForm):
    class Meta:
        model = RFQ
        fields = [
            "buyer",
            "original_language",
            "title",
            "description",
            "category",
            "quantity",
            "unit_type",
            "target_price",
            "currency",
            "location_country",
            "location_city",
            "moderation_status",
            "status",
            *translation_field_names(),
        ]


class AdminInquiryForm(BaseAdminStyledForm):
    class Meta:
        model = Inquiry
        fields = [
            "stocklot",
            "buyer",
            "seller_company",
            "subject",
            "message",
            "status",
            "moderation_status",
        ]


class AdminInquiryReplyForm(BaseAdminStyledForm):
    class Meta:
        model = InquiryReply
        fields = [
            "inquiry",
            "sender_user",
            "sender_company",
            "message",
            "moderation_status",
        ]


class AdminRFQMessageForm(BaseAdminStyledForm):
    class Meta:
        model = RFQMessage
        fields = [
            "conversation",
            "sender_user",
            "sender_company",
            "message",
            "price",
            "currency",
            "moderation_status",
        ]
