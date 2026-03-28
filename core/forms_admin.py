from django import forms

from accounts.models import User
from companies.models import Company
from core.models import DealTrigger
from stocklots.models import Stocklot
from rfqs.models import RFQ
from inquiries.models import Inquiry, InquiryReply
from rfqs.models import RFQMessage


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "email",
            "full_name",
            "is_buyer",
            "is_seller",
            "is_active",
            "identity_status",
        ]


class AdminCompanyForm(forms.ModelForm):
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


class AdminDealForm(forms.ModelForm):
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


class AdminStocklotForm(forms.ModelForm):
    class Meta:
        model = Stocklot
        fields = [
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
        ]


class AdminRFQForm(forms.ModelForm):
    class Meta:
        model = RFQ
        fields = [
            "buyer",
            "title",
            "description",
            "category",
            "quantity",
            "unit_type",
            "target_price",
            "currency",
            "location_country",
            "location_city",
            "status",
        ]


class AdminInquiryForm(forms.ModelForm):
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


class AdminInquiryReplyForm(forms.ModelForm):
    class Meta:
        model = InquiryReply
        fields = [
            "inquiry",
            "sender_user",
            "sender_company",
            "message",
            "moderation_status",
        ]


class AdminRFQMessageForm(forms.ModelForm):
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
