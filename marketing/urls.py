from django.urls import path
from . import views

app_name = "marketing"

urlpatterns = [
    # Campaigns
    path("campaigns/", views.campaign_list, name="campaign_list"),
    path("campaigns/add/", views.campaign_add, name="campaign_add"),
    path("campaigns/<int:pk>/edit/", views.campaign_edit, name="campaign_edit"),
    # Keywords
    path("keywords/", views.keyword_list, name="keyword_list"),
    path("keywords/add/", views.keyword_add, name="keyword_add"),
    path("keywords/<int:pk>/edit/", views.keyword_edit, name="keyword_edit"),
]
