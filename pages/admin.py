from django.contrib import admin
from .models import ContactLead


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
