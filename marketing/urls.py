from django.urls import path
from . import views

app_name = "marketing"

urlpatterns = [
    # Campaigns
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/add/", views.campaign_add, name="campaign_add"),
    path("campaigns/<int:pk>/edit/", views.campaign_edit, name="campaign_edit"),
    # Content Calendar
    path("content-calendar/", views.content_calendar, name="content_calendar"),
    path("content-calendar/add/", views.content_calendar_add, name="content_calendar_add"),
    path("content-calendar/<int:pk>/edit/", views.content_calendar_edit, name="content_calendar_edit"),
    # Keywords
    path("keywords/", views.keyword_list, name="keyword_list"),
    path("keywords/add/", views.keyword_add, name="keyword_add"),
    path("keywords/<int:pk>/edit/", views.keyword_edit, name="keyword_edit"),
]
