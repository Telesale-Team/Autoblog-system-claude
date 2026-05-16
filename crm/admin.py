from django.contrib import admin
from .models import Customer, Quote, Renewal

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["company_name", "tier", "health_score", "contract_value", "contract_end", "account_owner"]
    list_filter = ["tier", "is_active"]
    search_fields = ["company_name", "industry", "account_owner"]

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ["quote_number", "lead", "total", "status", "valid_until"]
    list_filter = ["status"]
    search_fields = ["quote_number"]

@admin.register(Renewal)
class RenewalAdmin(admin.ModelAdmin):
    list_display = ["customer", "renewal_date", "mrr_value", "status", "assigned_to"]
    list_filter = ["status"]
