from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class SiteSetting(models.Model):
    contact_email  = models.EmailField("อีเมลติดต่อ", default="dphoompat.pjs@gmail.com")
    line_id        = models.CharField("LINE ID", max_length=100, default="@aibizthailand")
    phone          = models.CharField("เบอร์โทร", max_length=30, blank=True)
    business_hours = models.CharField("เวลาทำการ", max_length=100, default="จ–ศ 09:00–18:00")

    class Meta:
        verbose_name = "ตั้งค่าเว็บไซต์"
        verbose_name_plural = "ตั้งค่าเว็บไซต์"

    def __str__(self):
        return "ตั้งค่าเว็บไซต์"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutStat(models.Model):
    number = models.CharField("ตัวเลข", max_length=20, help_text="เช่น 20+, 3 ปี+")
    label  = models.CharField("คำอธิบาย", max_length=60, help_text="เช่น ลูกค้า SME ที่ใช้จริง")
    order  = models.IntegerField("ลำดับ", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "สถิติ (About)"
        verbose_name_plural = "สถิติ (About)"

    def __str__(self):
        return f"{self.number} {self.label}"


class AboutValue(models.Model):
    icon        = models.CharField("Bootstrap Icon", max_length=60, default="bi-check-circle",
                                   help_text="เช่น bi-bar-chart-line-fill, bi-building-check")
    title       = models.CharField("หัวข้อ", max_length=100)
    description = models.TextField("รายละเอียด")
    order       = models.IntegerField("ลำดับ", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "ค่านิยม (About)"
        verbose_name_plural = "ค่านิยม (About)"

    def __str__(self):
        return self.title


class Service(models.Model):
    name = models.CharField("ชื่อบริการ", max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    tagline = models.CharField("Tagline สั้น", max_length=160)
    description = models.TextField("รายละเอียด")
    icon = models.CharField("Bootstrap Icon class", max_length=60, default="bi-stars",
                            help_text="เช่น bi-robot, bi-graph-up-arrow")
    cover_image_url = models.URLField("รูปปก (URL)", max_length=500, blank=True,
                                      help_text="Unsplash หรือ CDN URL สำหรับรูปหน้าการ์ด")
    price_start = models.PositiveIntegerField("ราคาเริ่มต้น (บาท)", default=0)
    price_label = models.CharField("Label ราคา", max_length=60, default="เริ่มต้น",
                                   help_text="เช่น 'เริ่มต้น', 'ต่อเดือน', 'ต่อโปรเจกต์'")
    features = models.TextField("Features (แต่ละบรรทัด = 1 feature)")
    is_featured = models.BooleanField("เด่น", default=False)
    display_order = models.IntegerField("ลำดับ", default=0)
    status = models.CharField(max_length=20,
                              choices=[("published", "Published"), ("draft", "Draft")],
                              default="published")

    class Meta:
        ordering = ["display_order"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name

    def get_feature_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class ContactLead(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("qualified", "Qualified"),
        ("proposal", "Proposal"),
        ("closed_won", "Closed - Won"),
        ("closed_lost", "Closed - Lost"),
    ]

    SOURCE_CHOICES = [
        ("landing", "Landing Page"),
        ("blog", "Blog"),
        ("portfolio", "Portfolio"),
        ("other", "Other"),
    ]

    name = models.CharField("ชื่อ-สกุล", max_length=100)
    email = models.EmailField("อีเมล")
    phone = models.CharField("เบอร์โทร", max_length=20, blank=True)
    company = models.CharField("บริษัท", max_length=100, blank=True)
    message = models.TextField("ข้อความ")

    source = models.CharField("ที่มา", max_length=20, choices=SOURCE_CHOICES, default="landing")
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)

    status = models.CharField("สถานะ", max_length=20, choices=STATUS_CHOICES, default="new")
    deal_value = models.DecimalField("มูลค่าดีล (บาท)", max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField("บันทึกภายใน", blank=True)

    # PDPA
    consent_given = models.BooleanField("ยินยอม PDPA", default=False)
    consent_text = models.TextField("ข้อความ consent ที่แสดง", blank=True)
    consent_given_at = models.DateTimeField("ยินยอมเมื่อ", null=True, blank=True)
    ip_address = models.GenericIPAddressField("IP", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deletable_after = models.DateTimeField("ลบได้หลัง", null=True, blank=True)

    class Meta:
        verbose_name = "Contact Lead"
        verbose_name_plural = "Contact Leads"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"

    def save(self, *args, **kwargs):
        if self.consent_given and not self.consent_given_at:
            self.consent_given_at = timezone.now()
            self.deletable_after = timezone.now() + timedelta(days=730)  # 24 months
        super().save(*args, **kwargs)
