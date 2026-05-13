from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.CaseStudyListView.as_view(), name="list"),
    path("<slug:slug>/", views.CaseStudyDetailView.as_view(), name="detail"),
]
