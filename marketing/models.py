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



# === CONTENT BACKLOG ===

class ContentBacklog(models.Model):

    class Priority(models.TextChoices):
        HIGH   = "P1", "P1 — High"
        MEDIUM = "P2", "P2 — Medium"
        LOW    = "P3", "P3 — Low"

    class Status(models.TextChoices):
        PENDING     = "pending",     "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW      = "review",      "Review"
        DONE        = "done",        "Done"

    class AssignedAgent(models.TextChoices):
        CONTENT_WRITER   = "content-writer-th",       "Content Writer TH (ทั่วไป)"
        HEALTHCARE       = "healthcare-writer",        "Healthcare Writer (คลินิก/โรงพยาบาล)"
        ECOMMERCE        = "ecommerce-writer",         "E-commerce Writer (ร้านค้าออนไลน์)"
        HOSPITALITY      = "hospitality-writer",       "Hospitality Writer (โรงแรม/รีสอร์ท)"
        BEAUTY           = "beauty-wellness-writer",   "Beauty & Wellness Writer (สปา/นวด)"
        HR_EDUCATION     = "hr-education-writer",      "HR & Education Writer (HR/โรงเรียน)"
        CREATOR_COACH    = "creator-coach-writer",     "Creator & Coach Writer (โค้ช/ครีเอเตอร์)"
        AI_NEWS_SCOUT    = "ai-news-scout",            "AI News Scout (ข่าว AI)"
        MARKETING        = "marketing-specialist",     "Marketing Specialist"
        SEO              = "seo-specialist",           "SEO Specialist"

    num      = models.IntegerField("ลำดับ", default=0)
    topic    = models.CharField("หัวข้อ", max_length=400)
    keyword  = models.CharField("Target Keyword", max_length=300, blank=True)
    priority = models.CharField("Priority", max_length=2, choices=Priority.choices, default=Priority.HIGH)
    status   = models.CharField("Status", max_length=15, choices=Status.choices, default=Status.PENDING)
    assigned_agent = models.CharField(
        "AI ส่งงาน", max_length=50,
        choices=AssignedAgent.choices,
        default=AssignedAgent.CONTENT_WRITER,
        blank=True
    )
    writer = models.ForeignKey(
        "auth.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="backlog_items",
        verbose_name="นักเขียน"
    )
    notes    = models.TextField("Notes", blank=True)
    category = models.ForeignKey(
        "blog.Category", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="backlog_items",
        verbose_name="หมวดหมู่บทความ"
    )
    calendar_event = models.OneToOneField(
        "dashboard.CalendarEvent", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="backlog_item",
        verbose_name="Calendar Event"
    )
    owner    = models.CharField("Owner", max_length=100, blank=True, default="All")
    added_by = models.CharField("เพิ่มโดย", max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # keywords → category_id (เรียงจาก specific → general)
    TOPIC_CATEGORY_KEYWORDS = [
        (12, ["โค้ช", "ครูออนไลน์", "สอนออนไลน์", "content creator", "personal brand", "freelancer", "อาจารย์ออนไลน์"]),
        (7,  ["คลินิก", "โรงพยาบาล", "แพทย์", "สุขภาพ", "ผู้ป่วย", "การแพทย์", "พยาบาล", "healthcare", "medical"]),
        (9,  ["โรงแรม", "รีสอร์ท", "ที่พัก", "ห้องพัก", "ota", "ท่องเที่ยว", "hotel", "resort", "hospitality"]),
        (10, ["ร้านนวด", "สปาไทย", "นวดแผน", "คลินิกความงาม", "wellness", "beauty clinic", "สปา "]),
        (11, ["hr ", " hr", "แรงงาน", "upskill", "resume", "โรงเรียน", "edtech", "มหาวิทยาลัย", "สมัครงาน", "บุคลากร"]),
        (8,  ["shopee", "lazada", "ร้านค้าออนไลน์", "ขายของออนไลน์", "line shopping", "ecommerce", "e-commerce"]),
        (2,  ["gpt", "chatgpt", "claude", "gemini", "llama", "mistral", "grok", "openai", "anthropic",
              "google ai", "meta ai", "xai", "ai model", "โมเดล ai", "flux.1", "midjourney"]),
    ]

    @classmethod
    def detect_category_id(cls, topic: str) -> int:
        """ตรวจ keyword ใน topic → คืน category_id ที่เหมาะสม (default=1 Educational)"""
        text = topic.lower()
        for cat_id, keywords in cls.TOPIC_CATEGORY_KEYWORDS:
            if any(kw in text for kw in keywords):
                return cat_id
        return 1  # default: Educational

    # category_id → writer user_id (primary — ข่าวเรื่องไหนใครเขียน)
    CATEGORY_WRITER_MAP = {
        1:  2,   # Educational       → dphoompat
        2:  2,   # Industry Insight  → dphoompat
        3:  2,   # Case Study        → dphoompat
        4:  2,   # Behind the Scenes → dphoompat
        5:  2,   # Openclaw          → dphoompat
        7:  3,   # Healthcare        → กนกวดี
        8:  4,   # E-Commerce        → วริญญา
        9:  5,   # Hospitality       → ปิยดา
        10: 6,   # Beauty & Wellness → มินตรา
        11: 7,   # HR & Education    → ณัฐวุฒิ
        12: 8,   # Creator & Coach   → ธีรพงษ์
    }

    # agent → category_id (ใช้เมื่อยังไม่มี category)
    AGENT_CATEGORY_MAP = {
        "content-writer-th":      1,
        "healthcare-writer":      7,
        "ecommerce-writer":       8,
        "hospitality-writer":     9,
        "beauty-wellness-writer": 10,
        "hr-education-writer":    11,
        "creator-coach-writer":   12,
        "ai-news-scout":          2,
        "marketing-specialist":   2,
        "seo-specialist":         1,
    }

    def save(self, *args, **kwargs):
        # 1. detect category จาก topic keyword (ถ้ายังไม่มี)
        if not self.category_id and self.topic:
            self.category_id = self.detect_category_id(self.topic)
        # 2. fill category จาก agent (fallback ถ้า detect ไม่ได้)
        if not self.category_id and self.assigned_agent in self.AGENT_CATEGORY_MAP:
            self.category_id = self.AGENT_CATEGORY_MAP[self.assigned_agent]
        # 3. fill writer จาก category เสมอ
        if self.category_id and self.category_id in self.CATEGORY_WRITER_MAP:
            self.writer_id = self.CATEGORY_WRITER_MAP[self.category_id]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Content Backlog"
        verbose_name_plural = "Content Backlog"
        ordering = ["num"]

    def __str__(self):
        return f"#{self.num} {self.topic[:60]}"


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
