from django.db import models
from blog.models import Article, Category, Tag
from pages.models import ContactLead


def global_context(request):
    recent_articles = Article.objects.filter(
        status="published"
    ).select_related("category").order_by("-published_at")[:4]

    categories = Category.objects.annotate(
        article_count=models.Count("articles", filter=models.Q(articles__status="published"))
    ).filter(article_count__gt=0).order_by("display_order", "name")

    tags = Tag.objects.annotate(
        article_count=models.Count("articles", filter=models.Q(articles__status="published"))
    ).filter(article_count__gt=0).order_by("name")[:20]

    # Sidebar badge counts (only for authenticated staff — skip DB hit for guests)
    sidebar_new_leads = 0
    sidebar_draft_articles = 0
    if request.user.is_authenticated and request.user.is_staff:
        sidebar_new_leads = ContactLead.objects.filter(status="new").count()
        sidebar_draft_articles = Article.objects.filter(status="draft").count()

    return {
        "recent_articles": recent_articles,
        "categories": categories,
        "tags": tags,
        "sidebar_new_leads": sidebar_new_leads,
        "sidebar_draft_articles": sidebar_draft_articles,
    }
