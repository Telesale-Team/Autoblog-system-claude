from django.contrib import admin
from .models import Campaign, Keyword, ContentBacklog

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "channel", "budget", "kpi_leads", "actual_leads", "status", "start_date"]
    list_filter = ["channel", "status"]
    search_fields = ["name"]

@admin.register(ContentBacklog)
class ContentBacklogAdmin(admin.ModelAdmin):
    list_display = ["num", "topic", "keyword", "priority", "status", "owner"]
    list_filter = ["priority", "status"]
    search_fields = ["topic", "keyword"]
    list_editable = ["status", "priority"]

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ["keyword", "intent", "search_volume", "difficulty", "current_rank", "target_position"]
    list_filter = ["intent"]
    search_fields = ["keyword"]
