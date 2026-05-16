from django.contrib import admin
from .models import CalendarEvent, Note

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "start_datetime", "is_completed", "assigned_to"]
    list_filter = ["category", "is_system", "is_completed"]

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ["title", "color", "pinned", "updated_at"]
    list_filter = ["color", "pinned"]
