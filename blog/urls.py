from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.ArticleListView.as_view(), name="list"),
    path("category/<slug:slug>/", views.CategoryView.as_view(), name="category"),
    path("tag/<slug:slug>/", views.TagView.as_view(), name="tag"),
    path("<slug:slug>/", views.ArticleDetailView.as_view(), name="detail"),
]
