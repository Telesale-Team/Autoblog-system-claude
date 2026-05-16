from django.urls import path
from . import views

app_name = "legal"

urlpatterns = [
    # Contracts
    path("contracts/", views.contract_list, name="contract_list"),
    path("contracts/add/", views.contract_add, name="contract_add"),
    path("contracts/<int:pk>/", views.contract_detail, name="contract_detail"),
    path("contracts/<int:pk>/edit/", views.contract_edit, name="contract_edit"),
]
