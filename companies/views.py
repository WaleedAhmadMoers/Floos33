from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from .forms import CompanyForm
from .models import Company


class CompanyContextMixin(LoginRequiredMixin):
    login_url = reverse_lazy("accounts:login")

    def get_company(self):
        try:
            return self.request.user.company
        except ObjectDoesNotExist:
            return None


class CompanyCreateView(CompanyContextMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_form.html"
    success_url = reverse_lazy("companies:profile")

    def dispatch(self, request, *args, **kwargs):
        if self.get_company() is not None:
            messages.info(request, "A company profile already exists for this account.")
            return redirect("companies:profile")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_mode": "create",
                "page_title": "Create company",
                "page_intro": "Add accurate company details to unlock marketplace capabilities.",
                "submit_label": "Save company",
            }
        )
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        messages.success(self.request, "Company created and saved.")
        return redirect(self.get_success_url())


class CompanyRequiredMixin(CompanyContextMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.get_company() is None:
            messages.info(request, "Create a company profile before accessing this page.")
            return redirect("companies:create")
        return super().dispatch(request, *args, **kwargs)


class CompanyProfileView(CompanyRequiredMixin, DetailView):
    model = Company
    template_name = "companies/company_profile.html"
    context_object_name = "company"

    def get_object(self, queryset=None):
        return self.get_company()


class CompanyEditView(CompanyRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/company_form.html"
    success_url = reverse_lazy("companies:profile")

    def get_object(self, queryset=None):
        return self.get_company()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "page_mode": "edit",
                "page_title": "Edit company",
                "page_intro": "Keep company information current to build trust with buyers.",
                "submit_label": "Save changes",
            }
        )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Company details updated.")
        return response
