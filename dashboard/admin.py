from django.contrib import admin
from .models import CalendarEvent, TeamStandup, Note

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "start_datetime", "is_completed", "assigned_to"]
    list_filter = ["category", "is_system", "is_completed"]

@admin.register(TeamStandup)
class TeamStandupAdmin(admin.ModelAdmin):
    list_display = ["agent_name", "date", "created_at"]
    list_filter = ["agent_name", "date"]

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["title", "color", "pinned", "updated_at"]
    list_filter = ["color", "pinned"]
