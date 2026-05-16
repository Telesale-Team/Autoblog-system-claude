from django import forms
from .models import TeamStandup


class TeamStandupForm(forms.ModelForm):
    class Meta:
        model = TeamStandup
        fields = ["agent_name", "date", "yesterday", "today", "blocker"]
        widgets = {
            "date":      forms.DateInput(attrs={"type": "date"}),
            "yesterday": forms.Textarea(attrs={"rows": 3}),
            "today":     forms.Textarea(attrs={"rows": 3}),
            "blocker":   forms.Textarea(attrs={"rows": 2}),
        }
