from django import forms


class SupportContactForm(forms.Form):
    name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100",
                "placeholder": "Your name",
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100",
                "placeholder": "you@company.com",
            }
        )
    )
    subject = forms.CharField(
        max_length=180,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100",
                "placeholder": "Subject (optional)",
            }
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "min-h-[180px] w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100",
                "placeholder": "Tell us how we can help.",
            }
        )
    )
