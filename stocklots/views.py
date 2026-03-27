from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import StocklotForm
from .models import Category, Stocklot


class MarketplaceListView(ListView):
    model = Stocklot
    template_name = "stocklots/marketplace_list.html"
    context_object_name = "stocklots"
    paginate_by = 12

    def get_selected_category(self):
        slug = self.request.GET.get("category", "").strip()
        if not slug:
            return None
        return Category.objects.filter(slug=slug, is_active=True).first()

    def get_queryset(self):
        queryset = (
            Stocklot.objects.select_related("company", "category", "category__parent")
            .filter(status=Stocklot.Status.PUBLISHED, is_active=True)
            .order_by("-created_at")
        )

        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        selected_category = self.get_selected_category()
        if selected_category:
            category_ids = [selected_category.id, *selected_category.get_descendant_ids()]
            queryset = queryset.filter(category_id__in=category_ids)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["marketplace_categories"] = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related(
            "children"
        )
        context["selected_category"] = self.get_selected_category()
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class StocklotDetailView(DetailView):
    model = Stocklot
    template_name = "stocklots/stocklot_detail.html"
    context_object_name = "stocklot"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        queryset = Stocklot.objects.select_related("company", "category", "category__parent")
        if self.request.user.is_authenticated:
            try:
                company = self.request.user.company
            except ObjectDoesNotExist:
                company = None

            if company and self.request.user.is_seller:
                return queryset.filter(Q(status=Stocklot.Status.PUBLISHED, is_active=True) | Q(company=company))

        return queryset.filter(status=Stocklot.Status.PUBLISHED, is_active=True)


class SellerCompanyRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("accounts:login")

    def get_user_company(self):
        try:
            return self.request.user.company
        except ObjectDoesNotExist:
            return None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_seller:
            messages.info(request, "يجب أن تتم الموافقة عليك كبائع أولاً قبل إدارة الستوكات.")
            return redirect("accounts:seller_request")

        if self.get_user_company() is None:
            messages.info(request, "يجب إنشاء ملف الشركة أولاً قبل إنشاء أو إدارة الستوكات.")
            return redirect("companies:create")

        return super().dispatch(request, *args, **kwargs)


class StocklotManagementContextMixin(SellerCompanyRequiredMixin):
    def get_management_context(self):
        company = self.get_user_company()
        return {
            "user_company": company,
            "my_stocklots_count": company.stocklots.count() if company else 0,
        }


class StocklotCreateView(StocklotManagementContextMixin, CreateView):
    model = Stocklot
    form_class = StocklotForm
    template_name = "stocklots/stocklot_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_management_context())
        context.update(
            {
                "page_title": "إضافة ستوك جديد",
                "page_intro": "أنشئ عرض ستوك جديد مرتبطاً بشركتك مباشرة، مع بيانات أساسية نظيفة وسهلة التطوير لاحقاً.",
                "submit_label": "حفظ الستوك",
            }
        )
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.company = self.get_user_company()
        self.object.save()
        messages.success(self.request, "تم حفظ الستوك بنجاح.")
        return redirect("stocklots:mine")


class MyStocklotListView(StocklotManagementContextMixin, ListView):
    model = Stocklot
    template_name = "stocklots/my_stocklots.html"
    context_object_name = "stocklots"

    def get_queryset(self):
        return (
            Stocklot.objects.select_related("company", "category", "category__parent")
            .filter(company=self.get_user_company())
            .order_by("-updated_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_management_context())
        return context


class StocklotUpdateView(StocklotManagementContextMixin, UpdateView):
    model = Stocklot
    form_class = StocklotForm
    template_name = "stocklots/stocklot_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("stocklots:mine")

    def get_queryset(self):
        return Stocklot.objects.select_related("company", "category").filter(company=self.get_user_company())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_management_context())
        context.update(
            {
                "page_title": "تعديل الستوك",
                "page_intro": "حدّث بيانات الستوك الحالي مع الحفاظ على ملكيته داخل الشركة فقط.",
                "submit_label": "حفظ التعديلات",
            }
        )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "تم تحديث بيانات الستوك بنجاح.")
        return response
