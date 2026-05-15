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
    # legacy coming-soon routes (keep for backward compat)
    path("projects/", views.coming_soon, name="projects"),
    path("loi/", views.coming_soon, name="loi"),
    path("retail/", views.coming_soon, name="retail"),
    path("gap/", views.coming_soon, name="gap"),
    path("savings/", views.coming_soon, name="savings"),
]
