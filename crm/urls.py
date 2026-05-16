from django.urls import path
from . import views

app_name = "crm"

urlpatterns = [
    # Customers
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("customers/add/", views.customer_add, name="customer_add"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    # Quotes
    path("quotes/", views.quote_list, name="quote_list"),
    path("quotes/add/", views.quote_add, name="quote_add"),
    path("quotes/<int:pk>/", views.quote_detail, name="quote_detail"),
    path("quotes/<int:pk>/edit/", views.quote_edit, name="quote_edit"),
    # Renewals
    path("renewals/", views.renewal_list, name="renewal_list"),
    path("renewals/add/", views.renewal_add, name="renewal_add"),
    path("renewals/<int:pk>/edit/", views.renewal_edit, name="renewal_edit"),
]
