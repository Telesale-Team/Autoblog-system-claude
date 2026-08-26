from django.contrib import admin
from .models import AIProject, PromptLibrary, QALog, Deployment, HealthCheck

@admin.register(AIProject)
class AIProjectAdmin(admin.ModelAdmin):
    list_display = ["project_name", "customer", "service", "status", "go_live_date", "monthly_fee"]
    list_filter = ["status", "is_active", "service"]
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


@admin.register(Deployment)
class DeploymentAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "environment", "base_url", "is_monitored",
                    "is_critical", "is_internal", "monthly_fee"]
    list_filter = ["environment", "is_monitored", "is_critical", "is_internal"]
    search_fields = ["name", "base_url", "server_host", "service_name"]
    autocomplete_fields = []


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    list_display = ["deployment", "checked_at", "is_up", "status_code", "response_ms", "version"]
    list_filter = ["is_up", "deployment"]
    readonly_fields = ["checked_at"]
