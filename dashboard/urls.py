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
    path("analytics/", views.redirect_to("dashboard:index"), name="analytics"),
    path("backlog/", views.backlog_view, name="backlog"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("api/events/", views.api_calendar_events, name="api_events"),
    path("api/events/<int:pk>/", views.api_calendar_event_detail, name="api_event_detail"),
    path("api/ep-articles/", views.api_ep_articles, name="api_ep_articles"),
    path("api/notes/", views.api_notes, name="api_notes"),
    path("api/notes/<int:pk>/", views.api_note_detail, name="api_note_detail"),
    path("team/", views.team_view, name="team"),
    path("blog/", views.blog_list, name="blog"),
    path("blog/new/", views.article_edit, name="article_new"),
    path("blog/<int:pk>/edit/", views.article_edit, name="article_edit"),
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
    path("kpi/",              views.kpi_dashboard,      name="kpi"),
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
    # Content Calendar ถูกลบแล้ว redirect ไป blog
    path("content-calendar/", views.redirect_to("dashboard:blog"), name="content_calendar"),
    # Frontend Designer
    path("design-system/",    views.design_system_view, name="design_system"),
    # Website Content Manager
    path("website-content/",                         views.website_content_view,    name="website_content"),
    path("website-content/service/<int:pk>/toggle/",  views.website_service_toggle,  name="website_service_toggle"),
    path("website-content/article/<int:pk>/toggle/",  views.website_article_toggle,  name="website_article_toggle"),
    path("website-content/portfolio/<int:pk>/toggle/",views.website_portfolio_toggle,name="website_portfolio_toggle"),
    path("website-content/stats/save/",               views.website_stats_save,       name="website_stats_save"),
    path("website-content/checkpoint/<int:pk>/save/", views.website_checkpoint_save,  name="website_checkpoint_save"),
    path("website-content/expertise/<int:pk>/save/",  views.website_expertise_save,   name="website_expertise_save"),
    path("website-content/value/<int:pk>/save/",     views.website_value_save,      name="website_value_save"),
    path("website-content/contact/save/",            views.website_contact_save,    name="website_contact_save"),
]
