"""ฟอร์มของหลังบ้าน (/owner/)

ทำไม lead ต้องมีฟอร์มของตัวเองแทนที่จะใช้หน้า admin ของ Django:
GTM สั่งให้ทัก DM สัปดาห์ละ 50 ราย บวก LINE OA และคนแนะนำต่อ
คนที่เราไปหาเองจึงเป็น lead ส่วนใหญ่ แต่ทั้งโปรเจกต์เดิมไม่มีทางบันทึกเลย
นอกจากฟอร์มบนเว็บสาธารณะ — lead กลุ่มนี้จึงไม่มีที่ลงและหายไปกับแชท
"""

from datetime import timedelta

from django import forms
from django.utils import timezone

from pages.models import ContactLead, LeadActivity


# กันความสับสน: ช่องทางที่เว็บกรอกให้เองอัตโนมัติ ไม่ควรให้เลือกตอนบันทึกมือ
WEB_ONLY_SOURCES = ("landing", "blog", "portfolio")


class LeadForm(forms.ModelForm):
    """บันทึก lead ที่ได้มาจากนอกเว็บ — DM / LINE / คนแนะนำต่อ / งานอีเวนต์"""

    class Meta:
        model = ContactLead
        fields = [
            "name", "email", "phone", "company",
            "source", "message",
            "status", "deal_value", "next_follow_up",
            "notes", "consent_given",
        ]
        labels = {
            "consent_given": "ได้รับความยินยอมให้เก็บข้อมูลแล้ว (PDPA)",
        }
        help_texts = {
            "consent_given": "ติ๊กเมื่อเจ้าตัวรับรู้และยินยอมให้เราเก็บข้อมูลติดต่อ "
                             "เช่น เขาให้เบอร์มาเองในแชท",
            "message": "เขาสนใจอะไร คุยกันมาถึงไหนแล้ว",
        }
        widgets = {
            "name":    forms.TextInput(attrs={"class": "form-control", "placeholder": "ชื่อ-สกุล"}),
            "email":   forms.EmailInput(attrs={"class": "form-control", "placeholder": "ไม่มีก็เว้นว่างได้"}),
            "phone":   forms.TextInput(attrs={"class": "form-control", "placeholder": "08X-XXX-XXXX"}),
            "company": forms.TextInput(attrs={"class": "form-control", "placeholder": "ชื่อร้าน / บริษัท"}),
            "source":  forms.Select(attrs={"class": "form-select"}),
            "status":  forms.Select(attrs={"class": "form-select"}),
            "deal_value": forms.NumberInput(attrs={"class": "form-control", "placeholder": "0"}),
            "next_follow_up": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "notes":   forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "consent_given": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # อีเมลไม่บังคับ เพราะ lead จาก LINE หรือ DM มักมีแค่ชื่อกับเบอร์
        self.fields["email"].required = False
        self.fields["message"].required = False
        # ตัดช่องทางที่เว็บกรอกให้เองออก เหลือเฉพาะช่องทางที่คนไปหามาเอง
        # ยกเว้นตอนแก้ไข lead ที่มาจากเว็บอยู่แล้ว ต้องคงค่าเดิมไว้ในตัวเลือก
        # ไม่งั้นกดบันทึกแล้วจะไม่ผ่านด้วยเหตุผลที่คนใช้งานไม่มีทางเดาถูก
        # เฉพาะแถวที่บันทึกไว้แล้วเท่านั้น — ของใหม่ instance.source เป็นค่า default ของ model
        current_source = self.instance.source if self.instance.pk else None
        self.fields["source"].choices = [
            (value, label)
            for value, label in ContactLead.SOURCE_CHOICES
            if value not in WEB_ONLY_SOURCES or value == current_source
        ]
        if not self.instance.pk:
            self.fields["source"].initial = "cold_dm"
            # ตั้งวันตามต่อล่วงหน้า 2 วันเป็นค่าตั้งต้น จะได้ไม่มี lead ที่ไม่มีอะไรทวง
            self.fields["next_follow_up"].initial = timezone.localdate() + timedelta(days=2)

    def clean(self):
        cleaned = super().clean()
        # ต้องติดต่อกลับได้อย่างน้อยทางใดทางหนึ่ง ไม่งั้นบันทึกไปก็ทำอะไรต่อไม่ได้
        if not cleaned.get("email") and not cleaned.get("phone"):
            raise forms.ValidationError("ต้องมีอีเมลหรือเบอร์โทรอย่างน้อยหนึ่งอย่าง ไม่งั้นติดต่อกลับไม่ได้")
        return cleaned

    def save(self, commit=True, created_by=None):
        lead = super().save(commit=False)
        if not lead.email:
            # ใส่ที่อยู่ภายในให้ เพื่อไม่ให้ช่องบังคับของ model ว่าง
            digits = (lead.phone or "no-phone").replace("-", "").replace(" ", "")
            lead.email = f"{digits}@manual.aibizth.ai"
        if created_by and not lead.pk:
            lead.created_by = created_by
        if commit:
            lead.save()
        return lead


class LeadActivityForm(forms.ModelForm):
    """บันทึกว่าคุยอะไรไป แล้วนัดตามอีกครั้งเมื่อไหร่

    ช่อง next_follow_up ไม่ได้อยู่ในตารางนี้ แต่ใส่ไว้ในฟอร์มเดียวกัน
    เพราะตอนบันทึกว่าเพิ่งคุยเสร็จคือจังหวะเดียวที่คนจะจำได้ว่าต้องตามต่อเมื่อไหร่
    ถ้าแยกเป็นสองฟอร์ม จะไม่มีใครกลับมากรอกช่องที่สอง
    """

    next_follow_up = forms.DateField(
        required=False,
        label="ตามอีกครั้งวันที่",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        help_text="เว้นว่าง = ไม่เปลี่ยนจากเดิม",
    )
    clear_follow_up = forms.BooleanField(
        required=False,
        label="ปิดเคสนี้ ไม่ต้องตามต่อ",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = LeadActivity
        fields = ["kind", "note", "occurred_at"]
        widgets = {
            "kind": forms.Select(attrs={"class": "form-select"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3,
                                          "placeholder": "คุยอะไรกัน เขาติดตรงไหน ตกลงอะไรไว้"}),
            "occurred_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"},
                                               format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["occurred_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
        if not self.is_bound:
            self.fields["occurred_at"].initial = timezone.localtime().strftime("%Y-%m-%dT%H:%M")
