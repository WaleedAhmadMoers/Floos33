from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal, InvalidOperation

from django.db.models import Q, OuterRef, Exists, Value, BooleanField
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views import View

from .forms import StocklotForm
from .models import Category, Favorite, Stocklot, StocklotDocument, StocklotImage, StocklotVideo
from accounts.models import SellerVerificationRequest
from core.utils.verification import enforce_verified


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
            Stocklot.objects.select_related("company", "category", "category__parent", "company__owner")
            .filter(status=Stocklot.Status.APPROVED, is_active=True)
            .annotate(
                seller_verified=Exists(
                    SellerVerificationRequest.objects.filter(
                        user=OuterRef("company__owner"), status=SellerVerificationRequest.Status.APPROVED
                    )
                )
            )
        )

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(Favorite.objects.filter(user=self.request.user, stocklot=OuterRef("pk")))
            )
        else:
            queryset = queryset.annotate(is_favorited=Value(False, output_field=BooleanField()))

        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        selected_category = self.get_selected_category()
        if selected_category:
            category_ids = [selected_category.id, *selected_category.get_descendant_ids()]
            queryset = queryset.filter(category_id__in=category_ids)

        country = self.request.GET.get("country", "").strip()
        if country:
            queryset = queryset.filter(location_country__iexact=country)

        condition = self.request.GET.get("condition", "").strip()
        if condition:
            queryset = queryset.filter(condition=condition)

        def parse_decimal(name):
            raw = self.request.GET.get(name, "").strip()
            if not raw:
                return None
            try:
                return Decimal(raw)
            except (InvalidOperation, TypeError):
                return None

        price_min = parse_decimal("price_min")
        price_max = parse_decimal("price_max")
        if price_min is not None:
            queryset = queryset.filter(price__gte=price_min)
        if price_max is not None:
            queryset = queryset.filter(price__lte=price_max)

        def parse_int(name):
            raw = self.request.GET.get(name, "").strip()
            try:
                return int(raw)
            except (TypeError, ValueError):
                return None

        qty_min = parse_int("quantity_min")
        qty_max = parse_int("quantity_max")
        if qty_min is not None:
            queryset = queryset.filter(quantity__gte=qty_min)
        if qty_max is not None:
            queryset = queryset.filter(quantity__lte=qty_max)

        sort = self.request.GET.get("sort", "newest")
        ordering_map = {
            "newest": "-created_at",
            "oldest": "created_at",
            "price_low": "price",
            "price_high": "-price",
            "quantity_high": "-quantity",
        }
        queryset = queryset.order_by(ordering_map.get(sort, "-created_at"))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["marketplace_categories"] = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related(
            "children"
        )
        context["selected_category"] = self.get_selected_category()
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_country"] = self.request.GET.get("country", "").strip()
        context["selected_condition"] = self.request.GET.get("condition", "").strip()
        context["price_min"] = self.request.GET.get("price_min", "").strip()
        context["price_max"] = self.request.GET.get("price_max", "").strip()
        context["quantity_min"] = self.request.GET.get("quantity_min", "").strip()
        context["quantity_max"] = self.request.GET.get("quantity_max", "").strip()
        context["sort"] = self.request.GET.get("sort", "newest")
        context["condition_choices"] = Stocklot.Condition.choices
        context["available_countries"] = (
            Stocklot.objects.filter(status=Stocklot.Status.APPROVED, is_active=True)
            .values_list("location_country", flat=True)
            .distinct()
            .order_by("location_country")
        )
        active_filters = []
        if context["selected_category"]:
            active_filters.append({"key": "category", "label": "Category", "value": context["selected_category"].full_name})
        if context["selected_country"]:
            active_filters.append({"key": "country", "label": "Country", "value": context["selected_country"]})
        if context["selected_condition"]:
            active_filters.append(
                {
                    "key": "condition",
                    "label": "Condition",
                    "value": dict(Stocklot.Condition.choices).get(
                        context["selected_condition"], context["selected_condition"]
                    ),
                }
            )
        if context["price_min"] or context["price_max"]:
            active_filters.append(
                {
                    "key": "price",
                    "label": "Price",
                    "value": f"{context['price_min'] or '0'} - {context['price_max'] or 'max'}",
                    "remove_keys": ["price_min", "price_max"],
                }
            )
        if context["quantity_min"] or context["quantity_max"]:
            active_filters.append(
                {
                    "key": "quantity",
                    "label": "Quantity",
                    "value": f"{context['quantity_min'] or '0'} - {context['quantity_max'] or 'max'}",
                    "remove_keys": ["quantity_min", "quantity_max"],
                }
            )
        context["active_filters"] = active_filters
        context["has_filters"] = bool(active_filters or context["search_query"])

        page_obj = context.get("page_obj")
        if page_obj:
            base_qs = self.request.GET.copy()
            base_qs.pop("page", None)
            base_prefix = "?" + base_qs.urlencode()
            if base_prefix != "?" and not base_prefix.endswith("&"):
                base_prefix += "&"
            context["page_prev"] = (
                f"{base_prefix}page={page_obj.previous_page_number()}" if page_obj.has_previous() else None
            )
            context["page_next"] = f"{base_prefix}page={page_obj.next_page_number()}" if page_obj.has_next() else None
        else:
            context["page_prev"] = context["page_next"] = None
        return context


