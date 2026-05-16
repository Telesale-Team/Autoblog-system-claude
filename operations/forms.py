from django import forms
from .models import AIProject, PromptLibrary, QALog


class AIProjectForm(forms.ModelForm):
    class Meta:
        model = AIProject
        fields = ["project_name", "customer", "status", "go_live_date", "monthly_fee", "description"]
        widgets = {
            "go_live_date": forms.DateInput(attrs={"type": "date"}),
            "description":  forms.Textarea(attrs={"rows": 4}),
        }


class PromptLibraryForm(forms.ModelForm):
    class Meta:
        model = PromptLibrary
        fields = ["title", "agent", "use_case", "prompt_text", "version", "rating"]
        widgets = {
            "prompt_text": forms.Textarea(attrs={"rows": 10, "class": "font-monospace"}),
        }


class QALogForm(forms.ModelForm):
    class Meta:
        model = QALog
        fields = ["output_type", "agent", "result", "issue_category", "severity", "notes", "reviewed_at"]
        widgets = {
            "reviewed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes":       forms.Textarea(attrs={"rows": 4}),
        }
