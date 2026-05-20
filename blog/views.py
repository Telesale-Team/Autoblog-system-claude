from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import F, Q
from .models import Article, Category, Tag


class ArticleListView(ListView):
    model = Article
    template_name = "blog/list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        qs = Article.objects.filter(status="published").select_related("category", "author")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/detail.html"
    context_object_name = "article"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Article.objects.filter(status="published").select_related("category", "author").prefetch_related("tags")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        Article.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["related"] = (
            Article.objects.filter(status="published", category=self.object.category)
            .exclude(pk=self.object.pk)[:6]
        )
        ctx["categories"] = Category.objects.all()
        return ctx


class CategoryView(ListView):
    template_name = "blog/list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return Article.objects.filter(status="published", category=self.category).select_related("category", "author")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["active_category"] = self.category
        return ctx


class TagView(ListView):
    template_name = "blog/list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return Article.objects.filter(status="published", tags=self.tag).select_related("category", "author")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["active_tag"] = self.tag
        return ctx
