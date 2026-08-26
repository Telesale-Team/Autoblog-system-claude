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


# === SEGMENT PROFILE =========================================================
# โปรไฟล์ 5 มิติต่อกลุ่มลูกค้า — แหล่งความจริงเดียวที่ทั้ง agent (LLM) และ
# script Python (Pillow / FLUX) อ่านร่วมกัน
#
# ปัญหาที่แก้: เดิม agent นักเขียนคุมแค่ "โทน" ส่วน skill ทำ diagram เลือกสไตล์จาก
# ประเภทหัวข้อ (concept/steps/comparison) และ skill ทำภาพปกให้คนเรียกเลือก pose เอง
# ทั้งสามอย่างจึงไม่เคยผูกกัน บทความร้านสปาโทนอบอุ่นได้ diagram แข็ง ๆ กับปกท่า serious ได้
#
# ทำไมเก็บใน DB ไม่ใช่ไฟล์: เจ้าของต้องแก้เองได้จากหน้าเว็บโดยไม่ต้อง deploy
# (ต่างจาก dashboard/roadmap.py ที่จงใจเป็นไฟล์เพราะ git hook ต้องตรวจได้)
#
# ⚠️ สีแบรนด์กรม #0F172A + ทอง #C9A84C ห้ามเปลี่ยน — segment ปรับได้แค่สีรอง
# รูปทรง อารมณ์ไอคอน และท่าของหนูดี เท่านั้น

