from django.contrib import admin
from .models import Campaign, ContentCalendar, Keyword

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "channel", "budget", "kpi_leads", "actual_leads", "status", "start_date"]
    list_filter = ["channel", "status"]
    search_fields = ["name"]

@admin.register(ContentCalendar)
class ContentCalendarAdmin(admin.ModelAdmin):
    list_display = ["__str__", "channel", "scheduled_date", "status", "assigned_agent"]
    list_filter = ["channel", "status"]

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ["keyword", "intent", "search_volume", "difficulty", "current_rank", "target_position"]
    list_filter = ["intent"]
    search_fields = ["keyword"]
