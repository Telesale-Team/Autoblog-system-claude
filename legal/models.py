from django.db import models
from crm.models import Customer


# === CONTRACT ===

class Contract(models.Model):

    class ContractType(models.TextChoices):
        SERVICE  = "service",  "สัญญาบริการ"
        NDA      = "nda",      "NDA"
        SLA      = "sla",      "SLA"
        RETAINER = "retainer", "Retainer"
        OTHER    = "other",    "อื่นๆ"

    class Status(models.TextChoices):
        DRAFT     = "draft",     "Draft"
        ACTIVE    = "active",    "Active"
        EXPIRING  = "expiring",  "กำลังหมดอายุ"
        EXPIRED   = "expired",   "หมดอายุ"
        CANCELLED = "cancelled", "Cancelled"

    title          = models.CharField("ชื่อสัญญา", max_length=300)
    customer       = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="ลูกค้า", related_name="contracts")
    contract_type  = models.CharField("ประเภทสัญญา", max_length=10, choices=ContractType.choices, default=ContractType.SERVICE)
    start_date     = models.DateField("วันเริ่มสัญญา")
    end_date       = models.DateField("วันหมดสัญญา")
    value          = models.DecimalField("มูลค่าสัญญา (บาท)", max_digits=12, decimal_places=2, default=0)
    file           = models.FileField("ไฟล์สัญญา", upload_to="contracts/%Y/", null=True, blank=True)
    pdpa_compliant = models.BooleanField("ผ่าน PDPA Checklist", default=False)
    status         = models.CharField("สถานะ", max_length=10, choices=Status.choices, default=Status.DRAFT)
    notes          = models.TextField("บันทึก", blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contract"
        verbose_name_plural = "Contracts"
        ordering = ["end_date"]

    def __str__(self):
        return f"{self.title} — {self.customer.company_name}"

    @property
    def days_until_expiry(self):
        from django.utils import timezone
        return (self.end_date - timezone.now().date()).days
