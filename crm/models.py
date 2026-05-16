from django.db import models
from django.utils import timezone
from pages.models import ContactLead


# === CUSTOMER ===

class Customer(models.Model):

    class Tier(models.TextChoices):
        A = "A", "A — Enterprise"
        B = "B", "B — Mid-Market"
        C = "C", "C — SME"

    company_name    = models.CharField("ชื่อบริษัท", max_length=200)
    industry        = models.CharField("อุตสาหกรรม", max_length=100, blank=True)
    tier            = models.CharField("Tier", max_length=1, choices=Tier.choices, default=Tier.C)
    contract_value  = models.DecimalField("มูลค่าสัญญา (บาท)", max_digits=12, decimal_places=2, default=0)
    health_score    = models.IntegerField("Health Score (0-100)", default=80)
    nps_score       = models.IntegerField("NPS Score (-100-100)", default=0)
    contract_start  = models.DateField("วันเริ่มสัญญา", null=True, blank=True)
    contract_end    = models.DateField("วันหมดสัญญา", null=True, blank=True)
    account_owner   = models.CharField("ผู้ดูแลบัญชี", max_length=100, blank=True)
    notes           = models.TextField("บันทึก", blank=True)
    is_active       = models.BooleanField("ใช้งาน", default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ["-created_at"]

    def __str__(self):
        return self.company_name

    @property
    def health_label(self):
        if self.health_score >= 70:
            return "green"
        elif self.health_score >= 40:
            return "yellow"
        return "red"


# === QUOTE ===

class Quote(models.Model):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT  = "sent",  "Sent"
        WON   = "won",   "Won"
        LOST  = "lost",  "Lost"

    quote_number      = models.CharField("เลขที่ใบเสนอราคา", max_length=20, unique=True, blank=True)
    lead              = models.ForeignKey(ContactLead, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Lead", related_name="quotes")
    items             = models.JSONField("รายการสินค้า/บริการ", default=list)
    subtotal          = models.DecimalField("ยอดรวมก่อนภาษี", max_digits=12, decimal_places=2, default=0)
    total             = models.DecimalField("ยอดรวมทั้งหมด", max_digits=12, decimal_places=2, default=0)
    valid_until       = models.DateField("ใบเสนอราคาหมดอายุ")
    status            = models.CharField("สถานะ", max_length=10, choices=Status.choices, default=Status.DRAFT)
    discount_authority = models.BooleanField("ต้องขออนุมัติส่วนลด (>10%)", default=False)
    approved_by       = models.CharField("อนุมัติโดย", max_length=100, blank=True)
    notes             = models.TextField("หมายเหตุ", blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.quote_number or f"Quote #{self.pk}"

    def save(self, *args, **kwargs):
        if not self.quote_number:
            year = timezone.now().year
            last = Quote.objects.filter(quote_number__startswith=f"QT-{year}-").count()
            self.quote_number = f"QT-{year}-{last + 1:04d}"
        super().save(*args, **kwargs)


# === RENEWAL ===

class Renewal(models.Model):

    class Status(models.TextChoices):
        UPCOMING     = "upcoming",      "Upcoming"
        CONTACTED    = "contacted",     "Contacted"
        NEGOTIATING  = "negotiating",   "Negotiating"
        RENEWED      = "renewed",       "Renewed"
        AT_RISK      = "at_risk",       "At Risk"
        CHURNED      = "churned",       "Churned"
        AUTO_RENEWED = "auto_renewed",  "Auto-Renewed"

    customer        = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="ลูกค้า", related_name="renewals")
    renewal_date    = models.DateField("วันต่อสัญญา")
    mrr_value       = models.DecimalField("MRR (บาท)", max_digits=12, decimal_places=2, default=0)
    prev_mrr        = models.DecimalField("MRR เดิม (บาท)", max_digits=12, decimal_places=2, default=0)
    status          = models.CharField("สถานะ", max_length=15, choices=Status.choices, default=Status.UPCOMING)
    assigned_to     = models.CharField("ผู้รับผิดชอบ", max_length=100, blank=True)
    reminder_sent_at = models.DateTimeField("ส่ง Reminder เมื่อ", null=True, blank=True)
    notes           = models.TextField("บันทึก", blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Renewal"
        verbose_name_plural = "Renewals"
        ordering = ["renewal_date"]

    def __str__(self):
        return f"{self.customer.company_name} — {self.renewal_date}"

    @property
    def days_until_renewal(self):
        delta = self.renewal_date - timezone.now().date()
        return delta.days
