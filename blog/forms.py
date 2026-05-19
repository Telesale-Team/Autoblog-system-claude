from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Article, Category, Tag


class ArticleForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditor5Widget(config_name="extends", attrs={"class": "django_ckeditor_5"}),
        label="เนื้อหา",
        required=False,
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Tags",
    )

    class Meta:
        model = Article
        fields = [
            "title", "slug", "category", "tags",
            "excerpt", "content",
            "cover_image_url",
            "meta_title", "meta_description",
            "status", "is_featured",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "ชื่อบทความ"}),
            "slug": forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": "auto-generate ถ้าว่าง"}),
            "category": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "excerpt": forms.Textarea(attrs={"class": "form-control form-control-sm", "rows": 3, "placeholder": "สรุปย่อ (~160 chars)"}),
            "cover_image_url": forms.URLInput(attrs={"class": "form-control form-control-sm", "placeholder": "https://..."}),
            "meta_title": forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": "≤60 chars"}),
            "meta_description": forms.TextInput(attrs={"class": "form-control form-control-sm", "placeholder": "≤155 chars"}),
            "status": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
