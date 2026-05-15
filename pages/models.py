from django.db import models
from django.utils import timezone
from datetime import timedelta


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
