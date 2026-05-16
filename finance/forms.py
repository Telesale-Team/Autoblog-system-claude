from django import forms
from .models import Invoice, Expense


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ["customer", "service_description", "subtotal", "wht_rate", "issue_date", "due_date", "payment_method", "withholding_cert_no", "is_vat_registered", "status"]
        widgets = {
            "issue_date":          forms.DateInput(attrs={"type": "date"}),
            "due_date":            forms.DateInput(attrs={"type": "date"}),
            "service_description": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "subtotal": "ยอดก่อน VAT — ระบบจะคำนวณ VAT 7% และ WHT อัตโนมัติ",
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["date", "category", "amount", "description", "vendor_name", "is_deductible", "tax_invoice_no", "payment_method", "receipt"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
