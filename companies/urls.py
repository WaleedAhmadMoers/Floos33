from django.urls import path

from .views import CompanyCreateView, CompanyEditView, CompanyProfileView

app_name = "companies"

urlpatterns = [
    path("company/create/", CompanyCreateView.as_view(), name="create"),
    path("company/profile/", CompanyProfileView.as_view(), name="profile"),
    path("company/edit/", CompanyEditView.as_view(), name="edit"),
]
