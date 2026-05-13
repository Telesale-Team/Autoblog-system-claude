from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("projects/", views.coming_soon, name="projects"),
    path("loi/", views.coming_soon, name="loi"),
    path("retail/", views.coming_soon, name="retail"),
    path("gap/", views.coming_soon, name="gap"),
    path("savings/", views.coming_soon, name="savings"),
    path("docs/", views.docs_index, name="docs_index"),
    path("docs/<slug:slug>/", views.docs_view, name="docs_view"),
]
