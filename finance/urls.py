from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    # Invoices
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/add/", views.invoice_add, name="invoice_add"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/edit/", views.invoice_edit, name="invoice_edit"),
    path("invoices/<int:pk>/mark-paid/", views.invoice_mark_paid, name="invoice_mark_paid"),
    # Expenses
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/add/", views.expense_add, name="expense_add"),
    path("expenses/<int:pk>/edit/", views.expense_edit, name="expense_edit"),
]
