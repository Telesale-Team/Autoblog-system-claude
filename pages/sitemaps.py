from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Article, Category


class StaticSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return ["pages:home", "pages:about", "pages:services", "pages:contact"]

    def location(self, item):
        return reverse(item)


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Article.objects.filter(status="published").order_by("-published_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()
