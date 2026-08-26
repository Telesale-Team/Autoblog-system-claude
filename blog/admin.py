from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

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


class ArticleAdminForm(forms.ModelForm):
    """ช่อง Markdown ใช้ textarea monospace ตัวใหญ่ อ่าน/แก้โค้ดได้สบาย"""

    class Meta:
        model = Article
        fields = "__all__"
        widgets = {
            "content_md": forms.Textarea(attrs={
                "rows": 40,
                "style": ("font-family: Consolas, 'Cascadia Mono', monospace;"
                          "font-size: 13px; line-height: 1.6; width: 100%;"
                          "white-space: pre; overflow-wrap: normal; overflow-x: auto;"),
                "spellcheck": "false",
            }),
        }


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ("title", "category", "author", "content_format", "layout",
                    "status", "is_featured", "views_count", "published_at")
    list_filter = ("status", "content_format", "layout", "is_featured", "category", "tags", "published_at")
    search_fields = ("title", "excerpt", "content", "content_md")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    date_hierarchy = "published_at"
    fieldsets = (
        ("รูปแบบ", {
            "fields": ("content_format", "layout"),
            "description": mark_safe(
                "<b>HTML</b> = เขียนใน CKEditor ตามปกติ (บทความการตลาดทั่วไป)<br>"
                "<b>Markdown</b> = เขียนในช่อง 'เนื้อหา (Markdown)' ด้านล่าง "
                "ระบบแปลงเป็น HTML ให้ตอนเซฟ — ใช้กับบทเรียน/คู่มือที่มี callout, step, "
                "code block, SVG เพราะ CKEditor จะลบของพวกนี้ทิ้ง<br>"
                "<a href='/static/docs/markdown_cheatsheet.html' target='_blank'>ดูสูตร Markdown ทั้งหมด</a>"
            ),
        }),
        ("เนื้อหา", {
            "fields": ("title", "slug", "category", "tags", "excerpt",
                       "content_md", "content", "cover_image"),
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

    def get_readonly_fields(self, request, obj=None):
        """
        บทความ Markdown -> ล็อกช่อง content ไม่ให้เปิด CKEditor
        กันปัญหา CKEditor ลบ callout/SVG ทิ้งตอนเซฟ (ต้นฉบับอยู่ที่ content_md อยู่แล้ว)
        """
        base = ["views_count", "created_at", "updated_at"]
        if obj and obj.content_format == "markdown":
            base.append("content")
        return base

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
