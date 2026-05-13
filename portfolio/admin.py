from django.contrib import admin
from .models import CaseStudy, CaseStudyImage


class CaseStudyImageInline(admin.TabularInline):
    model = CaseStudyImage
    extra = 1


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ("project_title", "industry", "status", "is_featured", "display_order", "published_at")
    list_filter = ("status", "is_featured", "industry", "published_at")
    search_fields = ("project_title", "client_name", "problem", "result", "tech_stack")
    prepopulated_fields = {"slug": ("project_title",)}
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "published_at"
    inlines = [CaseStudyImageInline]
    fieldsets = (
        ("ข้อมูลโปรเจกต์", {
            "fields": ("project_title", "slug", "client_name", "industry", "cover_image"),
        }),
        ("เนื้อหา Case Study", {
            "fields": ("problem", "solution", "result", "roi_metric"),
        }),
        ("Testimonial", {
            "fields": ("testimonial", "testimonial_by"),
        }),
        ("Technical", {
            "fields": ("tech_stack", "duration"),
        }),
        ("Publishing", {
            "fields": ("status", "is_featured", "display_order", "published_at"),
        }),
        ("SEO", {
            "fields": ("meta_title", "meta_description"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
