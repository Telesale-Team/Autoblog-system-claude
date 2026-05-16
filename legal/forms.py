from django import forms
from .models import Contract


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ["title", "customer", "contract_type", "start_date", "end_date", "value", "file", "pdpa_compliant", "status", "notes"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date":   forms.DateInput(attrs={"type": "date"}),
            "notes":      forms.Textarea(attrs={"rows": 3}),
        }
