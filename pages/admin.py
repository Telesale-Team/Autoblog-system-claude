from django.contrib import admin
from .models import (ContactLead, LeadActivity, Service, SiteSetting, ContactTopic,
                     AboutPage, AboutStat, AboutValue, AboutCheckpoint, AboutExpertise,
                     HomePage, HomePain, HomeProcess, HomeTestimonial, HomeFAQ)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "price_start", "price_label", "is_featured", "status")
    list_editable = ("display_order", "is_featured", "status")
    list_filter = ("status", "is_featured")
    search_fields = ("name", "tagline")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("ข้อมูลหลัก", {
            "fields": ("name", "slug", "tagline", "description", "icon", "cover_image_url"),
        }),
        ("ราคา", {
            "fields": ("price_start", "price_label"),
        }),
        ("Features", {
            "fields": ("features",),
            "description": "พิมพ์แต่ละ feature ขึ้นบรรทัดใหม่ (Enter)",
        }),
        ("การแสดงผล", {
            "fields": ("display_order", "is_featured", "status"),
        }),
    )


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ("ข้อมูลติดต่อ", {
            "fields": ("contact_email", "line_id", "phone", "business_hours"),
        }),
        ("Contact Page — Hero", {
            "fields": ("contact_hero_title", "contact_hero_subtitle"),
        }),
        ("Contact Page — Channels", {
            "fields": ("line_desc", "email_desc", "form_desc"),
        }),
        ("Contact Page — Sidebar", {
            "fields": ("response_time", "guarantee"),
        }),
    )


@admin.register(ContactTopic)
class ContactTopicAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "url", "order")
    list_editable = ("order",)

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # ถ้ายังไม่มี record ให้สร้างและ redirect ไปหน้า edit ทันที
        obj, _ = SiteSetting.objects.get_or_create(pk=1)
        from django.shortcuts import redirect
        return redirect(f"/admin/pages/sitesetting/{obj.pk}/change/")


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Hero", {"fields": ("hero_title", "hero_subtitle", "hero_cta_text", "hero_cta2_text")}),
        ("Pain Section", {"fields": ("pain_title", "pain_subtitle")}),
        ("Process Section", {"fields": ("process_title", "process_subtitle")}),
        ("Testimonials Section", {"fields": ("testi_title",)}),
        ("FAQ Section", {"fields": ("faq_title",)}),
        ("CTA Section", {"fields": ("cta_title", "cta_subtitle", "cta_button")}),
    )
    def has_add_permission(self, request): return not HomePage.objects.exists()
    def has_delete_permission(self, request, obj=None): return False
    def changelist_view(self, request, extra_context=None):
        obj, _ = HomePage.objects.get_or_create(pk=1)
        from django.shortcuts import redirect
        return redirect(f"/admin/pages/homepage/{obj.pk}/change/")


@admin.register(HomePain)
class HomePainAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)


@admin.register(HomeProcess)
class HomeProcessAdmin(admin.ModelAdmin):
    list_display = ("step_num", "title", "order")
    list_editable = ("order",)


@admin.register(HomeTestimonial)
class HomeTestimonialAdmin(admin.ModelAdmin):
    list_display = ("author", "role", "order")
    list_editable = ("order",)


@admin.register(HomeFAQ)
class HomeFAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order")
    list_editable = ("order",)


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Hero Section", {"fields": ("hero_title", "hero_lead")}),
        ("Mission Section", {"fields": ("mission_title", "mission_body")}),
        ("CTA Section", {"fields": ("cta_title", "cta_subtitle", "cta_button_text")}),
    )
    def has_add_permission(self, request):
        return not AboutPage.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False
    def changelist_view(self, request, extra_context=None):
        obj, _ = AboutPage.objects.get_or_create(pk=1)
        from django.shortcuts import redirect
        return redirect(f"/admin/pages/aboutpage/{obj.pk}/change/")


@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    list_display = ("number", "label", "order")
    list_editable = ("order",)


@admin.register(AboutValue)
class AboutValueAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)


@admin.register(AboutCheckpoint)
class AboutCheckpointAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)


@admin.register(AboutExpertise)
class AboutExpertiseAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)


@admin.register(ContactLead)
class ContactLeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "source", "status", "next_follow_up",
                    "is_spam", "consent_given", "created_at")
    list_filter = ("is_spam", "status", "source", "consent_given", "created_at")
    search_fields = ("name", "email", "phone", "company", "message")
    readonly_fields = ("created_at", "updated_at", "consent_given_at", "ip_address",
                       "utm_source", "utm_medium", "utm_campaign", "deletable_after",
                       "spam_marked_at")
    fieldsets = (
        ("ข้อมูลลูกค้า", {
            "fields": ("name", "email", "phone", "company", "message"),
        }),
        ("CRM", {
            "fields": ("source", "status", "deal_value", "notes"),
        }),
        ("การตามงาน", {
            "fields": ("next_follow_up", "last_contacted_at", "created_by"),
        }),
        ("สแปม", {
            "fields": ("is_spam", "spam_marked_at"),
        }),
        ("PDPA", {
            "fields": ("consent_given", "consent_text", "consent_given_at",
                       "ip_address", "deletable_after"),
        }),
        ("UTM Tracking", {
            "fields": ("utm_source", "utm_medium", "utm_campaign"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ("lead", "kind", "occurred_at", "created_by")
    list_filter = ("kind", "occurred_at")
    search_fields = ("lead__name", "lead__email", "note")
    autocomplete_fields = ("lead",)
