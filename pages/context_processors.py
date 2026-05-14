from django.db import models
from blog.models import Article, Category, Tag


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

    return {
        "recent_articles": recent_articles,
        "categories": categories,
        "tags": tags,
    }
