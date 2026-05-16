from django.contrib import admin
from .models import AIProject, PromptLibrary, QALog

@admin.register(AIProject)
class AIProjectAdmin(admin.ModelAdmin):
    list_display = ["project_name", "customer", "status", "go_live_date", "monthly_fee"]
    list_filter = ["status", "is_active"]
    search_fields = ["project_name"]

@admin.register(PromptLibrary)
class PromptLibraryAdmin(admin.ModelAdmin):
    list_display = ["title", "agent", "use_case", "version", "rating"]
    list_filter = ["agent", "rating"]
    search_fields = ["title", "use_case"]

@admin.register(QALog)
class QALogAdmin(admin.ModelAdmin):
    list_display = ["output_type", "agent", "result", "severity", "reviewed_at"]
    list_filter = ["agent", "result", "severity"]
