from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm, ReadOnlyPasswordHashField, SetPasswordForm

from .models import BuyerVerificationRequest, SellerVerificationRequest, User


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


class AdminUserCreationForm(BaseStyledFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("email", "full_name", "preferred_language", "email_verified")

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
        password_validation.validate_password(password2, self.instance)
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.full_name = (self.cleaned_data.get("full_name") or "").strip()
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
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("email",)
        labels = {"email": "Email address"}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                self.add_error("password2", "Passwords do not match.")
            else:
                try:
                    password_validation.validate_password(password2, self.instance)
                except forms.ValidationError as error:
                    self.add_error("password1", error)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.full_name = ""
        user.email_verified = False
        user.is_active = False
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

        if not email or not password:
            return cleaned_data

        user = User.objects.filter(email__iexact=email).first()
        if user and user.check_password(password):
            if not user.email_verified:
                raise forms.ValidationError(
                    "Please verify your email before logging in. Check your inbox for the activation link."
                )
            if not user.is_active:
                raise forms.ValidationError("This account is inactive. Please contact support if you need help.")

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
        full_name = (self.cleaned_data["full_name"] or "").strip()
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
