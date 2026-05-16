from django import forms
from .models import Customer, Quote, Renewal


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["company_name", "industry", "tier", "contract_value", "health_score", "nps_score", "contract_start", "contract_end", "account_owner", "notes"]
        widgets = {
            "contract_start": forms.DateInput(attrs={"type": "date"}),
            "contract_end":   forms.DateInput(attrs={"type": "date"}),
            "notes":          forms.Textarea(attrs={"rows": 3}),
        }


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ["lead", "valid_until", "status", "notes"]
        widgets = {
            "valid_until": forms.DateInput(attrs={"type": "date"}),
            "notes":       forms.Textarea(attrs={"rows": 3}),
        }


class RenewalForm(forms.ModelForm):
    class Meta:
        model = Renewal
        fields = ["customer", "renewal_date", "mrr_value", "prev_mrr", "status", "assigned_to", "notes"]
        widgets = {
            "renewal_date": forms.DateInput(attrs={"type": "date"}),
            "notes":        forms.Textarea(attrs={"rows": 3}),
        }
