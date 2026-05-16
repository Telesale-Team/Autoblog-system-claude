from django.contrib import admin
from .models import Invoice, Expense

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "customer", "subtotal", "total_payable", "status", "due_date"]
    list_filter = ["status", "wht_rate"]
    search_fields = ["invoice_number", "customer__company_name"]

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["date", "category", "description", "amount", "vendor_name"]
    list_filter = ["category", "is_deductible"]
    search_fields = ["description", "vendor_name"]
