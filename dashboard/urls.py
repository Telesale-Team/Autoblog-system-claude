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

    # ── Agent Feature Routes — redirect to feature apps ──────────────────
    # Chief of Staff
    path("standup/",          views.coming_soon, name="standup"),
    # Hustler
    path("quotes/",           views.redirect_to("crm:quote_list"),          name="quotes"),
    # Money Manager
    path("expenses/",         views.redirect_to("finance:expense_list"),    name="expenses"),
    path("invoices/",         views.redirect_to("finance:invoice_list"),    name="invoices"),
    # Marketing Specialist
    path("campaigns/",        views.redirect_to("marketing:campaign_list"), name="campaigns"),
    # Customer Success
    path("customers/",        views.redirect_to("crm:customer_list"),       name="customers"),
    path("renewals/",         views.redirect_to("crm:renewal_list"),        name="renewals"),
    # Data Analyst
    path("kpi/",              views.coming_soon, name="kpi"),
    # Legal Advisor
    path("contracts/",        views.redirect_to("legal:contract_list"),     name="contracts"),
    # AI Orchestrator
    path("ai-projects/",      views.redirect_to("operations:project_list"), name="ai_projects"),
    # AI Toolsmith
    path("prompt-library/",   views.redirect_to("operations:prompt_list"),  name="prompt_library"),
    # QA Agent
    path("qa-log/",           views.redirect_to("operations:qa_list"),      name="qa_log"),
    # SEO Specialist
    path("keywords/",         views.redirect_to("marketing:keyword_list"),  name="keywords"),
    # Content Writer
    path("content-calendar/", views.redirect_to("marketing:content_calendar"), name="content_calendar"),
    # Frontend Designer
    path("design-system/",    views.coming_soon, name="design_system"),
]
