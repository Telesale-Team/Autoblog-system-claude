from django.db import models
from blog.models import Article


# === CAMPAIGN ===

class Campaign(models.Model):

    class Channel(models.TextChoices):
        FACEBOOK = "facebook", "Facebook"
        LINE     = "line",     "LINE"
        EMAIL    = "email",    "Email"
        GOOGLE   = "google",   "Google Ads"
        LINKEDIN = "linkedin", "LinkedIn"
        TIKTOK   = "tiktok",   "TikTok"
        ORGANIC  = "organic",  "Organic"
        BLOG     = "blog",     "Blog"
        YOUTUBE  = "youtube",  "YouTube"
        OTHER    = "other",    "อื่นๆ"

    class Status(models.TextChoices):
        DRAFT     = "draft",     "Draft"
        ACTIVE    = "active",    "Active"
        PAUSED    = "paused",    "Paused"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    name         = models.CharField("ชื่อ Campaign", max_length=200)
    channel      = models.CharField("ช่องทาง", max_length=15, choices=Channel.choices)
    budget       = models.DecimalField("งบประมาณ (บาท)", max_digits=12, decimal_places=2, default=0)
    start_date   = models.DateField("วันเริ่ม")
    end_date     = models.DateField("วันสิ้นสุด", null=True, blank=True)
    kpi_leads    = models.IntegerField("เป้า Leads", default=0)
    actual_leads = models.IntegerField("Leads จริง", default=0)
    status       = models.CharField("สถานะ", max_length=10, choices=Status.choices, default=Status.DRAFT)
    notes        = models.TextField("หมายเหตุ", blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.get_channel_display()})"

    @property
    def achievement_pct(self):
        if self.kpi_leads:
            return round(self.actual_leads / self.kpi_leads * 100, 1)
        return 0



# === KEYWORD ===

class Keyword(models.Model):

    class Intent(models.TextChoices):
        INFORMATIONAL = "info",       "Informational (ข้อมูล)"
        TRANSACTIONAL = "trans",      "Transactional (ซื้อ)"
        NAVIGATIONAL  = "nav",        "Navigational (หาเว็บ)"
        COMMERCIAL    = "commercial", "Commercial (เปรียบเทียบ/ราคา)"

    keyword           = models.CharField("Keyword", max_length=200)
    search_volume     = models.IntegerField("Search Volume/เดือน", default=0)
    difficulty        = models.IntegerField("Keyword Difficulty (0-100)", default=0)
    intent            = models.CharField("Search Intent", max_length=15, choices=Intent.choices, default=Intent.INFORMATIONAL)
    current_rank      = models.IntegerField("Rank ปัจจุบัน", null=True, blank=True)
    target_position   = models.IntegerField("เป้า Rank", null=True, blank=True)
    last_checked_date = models.DateField("ตรวจสอบล่าสุด", null=True, blank=True)
    article           = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="บทความที่ target", related_name="keywords")
    notes             = models.TextField("บันทึก / Brief", blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"
        ordering = ["current_rank"]

    def __str__(self):
        return self.keyword
