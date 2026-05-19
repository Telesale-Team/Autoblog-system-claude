from django.views.generic import ListView, DetailView
from .models import CaseStudy


class CaseStudyListView(ListView):
    model = CaseStudy
    template_name = "portfolio/list.html"
    context_object_name = "case_studies"
    paginate_by = 9

    def get_queryset(self):
        qs = CaseStudy.objects.filter(status="published")
        industry = self.request.GET.get("industry")
        if industry:
            qs = qs.filter(industry=industry)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["industries"] = CaseStudy.INDUSTRY_CHOICES
        ctx["active_industry"] = self.request.GET.get("industry", "")
        return ctx


class CaseStudyDetailView(DetailView):
    model = CaseStudy
    template_name = "portfolio/detail.html"
    context_object_name = "case"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return CaseStudy.objects.filter(status="published").prefetch_related("images")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["related"] = (
            CaseStudy.objects.filter(status="published")
            .exclude(pk=self.object.pk)
            .order_by("display_order", "-published_at")[:8]
        )
        return ctx
