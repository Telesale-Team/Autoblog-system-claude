from django.contrib import admin
from .models import ContactLead, Service, SiteSetting, AboutStat, AboutValue


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
            "description": "ข้อมูลเหล่านี้จะแสดงในหน้าติดต่อเรา",
        }),
    )

    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # ถ้ายังไม่มี record ให้สร้างและ redirect ไปหน้า edit ทันที
        obj, _ = SiteSetting.objects.get_or_create(pk=1)
        from django.shortcuts import redirect
        return redirect(f"/admin/pages/sitesetting/{obj.pk}/change/")


@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    list_display = ("number", "label", "order")
    list_editable = ("order",)


@admin.register(AboutValue)
class AboutValueAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "order")
    list_editable = ("order",)


@admin.register(ContactLead)
class ContactLeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "source", "status", "consent_given", "created_at")
    list_filter = ("status", "source", "consent_given", "created_at")
    search_fields = ("name", "email", "phone", "company", "message")
    readonly_fields = ("created_at", "updated_at", "consent_given_at", "ip_address",
                       "utm_source", "utm_medium", "utm_campaign", "deletable_after")
    fieldsets = (
        ("ข้อมูลลูกค้า", {
            "fields": ("name", "email", "phone", "company", "message"),
        }),
        ("CRM", {
            "fields": ("source", "status", "notes"),
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
