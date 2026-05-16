from django.contrib import admin
from .models import Contract

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["title", "customer", "contract_type", "value", "end_date", "pdpa_compliant", "status"]
    list_filter = ["contract_type", "status", "pdpa_compliant"]
    search_fields = ["title", "customer__company_name"]
