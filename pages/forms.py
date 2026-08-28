from django import forms
from django.conf import settings
from django.utils import timezone

from .models import ContactLead

# ชื่อช่องกับดักบอท — ตั้งชื่อให้ดูน่ากรอกสำหรับสคริปต์ที่กรอกทุกช่องที่เจอ
# คนจริงไม่เห็นช่องนี้ (ซ่อนด้วย CSS + aria-hidden) จึงไม่มีทางกรอก
HONEYPOT_FIELD = "website"


CONSENT_TEXT = (
    "ฉันยินยอมให้ AIBiz Thailand เก็บและประมวลผลข้อมูลส่วนบุคคลของฉัน "
    "เพื่อวัตถุประสงค์ในการติดต่อกลับและนำเสนอบริการที่เกี่ยวข้อง "
    "ตาม พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (PDPA) "
    "ข้อมูลจะถูกเก็บไม่เกิน 24 เดือน และสามารถขอลบได้ทุกเมื่อ"
)


class ContactForm(forms.ModelForm):
    """ฟอร์มติดต่อบนหน้าเว็บสาธารณะ — มีด่านกันบอท 2 ชั้น

    ชั้นที่ 1 กับดัก (honeypot): ช่องที่คนมองไม่เห็น ถ้ามีค่า = บอทกรอก
    ชั้นที่ 2 reCAPTCHA: เปิดเมื่อมีกุญแจใน .env ครบ (settings.RECAPTCHA_ENABLED)

    ทำไมต้องสองชั้น: กับดักดักบอทถูก ๆ ได้ฟรีโดยลูกค้าไม่ต้องกดอะไรเลย
    ส่วน reCAPTCHA ดักตัวที่ฉลาดกว่า แต่เพิ่มขั้นตอนให้ลูกค้า จึงให้กับดักทำงานก่อน
    """

    consent_given = forms.BooleanField(
        required=True,
        label=CONSENT_TEXT,
        error_messages={"required": "ต้องยินยอม PDPA ก่อนส่งข้อความ"},
    )

    # ช่องกับดัก — ต้องเว้นว่างเสมอ
    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "tabindex": "-1",
            "autocomplete": "off",
            "aria-hidden": "true",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(settings, "RECAPTCHA_ENABLED", False):
            from django_recaptcha.fields import ReCaptchaField
            from django_recaptcha.widgets import ReCaptchaV2Checkbox

            self.fields["captcha"] = ReCaptchaField(
                widget=ReCaptchaV2Checkbox(attrs={"data-theme": "light"}),
                label="",
                error_messages={
                    "required": "กรุณาทำเครื่องหมายยืนยันว่าไม่ใช่บอทก่อนส่งข้อความ",
                },
            )

    def clean_website(self):
        """กับดักบอท — ถ้าช่องนี้มีค่า แปลว่าไม่ใช่คน"""
        value = self.cleaned_data.get(HONEYPOT_FIELD, "")
        if value:
            raise forms.ValidationError("ไม่สามารถส่งข้อความได้ กรุณาติดต่อทาง LINE แทน")
        return value

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
