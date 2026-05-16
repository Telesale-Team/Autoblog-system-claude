from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("leads/", views.leads_list, name="leads"),
    path("leads/<int:pk>/status/", views.lead_update_status, name="lead_status"),
    path("pipeline/", views.pipeline_view, name="pipeline"),
    path("pipeline/<int:pk>/deal-value/", views.lead_update_deal_value, name="lead_deal_value"),
    path("revenue/", views.revenue_view, name="revenue"),
    path("analytics/", views.analytics_view, name="analytics"),
    path("backlog/", views.backlog_view, name="backlog"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("api/events/", views.api_calendar_events, name="api_events"),
    path("api/events/<int:pk>/", views.api_calendar_event_detail, name="api_event_detail"),
    path("team/", views.team_view, name="team"),
    path("blog/", views.blog_list, name="blog"),
    path("blog/<int:pk>/toggle/", views.article_toggle_status, name="article_toggle"),
    path("docs/", views.docs_index, name="docs_index"),
    path("docs/<slug:slug>/", views.docs_view, name="docs_view"),
    path("docs/<slug:slug>/content/", views.docs_content, name="docs_content"),
    # legacy coming-soon routes (keep for backward compat)
    path("projects/", views.coming_soon, name="projects"),
    path("loi/", views.coming_soon, name="loi"),
    path("retail/", views.coming_soon, name="retail"),
    path("gap/", views.coming_soon, name="gap"),
    path("savings/", views.coming_soon, name="savings"),

    # ── Agent Feature Routes (Phase 1 — coming soon) ──────────────────
    # Chief of Staff
    path("standup/",         views.coming_soon, name="standup"),
    # Hustler
    path("quotes/",          views.coming_soon, name="quotes"),
    # Money Manager
    path("expenses/",        views.coming_soon, name="expenses"),
    path("invoices/",        views.coming_soon, name="invoices"),
    # Marketing Specialist
    path("campaigns/",       views.coming_soon, name="campaigns"),
    # Customer Success
    path("customers/",       views.coming_soon, name="customers"),
    path("renewals/",        views.coming_soon, name="renewals"),
    # Data Analyst
    path("kpi/",             views.coming_soon, name="kpi"),
    # Legal Advisor
    path("contracts/",       views.coming_soon, name="contracts"),
    # AI Orchestrator
    path("ai-projects/",     views.coming_soon, name="ai_projects"),
    # AI Toolsmith
    path("prompt-library/",  views.coming_soon, name="prompt_library"),
    # QA Agent
    path("qa-log/",          views.coming_soon, name="qa_log"),
    # SEO Specialist
    path("keywords/",        views.coming_soon, name="keywords"),
    # Content Writer
    path("content-calendar/",views.coming_soon, name="content_calendar"),
    # Frontend Designer
    path("design-system/",   views.coming_soon, name="design_system"),
]
