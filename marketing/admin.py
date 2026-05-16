from django.contrib import admin
from .models import Campaign, Keyword

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "channel", "budget", "kpi_leads", "actual_leads", "status", "start_date"]
    list_filter = ["channel", "status"]
    search_fields = ["name"]

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ["keyword", "intent", "search_volume", "difficulty", "current_rank", "target_position"]
    list_filter = ["intent"]
    search_fields = ["keyword"]
