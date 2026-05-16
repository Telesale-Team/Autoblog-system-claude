from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from crm.models import Customer


# === INVOICE ===

class Invoice(models.Model):

    class Status(models.TextChoices):
        DRAFT     = "draft",     "Draft"
        SENT      = "sent",      "Sent"
        PARTIAL   = "partial",   "Partial"
        PAID      = "paid",      "Paid"
        OVERDUE   = "overdue",   "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    class WHTRate(models.TextChoices):
        ZERO    = "0",  "0%"
        ONE     = "1",  "1% (ขายสินค้า)"
        THREE   = "3",  "3% (บริการ)"
        FIVE    = "5",  "5%"
        FIFTEEN = "15", "15%"

    class PaymentMethod(models.TextChoices):
        TRANSFER = "transfer", "โอนเงิน"
        CHEQUE   = "cheque",   "เช็ค"
        CASH     = "cash",     "เงินสด"
        OTHER    = "other",    "อื่นๆ"

    invoice_number      = models.CharField("เลขที่ใบแจ้งหนี้", max_length=20, unique=True, blank=True)
    customer            = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="ลูกค้า", related_name="invoices")
    service_description = models.TextField("รายละเอียดบริการ", blank=True)
    subtotal            = models.DecimalField("ยอดก่อนภาษี", max_digits=12, decimal_places=2, default=0)
    vat                 = models.DecimalField("VAT 7%", max_digits=12, decimal_places=2, default=0)
    wht_rate            = models.CharField("อัตรา WHT", max_length=2, choices=WHTRate.choices, default=WHTRate.THREE)
    wht                 = models.DecimalField("หัก ณ ที่จ่าย", max_digits=12, decimal_places=2, default=0)
    total_payable       = models.DecimalField("ยอดที่ต้องชำระ", max_digits=12, decimal_places=2, default=0)
    issue_date          = models.DateField("วันที่ออกใบแจ้งหนี้", default=timezone.now)
    due_date            = models.DateField("วันครบกำหนด")
    paid_at             = models.DateTimeField("ชำระเมื่อ", null=True, blank=True)
    payment_method      = models.CharField("ช่องทางชำระ", max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.TRANSFER)
    withholding_cert_no = models.CharField("เลขที่ใบหัก ณ ที่จ่าย", max_length=50, blank=True)
    is_vat_registered   = models.BooleanField("ลูกค้าจด VAT", default=True)
    status              = models.CharField("สถานะ", max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ["-issue_date"]

    def __str__(self):
        return self.invoice_number or f"Invoice #{self.pk}"

    def clean(self):
        if self.due_date and self.issue_date and self.due_date < self.issue_date:
            raise ValidationError({"due_date": "วันครบกำหนดต้องไม่ก่อนวันที่ออกใบ"})
        if self.paid_at and self.status not in (self.Status.PAID, self.Status.PARTIAL):
            raise ValidationError({"paid_at": "ระบุวันชำระได้เฉพาะสถานะ Paid หรือ Partial"})

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = timezone.now().year
            last = Invoice.objects.filter(invoice_number__startswith=f"INV-{year}-").count()
            self.invoice_number = f"INV-{year}-{last + 1:04d}"
        self.vat = self.subtotal * 7 / 100
        wht_pct = int(self.wht_rate) if self.wht_rate else 0
        self.wht = self.subtotal * wht_pct / 100
        self.total_payable = self.subtotal + self.vat - self.wht
        super().save(*args, **kwargs)


# === EXPENSE ===

class Expense(models.Model):

    class Category(models.TextChoices):
        MARKETING         = "marketing",         "การตลาด / โฆษณา"
        TOOLS_SOFTWARE    = "tools_software",    "เครื่องมือ / Software"
        HOSTING_INFRA     = "hosting_infra",     "Hosting / Infrastructure"
        LLM_API           = "llm_api",           "LLM API (OpenAI, Claude ฯลฯ)"
        SALARY_PAYROLL    = "salary_payroll",    "เงินเดือน / ค่าจ้าง"
        OFFICE_SUPPLIES   = "office_supplies",   "เครื่องเขียน / อุปกรณ์สำนักงาน"
        PROFESSIONAL_FEES = "professional_fees", "ค่าที่ปรึกษา / วิชาชีพ"
        TRAVEL            = "travel",            "เดินทาง"
        BANK_FEES         = "bank_fees",         "ค่าธรรมเนียมธนาคาร"
        TAX_ACCOUNTING    = "tax_accounting",    "ภาษี / บัญชี"
        HARDWARE          = "hardware",          "Hardware / อุปกรณ์"
        OTHER             = "other",             "อื่นๆ"

    class PaymentMethod(models.TextChoices):
        TRANSFER = "transfer", "โอนเงิน"
        CASH     = "cash",     "เงินสด"
        CREDIT   = "credit",   "บัตรเครดิต"
        OTHER    = "other",    "อื่นๆ"

    date           = models.DateField("วันที่")
    category       = models.CharField("หมวดหมู่", max_length=20, choices=Category.choices)
    amount         = models.DecimalField("จำนวนเงิน (บาท)", max_digits=12, decimal_places=2)
    description    = models.CharField("รายละเอียด", max_length=300)
    vendor_name    = models.CharField("ชื่อผู้ขาย/ผู้รับเงิน", max_length=200, blank=True)
    is_deductible  = models.BooleanField("หักภาษีได้", default=True)
    tax_invoice_no = models.CharField("เลขที่ใบกำกับภาษี", max_length=50, blank=True)
    payment_method = models.CharField("ช่องทางชำระ", max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.TRANSFER)
    receipt        = models.FileField("สลิป/ใบเสร็จ", upload_to="expenses/%Y/%m/", null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} — {self.get_category_display()} — {self.amount:,.0f} บาท"
