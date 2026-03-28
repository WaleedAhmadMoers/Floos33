from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm, ReadOnlyPasswordHashField, SetPasswordForm

from .models import BuyerVerificationRequest, SellerVerificationRequest, User


class BaseStyledFormMixin:
    def _apply_widget_classes(self):
        for field in self.fields.values():
            existing_class = field.widget.attrs.get("class", "")
            classes = " ".join(part for part in [existing_class, "form-input"] if part).strip()
            field.widget.attrs["class"] = classes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_widget_classes()


class AdminUserCreationForm(BaseStyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "full_name", "preferred_language")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_buyer = True
        user.is_seller = False
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class AdminUserChangeForm(BaseStyledFormMixin, forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text="You can change the password using the dedicated form.",
    )

    class Meta:
        model = User
        fields = "__all__"

    def clean_password(self):
        return self.initial["password"]


class SignupForm(BaseStyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("full_name", "email")
        labels = {
            "full_name": "Full name",
            "email": "Email address",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        if not full_name:
            raise forms.ValidationError("Full name is required.")
        return full_name

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_buyer = True
        user.is_seller = False
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(BaseStyledFormMixin, forms.Form):
    email = forms.EmailField(label="Email address")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Invalid email or password.")

        return cleaned_data

    def get_user(self):
        return self.user


class AccountSettingsForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("full_name", "email", "preferred_language")
        labels = {
            "full_name": "Full name",
            "email": "Email address",
            "preferred_language": "Preferred language",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        if not full_name:
            raise forms.ValidationError("Full name is required.")
        return full_name


class SellerVerificationRequestForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = SellerVerificationRequest
        fields = (
            "company_name",
            "contact_person_name",
            "phone_number",
            "company_email",
            "company_address",
            "country",
            "city",
            "business_type",
            "business_description",
            "registration_number",
            "vat_number",
            "supporting_document",
        )
        labels = {
            "company_name": "Company name",
            "contact_person_name": "Contact person name",
            "phone_number": "Phone number",
            "company_email": "Company email",
            "company_address": "Company address",
            "country": "Country",
            "city": "City",
            "business_type": "Business type",
            "business_description": "Business description",
            "registration_number": "Registration number",
            "vat_number": "VAT or tax number",
            "supporting_document": "Supporting document",
        }
        widgets = {
            "business_description": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_company_email(self):
        return self.cleaned_data["company_email"].strip().lower()

    def clean(self):
        cleaned_data = super().clean()
        for field_name in (
            "company_name",
            "contact_person_name",
            "phone_number",
            "company_address",
            "country",
            "city",
            "business_type",
        ):
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()
        return cleaned_data


class BuyerVerificationRequestForm(BaseStyledFormMixin, forms.ModelForm):
    class Meta:
        model = BuyerVerificationRequest
        fields = (
            "legal_full_name",
            "phone_number",
            "country",
            "city",
            "address",
            "identity_document_type",
            "identity_document",
            "selfie_document",
        )
        labels = {
            "legal_full_name": "Legal full name",
            "phone_number": "Phone number",
            "country": "Country",
            "city": "City",
            "address": "Address",
            "identity_document_type": "Identity document type",
            "identity_document": "Identity document",
            "selfie_document": "Selfie or face photo",
        }

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ("legal_full_name", "phone_number", "country", "city", "address"):
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = value.strip()
        return cleaned_data


class AccountPasswordResetForm(BaseStyledFormMixin, PasswordResetForm):
    email = forms.EmailField(label="Email address")


class AccountPasswordChangeForm(BaseStyledFormMixin, DjangoPasswordChangeForm):
    old_password = forms.CharField(label="Current password", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)


class AccountSetPasswordForm(BaseStyledFormMixin, SetPasswordForm):
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput)
