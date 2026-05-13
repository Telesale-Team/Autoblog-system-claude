from django import forms
from django.utils import timezone
from .models import ContactLead


CONSENT_TEXT = (
    "ฉันยินยอมให้ AIBiz Thailand เก็บและประมวลผลข้อมูลส่วนบุคคลของฉัน "
    "เพื่อวัตถุประสงค์ในการติดต่อกลับและนำเสนอบริการที่เกี่ยวข้อง "
    "ตาม พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (PDPA) "
    "ข้อมูลจะถูกเก็บไม่เกิน 24 เดือน และสามารถขอลบได้ทุกเมื่อ"
)


class ContactForm(forms.ModelForm):
    consent_given = forms.BooleanField(
        required=True,
        label=CONSENT_TEXT,
        error_messages={"required": "ต้องยินยอม PDPA ก่อนส่งข้อความ"},
    )

    class Meta:
        model = ContactLead
        fields = ["name", "email", "phone", "company", "message", "consent_given"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "ชื่อ-สกุล"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "08X-XXX-XXXX"}),
            "company": forms.TextInput(attrs={"placeholder": "ชื่อบริษัท (ถ้ามี)"}),
            "message": forms.Textarea(attrs={"placeholder": "เล่าให้ฟังว่าธุรกิจคุณกำลังเจอปัญหาอะไร อยากให้ AI ช่วยอะไร..."}),
        }

    def save(self, commit=True, ip_address=None, source="landing", utm=None):
        instance = super().save(commit=False)
        instance.consent_text = CONSENT_TEXT
        instance.consent_given_at = timezone.now()
        instance.ip_address = ip_address
        instance.source = source
        if utm:
            instance.utm_source = utm.get("utm_source", "")
            instance.utm_medium = utm.get("utm_medium", "")
            instance.utm_campaign = utm.get("utm_campaign", "")
        if commit:
            instance.save()
        return instance