class StocklotDetailView(DetailView):
    model = Stocklot
    template_name = "stocklots/stocklot_detail.html"
    context_object_name = "stocklot"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        queryset = (
            Stocklot.objects.select_related("company", "category", "category__parent")
            .prefetch_related("images", "documents", "videos")
        )
        if self.request.user.is_authenticated:
            try:
                company = self.request.user.company
            except ObjectDoesNotExist:
                company = None

            if company and self.request.user.is_seller:
                return queryset.filter(Q(status=Stocklot.Status.APPROVED, is_active=True) | Q(company=company))

        return queryset.filter(status=Stocklot.Status.APPROVED, is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["is_favorited"] = Favorite.objects.filter(
                user=self.request.user, stocklot=self.object
            ).exists()
        else:
            context["is_favorited"] = False
        if self.request.user.is_authenticated:
            ok_buyer, _ = enforce_verified(self.request, role="buyer")
            context["can_contact"] = ok_buyer
        else:
            context["can_contact"] = False
        # Hot deals / other marketplace items for exploration
        context.setdefault(
            "other_market_stocklots",
            list(
                Stocklot.objects.select_related("company", "category")
                .filter(status=Stocklot.Status.APPROVED, is_active=True)
                .exclude(pk=self.object.pk)
                .order_by("-created_at")[:8]
            ),
        )
        # Precompute document display names (basename only) for clean UI
        docs = []
        for d in self.object.documents.all():
            d.display_name = d.file.name.rsplit("/", 1)[-1] if d.file and d.file.name else "Document"
            docs.append(d)
        context["stocklot_documents"] = docs
        return context


class SellerCompanyRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("accounts:login")

    def get_user_company(self):
        try:
            return self.request.user.company
        except ObjectDoesNotExist:
            return None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_seller:
            messages.info(request, "Please switch to a seller account to list stocklots.")
            return redirect("accounts:seller_request")

        if self.get_user_company() is None:
            messages.info(request, "Create a company profile before posting stocklots.")
            return redirect("companies:create")

        ok, msg = enforce_verified(request, role="seller")
        if not ok:
            messages.error(request, msg)
            return redirect("accounts:dashboard")

        return super().dispatch(request, *args, **kwargs)


class StocklotManagementContextMixin(SellerCompanyRequiredMixin):
    def get_management_context(self):
        company = self.get_user_company()
        return {
            "user_company": company,
            "my_stocklots_count": company.stocklots.count() if company else 0,
        }

    def _save_media(self, stocklot, replace_images=True, replace_videos=True, replace_documents=True):
        """
        Persist uploaded media files and bind them to the stocklot.
        - Images: append by default in update flows; optionally replace all.
        - Videos: single primary video; replace existing when a new one is provided.
        - Documents: append by default; optionally replace all.
        """
        request = self.request

        # Images
        image_files = request.FILES.getlist("media_images")
        if image_files:
            if replace_images:
                for img in stocklot.images.all():
                    img.file.delete(save=False)
                stocklot.images.all().delete()
            for uploaded in image_files:
                StocklotImage.objects.create(stocklot=stocklot, file=uploaded)

        # Videos (only first file kept)
        video_files = request.FILES.getlist("media_videos")
        if video_files:
            if replace_videos or stocklot.videos.exists():
                for vid in stocklot.videos.all():
                    vid.file.delete(save=False)
                stocklot.videos.all().delete()
            StocklotVideo.objects.create(stocklot=stocklot, file=video_files[0])

        # Documents
        doc_files = request.FILES.getlist("media_excel") + request.FILES.getlist("media_pdf")
        if doc_files:
            if replace_documents:
                for doc in stocklot.documents.all():
                    doc.file.delete(save=False)
                stocklot.documents.all().delete()
            for uploaded in doc_files:
                name = uploaded.name.lower()
                if name.endswith((".pdf",)):
                    doc_type = StocklotDocument.DocType.PDF
                elif name.endswith((".xls", ".xlsx", ".csv")):
                    doc_type = StocklotDocument.DocType.EXCEL
                else:
                    doc_type = StocklotDocument.DocType.OTHER
                StocklotDocument.objects.create(stocklot=stocklot, file=uploaded, doc_type=doc_type)


class StocklotCreateView(StocklotManagementContextMixin, CreateView):
    model = Stocklot
    form_class = StocklotForm
    template_name = "stocklots/stocklot_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_management_context())
        context.update(
            {
                "page_title": "Create stocklot",
                "page_intro": "Add a new stocklot with clear specs and pricing so buyers understand it before reaching out.",
                "submit_label": "Save listing",
            }
        )
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.company = self.get_user_company()
        if not self.request.user.is_staff:
            self.object.status = Stocklot.Status.PENDING_REVIEW
            self.object.is_admin_verified = False
        self.object.save()
        self._save_media(self.object, replace_images=True, replace_videos=True, replace_documents=True)
        messages.success(self.request, "Listing saved.")
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
        return (
            Stocklot.objects.select_related("company", "category")
            .prefetch_related("images", "documents", "videos")
            .filter(company=self.get_user_company())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_management_context())
        context.update(
            {
                "page_title": "Edit stocklot",
                "page_intro": "Refresh the existing stocklot details, pricing, or media so buyers always see accurate information.",
                "submit_label": "Save changes",
            }
        )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # Append new images/documents; replace the primary video if a new one is provided.
        self._save_media(self.object, replace_images=False, replace_videos=True, replace_documents=False)
        if not self.request.user.is_staff:
            self.object.status = Stocklot.Status.PENDING_REVIEW
            self.object.is_admin_verified = False
            self.object.save(update_fields=["status", "is_admin_verified"])
        messages.success(self.request, "Listing updated.")
        return response


class StocklotMarkSoldView(StocklotManagementContextMixin, View):
    def post(self, request, *args, **kwargs):
        stocklot = (
            Stocklot.objects.select_related("company")
            .filter(company=self.get_user_company(), slug=kwargs.get("slug"))
            .first()
        )
        if not stocklot:
            messages.error(request, "Stocklot not found or not allowed.")
            return redirect("stocklots:mine")

        stocklot.status = Stocklot.Status.ARCHIVED
        stocklot.is_active = False
        stocklot.save(update_fields=["status", "is_active"])
        messages.success(request, "Listing marked as sold and archived.")
        return redirect("stocklots:mine")


class StocklotDeleteView(StocklotManagementContextMixin, View):
    def post(self, request, *args, **kwargs):
        stocklot = (
            Stocklot.objects.select_related("company")
            .prefetch_related("images", "videos", "documents")
            .filter(company=self.get_user_company(), slug=kwargs.get("slug"))
            .first()
        )
        if not stocklot:
            messages.error(request, "Stocklot not found or not allowed.")
            return redirect("stocklots:mine")

        # Clean up associated media files
        for img in stocklot.images.all():
            img.file.delete(save=False)
        stocklot.images.all().delete()

        for vid in stocklot.videos.all():
            vid.file.delete(save=False)
        stocklot.videos.all().delete()

        for doc in stocklot.documents.all():
            doc.file.delete(save=False)
        stocklot.documents.all().delete()

        stocklot.delete()
        messages.success(request, "Listing deleted.")
        return redirect("stocklots:mine")


class StocklotDeactivateView(StocklotManagementContextMixin, View):
    def post(self, request, *args, **kwargs):
        stocklot = (
            Stocklot.objects.select_related("company")
            .filter(company=self.get_user_company(), slug=kwargs.get("slug"))
            .first()
        )
        if not stocklot:
            messages.error(request, "Stocklot not found or not allowed.")
            return redirect("stocklots:mine")

        stocklot.is_active = False
        if stocklot.status == Stocklot.Status.APPROVED:
            stocklot.status = Stocklot.Status.DRAFT
        stocklot.save(update_fields=["is_active", "status"])
        messages.success(request, "Listing deactivated.")
        return redirect("stocklots:mine")


class StocklotActivateView(StocklotManagementContextMixin, View):
    def post(self, request, *args, **kwargs):
        stocklot = (
            Stocklot.objects.select_related("company")
            .filter(company=self.get_user_company(), slug=kwargs.get("slug"))
            .first()
        )
        if not stocklot:
            messages.error(request, "Stocklot not found or not allowed.")
            return redirect("stocklots:mine")

        stocklot.is_active = True
        if request.user.is_staff:
            stocklot.status = Stocklot.Status.APPROVED
        else:
            stocklot.status = Stocklot.Status.PENDING_REVIEW
            stocklot.is_admin_verified = False
        stocklot.save(update_fields=["is_active", "status", "is_admin_verified"])
        messages.success(request, "Listing activated and sent for review." if not request.user.is_staff else "Listing activated and approved.")
        return redirect("stocklots:mine")


class StocklotUnmarkSoldView(StocklotManagementContextMixin, View):
    def post(self, request, *args, **kwargs):
        stocklot = (
            Stocklot.objects.select_related("company")
            .filter(company=self.get_user_company(), slug=kwargs.get("slug"))
            .first()
        )
        if not stocklot:
            messages.error(request, "Stocklot not found or not allowed.")
            return redirect("stocklots:mine")

        if stocklot.status == Stocklot.Status.ARCHIVED:
            stocklot.status = Stocklot.Status.DRAFT
        stocklot.is_active = True
        stocklot.is_admin_verified = False
        stocklot.save(update_fields=["status", "is_active", "is_admin_verified"])
        messages.success(request, "Listing restored from sold.")
        return redirect("stocklots:mine")
