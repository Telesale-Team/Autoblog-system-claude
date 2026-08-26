from django.urls import path
from . import views

app_name = "operations"

urlpatterns = [
    # AI Projects
    path("projects/", views.project_list, name="project_list"),
    path("projects/add/", views.project_add, name="project_add"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
    path("projects/<int:pk>/edit/", views.project_edit, name="project_edit"),
    # Project Monitor
    path("monitor/", views.monitor, name="monitor"),
    path("monitor/<int:pk>/", views.monitor_detail, name="monitor_detail"),
    # Prompt Library
    path("prompts/", views.prompt_list, name="prompt_list"),
    path("prompts/add/", views.prompt_add, name="prompt_add"),
    path("prompts/<int:pk>/edit/", views.prompt_edit, name="prompt_edit"),
    # QA Log
    path("qa/", views.qa_list, name="qa_list"),
    path("qa/add/", views.qa_add, name="qa_add"),
    path("qa/<int:pk>/edit/", views.qa_edit, name="qa_edit"),
]
