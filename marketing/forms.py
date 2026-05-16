from django import forms
from .models import Campaign, ContentCalendar, Keyword


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["name", "channel", "budget", "start_date", "end_date", "kpi_leads", "actual_leads", "status", "notes"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date":   forms.DateInput(attrs={"type": "date"}),
            "notes":      forms.Textarea(attrs={"rows": 3}),
        }


class ContentCalendarForm(forms.ModelForm):
    class Meta:
        model = ContentCalendar
        fields = ["article", "title", "scheduled_date", "channel", "assigned_agent", "status", "notes"]
        widgets = {
            "scheduled_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes":          forms.Textarea(attrs={"rows": 3}),
        }


class KeywordForm(forms.ModelForm):
    class Meta:
        model = Keyword
        fields = ["keyword", "search_volume", "difficulty", "intent", "current_rank", "target_position", "last_checked_date", "article", "notes"]
        widgets = {
            "last_checked_date": forms.DateInput(attrs={"type": "date"}),
            "notes":             forms.Textarea(attrs={"rows": 3}),
        }
