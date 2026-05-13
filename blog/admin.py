from django.contrib import admin
from .models import Category, Tag, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "status", "is_featured", "views_count", "published_at")
    list_filter = ("status", "is_featured", "category", "tags", "published_at")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    readonly_fields = ("views_count", "created_at", "updated_at")
    date_hierarchy = "published_at"
    fieldsets = (
        ("เนื้อหา", {
            "fields": ("title", "slug", "category", "tags", "excerpt", "content", "cover_image"),
        }),
        ("Publishing", {
            "fields": ("author", "status", "is_featured", "published_at"),
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description", "og_image"),
            "classes": ("collapse",),
        }),
        ("Stats", {
            "fields": ("views_count", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