class SegmentProfile(models.Model):

    class Shape(models.TextChoices):
        ROUNDED = "rounded", "มุมโค้ง (อบอุ่น เป็นมิตร)"
        SOFT    = "soft",    "มุมมนน้อย (กลาง ๆ)"
        SHARP   = "sharp",   "มุมเหลี่ยม (จริงจัง เป็นทางการ)"

    class IconMood(models.TextChoices):
        SOFT       = "soft",       "นุ่มนวล"
        CLEAN      = "clean",      "เรียบ สะอาด"
        TECHNICAL  = "technical",  "เทคนิค"
        ENERGETIC  = "energetic",  "มีพลัง"

    class DiagramType(models.TextChoices):
        CONCEPT    = "concept",    "แผนภาพแนวคิด"
        STEPS      = "steps",      "ขั้นตอนเป็นลำดับ"
        COMPARISON = "comparison", "ตารางเปรียบเทียบ"
        STATS      = "stats",      "ตัวเลขและสถิติ"

    class Pose(models.TextChoices):
        THINKING = "thinking", "คิด"
        POINTING = "pointing", "ชี้"
        HAPPY    = "happy",    "ยิ้มสดใส"
        SERIOUS  = "serious",  "จริงจัง"
        READING  = "reading",  "อ่าน"

    class Mood(models.TextChoices):
        TECH  = "tech",  "เทคโนโลยี"
        WARM  = "warm",  "อบอุ่น"
        CLEAN = "clean", "สะอาดตา"
        DARK  = "dark",  "เข้ม"

    # --- ตัวระบุ ---
    key         = models.SlugField("รหัส segment", max_length=50, unique=True,
                                   help_text="เช่น beauty_wellness — script ใช้ค่านี้เรียก")
    name        = models.CharField("ชื่อกลุ่ม", max_length=100)
    agent_slug  = models.CharField("agent ที่รับผิดชอบ", max_length=60,
                                   help_text="slug ใน frontmatter ของไฟล์ agent")
    pen_name    = models.CharField("นามปากกา", max_length=50, blank=True)
    pronoun     = models.CharField("สรรพนามในบทความ", max_length=20, blank=True)

    # --- มิติที่ 1: โทนการเขียน ---
    tone        = models.TextField("โทนการเขียน",
                                   help_text="สรุปสั้น ๆ ว่าเขียนด้วยน้ำเสียงแบบไหน")
    reader      = models.TextField("ผู้อ่านเป็นใคร", blank=True)

    # --- มิติที่ 2: แหล่งค้นข้อมูล ---
    research    = models.TextField("แหล่งค้นข้อมูลและมุมที่ควรหา", blank=True,
                                   help_text="หนึ่งบรรทัดต่อหนึ่งแหล่ง")

    # --- มิติที่ 3: สไตล์ diagram ---
    shape            = models.CharField("รูปทรง", max_length=15, choices=Shape.choices, default=Shape.SOFT)
    accent_secondary = models.CharField("สีรอง (hex)", max_length=7, default="#C9A84C",
                                        help_text="สีหลักกรม+ทองห้ามเปลี่ยน อันนี้คือสีรองเท่านั้น")
    icon_mood        = models.CharField("อารมณ์ไอคอน", max_length=15, choices=IconMood.choices, default=IconMood.CLEAN)
    prefer_diagram   = models.CharField("ชนิด diagram ที่กลุ่มนี้ชอบ", max_length=15,
                                        choices=DiagramType.choices, default=DiagramType.CONCEPT)

    # --- มิติที่ 4: ภาพปก ---
    cover_pose = models.CharField("ท่าของหนูดี", max_length=15, choices=Pose.choices, default=Pose.THINKING)
    cover_mood = models.CharField("อารมณ์พื้นหลัง", max_length=15, choices=Mood.choices, default=Mood.CLEAN)

    # --- มิติที่ 5: รูปแบบ hook ---
    hook_style = models.CharField("รูปแบบ hook", max_length=200, blank=True,
                                  help_text="เช่น คำถามที่ relate ได้ / ตัวเลขที่น่าตกใจ")

    is_active  = models.BooleanField("ใช้งานอยู่", default=True)
    notes      = models.TextField("บันทึกเพิ่มเติม", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Segment Profile"
        verbose_name_plural = "Segment Profiles"
        ordering = ["name"]

    def __str__(self):
        return "%s (%s)" % (self.name, self.key)

    @property
    def research_count(self):
        """จำนวนแหล่งค้นข้อมูลที่ใช้ได้จริง — นับแบบเดียวกับที่ as_dict() ตัด
        ไม่งั้นตัวเลขบนหน้าจอจะไม่ตรงกับสิ่งที่ script ได้ไปจริง"""
        return len([line for line in self.research.splitlines() if line.strip()])

    def as_dict(self):
        """รูปแบบที่ script Pillow/FLUX เอาไปใช้ได้ตรง ๆ

        ตั้งใจให้ชื่อ key ตรงกับ input ที่ SKILL.md ของ auto-diagram-generator
        และ flux-cover-image ประกาศไว้ จะได้เสียบใช้ได้เลยไม่ต้องแปลงอีกชั้น
        """
        return {
            "key": self.key,
            "name": self.name,
            "writer": self.agent_slug,
            "pen_name": self.pen_name,
            "pronoun": self.pronoun,
            "tone": self.tone,
            "reader": self.reader,
            "research": [line.strip() for line in self.research.splitlines() if line.strip()],
            "diagram": {
                "shape": self.shape,
                "accent_secondary": self.accent_secondary,
                "icon_mood": self.icon_mood,
                "prefer_type": self.prefer_diagram,
            },
            "cover": {
                "pose_category": self.cover_pose,
                "background_mood": self.cover_mood,
                "hook_style": self.hook_style,
            },
        }


# === AI-SLOP PATTERN ========================================================
# รายการคำและรูปประโยคที่ทำให้บทความ "อ่านออกว่า AI เขียน"
#
# ที่มาแนวคิด: content-ops/experts/humanizer.md ของ ai-marketing-skills (MIT)
# แต่ของเขาเป็นภาษาอังกฤษล้วน (delve, tapestry, seamless) ใช้กับบทความไทยไม่ได้เลย
# รายการนี้จึงรวบรวมขึ้นใหม่สำหรับภาษาไทยโดยเฉพาะ
#
# ทำไมเก็บใน DB: รายการนี้ต้องโตขึ้นเรื่อย ๆ จากของจริงที่เจอ
# ถ้าฝังในโค้ดหรือใน prompt จะไม่มีใครเพิ่ม เพราะต้องแก้ไฟล์แล้ว deploy

class SlopPattern(models.Model):

    class Kind(models.TextChoices):
        WORD      = "word",      "คำต้องห้าม"
        PHRASE    = "phrase",    "วลีสำเร็จรูป"
        STRUCTURE = "structure", "รูปประโยค/โครงสร้าง"
        CLAIM     = "claim",     "การอ้างลอย ๆ"

    class Severity(models.IntegerChoices):
        LIGHT  = 3,  "เบา (-3)"
        MEDIUM = 5,  "กลาง (-5)"
        HEAVY  = 8,  "หนัก (-8)"
        FATAL  = 10, "ร้ายแรง (-10)"

    pattern     = models.CharField("คำ/วลีที่จับ", max_length=200,
                                   help_text="ข้อความที่ค้นหาตรง ๆ ในบทความ")
    kind        = models.CharField("ชนิด", max_length=15, choices=Kind.choices, default=Kind.PHRASE)
    penalty     = models.IntegerField("คะแนนที่หัก", choices=Severity.choices, default=Severity.MEDIUM)
    why         = models.TextField("ทำไมถึงไม่ดี",
                                   help_text="อธิบายให้นักเขียนเข้าใจ ไม่ใช่แค่บอกว่าห้าม")
    fix         = models.TextField("ควรเขียนแทนว่าอย่างไร", blank=True)
    example_bad = models.TextField("ตัวอย่างที่ไม่ดี", blank=True)
    example_ok  = models.TextField("ตัวอย่างที่แก้แล้ว", blank=True)
    is_active   = models.BooleanField("ใช้งานอยู่", default=True)
    hit_count   = models.IntegerField("เจอมาแล้วกี่ครั้ง", default=0,
                                      help_text="ระบบนับให้เอง ใช้ดูว่าอันไหนเป็นปัญหาจริง")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AI-Slop Pattern"
        verbose_name_plural = "AI-Slop Patterns (ไทย)"
        ordering = ["-penalty", "pattern"]

    def __str__(self):
        return self.pattern


# === CONTENT SCORE ==========================================================
# คะแนนคุณภาพบทความจากคณะกรรมการผู้เชี่ยวชาญ
#
# ที่มาแนวคิด: content-ops/SKILL.md (Expert Panel) ของ ai-marketing-skills
# เก็บ "ทุกรอบ" ไม่ใช่แค่รอบสุดท้าย เพราะเส้นทางการแก้คือของมีค่า
# ถ้าเก็บแค่คะแนนสุดท้ายจะไม่มีใครรู้ว่าแก้อะไรไปบ้างและทำไม

class ContentScore(models.Model):

    class Status(models.TextChoices):
        RUNNING    = "running",    "กำลังให้คะแนน"
        PASSED     = "passed",     "ผ่าน (90+)"
        NEEDS_WORK = "needs_work", "ยังไม่ผ่าน"

    PASS_MARK = 90          # เกณฑ์ผ่าน ตามที่ Expert Panel ต้นทางใช้
    MAX_ROUNDS = 3          # วนแก้ได้สูงสุดกี่รอบ

    article      = models.ForeignKey(Article, on_delete=models.CASCADE,
                                     related_name="scores", verbose_name="บทความ")
    segment      = models.ForeignKey(SegmentProfile, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name="scores",
                                     verbose_name="กลุ่มลูกค้า")
    rubric       = models.CharField("เกณฑ์ที่ใช้", max_length=30, default="content-quality")
    aggregate    = models.IntegerField("คะแนนรวม (ถ่วงน้ำหนักแล้ว)", default=0)
    rounds       = models.IntegerField("จำนวนรอบที่วน", default=0)
    status       = models.CharField("สถานะ", max_length=15,
                                    choices=Status.choices, default=Status.RUNNING)
    panel        = models.TextField("รายชื่อคณะกรรมการ", blank=True,
                                    help_text="หนึ่งบรรทัดต่อหนึ่งคน")
    weaknesses   = models.TextField("จุดอ่อนที่เหลืออยู่", blank=True)
    slop_hits    = models.TextField("AI-slop ที่เจอ", blank=True)
    approved_by  = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="approved_scores", verbose_name="ผู้อนุมัติ")
    approved_at  = models.DateTimeField("อนุมัติเมื่อ", null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Content Score"
        verbose_name_plural = "Content Scores"
        ordering = ["-created_at"]

    def __str__(self):
        return "%s — %s/100" % (self.article.title[:40], self.aggregate)

    @property
    def is_passed(self):
        return self.aggregate >= self.PASS_MARK

    @property
    def is_approved(self):
        """ผ่านเกณฑ์ยังไม่พอ ต้องมีคนกดอนุมัติด้วย

        คะแนนบอกว่า 'ดีพอ' แต่การอนุมัติบอกว่า 'เจ้าของยอมให้เผยแพร่'
        สองอย่างนี้ไม่ใช่เรื่องเดียวกัน
        """
        return self.approved_at is not None

    def recalculate(self):
        """คิดคะแนนรวมใหม่จากกรรมการทุกคนในรอบล่าสุด (ถ่วงน้ำหนักแล้ว)"""
        latest = self.expert_scores.filter(round_no=self.rounds)
        total_weight = sum(e.weight for e in latest)
        if not total_weight:
            self.aggregate = 0
        else:
            self.aggregate = round(
                sum(e.score * e.weight for e in latest) / total_weight)
        self.status = self.Status.PASSED if self.is_passed else self.Status.NEEDS_WORK
        return self.aggregate


class ExpertScore(models.Model):
    """คะแนนรายคนต่อรอบ — ตัวตรวจ AI-slop ถ่วงน้ำหนัก 1.5 เท่าตามต้นทาง"""

    HUMANIZER_WEIGHT = 1.5

    content_score = models.ForeignKey(ContentScore, on_delete=models.CASCADE,
                                      related_name="expert_scores")
    round_no      = models.IntegerField("รอบที่", default=1)
    expert        = models.CharField("ผู้เชี่ยวชาญ", max_length=100)
    lens          = models.CharField("มองจากมุมไหน", max_length=200, blank=True)
    score         = models.IntegerField("คะแนน 0-100", default=0)
    weight        = models.FloatField("น้ำหนัก", default=1.0)
    feedback      = models.TextField("เหตุผล", blank=True)

    class Meta:
        verbose_name = "Expert Score"
        verbose_name_plural = "Expert Scores"
        ordering = ["round_no", "-weight", "expert"]

    def __str__(self):
        return "รอบ %s · %s · %s" % (self.round_no, self.expert, self.score)
