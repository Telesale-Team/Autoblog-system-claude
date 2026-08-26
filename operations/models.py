from django.db import models
from crm.models import Customer


# === AI PROJECT ===

class AIProject(models.Model):

    class Status(models.TextChoices):
        SCOPING = "scoping", "Scoping"
        DEV     = "dev",     "Development"
        TESTING = "testing", "Testing"
        LIVE    = "live",    "Live"
        PAUSED  = "paused",  "Paused"
        CLOSED  = "closed",  "Closed"

    project_name = models.CharField("ชื่อโปรเจกต์", max_length=200)
    customer     = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ลูกค้า", related_name="ai_projects")
    service      = models.ForeignKey("pages.Service", on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name="บริการที่ขาย", related_name="projects",
                                     help_text="ผูกกับบริการบนเว็บ ใช้จัดกลุ่มในหน้า Project Monitor")
    tech_stack   = models.JSONField("Tech Stack", default=list)
    status       = models.CharField("สถานะ", max_length=10, choices=Status.choices, default=Status.SCOPING)
    go_live_date = models.DateField("วัน Go-Live", null=True, blank=True)
    monthly_fee  = models.DecimalField("ค่าบริการรายเดือน (บาท)", max_digits=12, decimal_places=2, default=0)
    description  = models.TextField("รายละเอียด", blank=True)
    is_active    = models.BooleanField("ใช้งาน", default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Project"
        verbose_name_plural = "AI Projects"
        ordering = ["-created_at"]

    def __str__(self):
        return self.project_name


# === PROMPT LIBRARY ===

class PromptLibrary(models.Model):

    class Rating(models.TextChoices):
        GOOD       = "good",       "ดีมาก"
        OK         = "ok",         "พอใช้"
        NEEDS_WORK = "needs_work", "ควรปรับปรุง"

    AGENT_CHOICES = [
        ("chief-of-staff",       "Chief of Staff"),
        ("hustler-sales",        "Hustler (Sales)"),
        ("ai-orchestrator",      "AI Orchestrator"),
        ("money-manager",        "Money Manager"),
        ("ai-toolsmith",         "AI Toolsmith"),
        ("qa-agent",             "QA Agent"),
        ("marketing-specialist", "Marketing Specialist"),
        ("customer-success",     "Customer Success"),
        ("data-analyst",         "Data Analyst"),
        ("legal-advisor",        "Legal Advisor"),
        ("seo-specialist",       "SEO Specialist"),
        ("content-writer-th",    "Content Writer (TH)"),
        ("frontend-designer",    "Frontend Designer"),
    ]

    title       = models.CharField("ชื่อ Prompt", max_length=200)
    agent       = models.CharField("Agent", max_length=30, choices=AGENT_CHOICES)
    use_case    = models.CharField("Use Case", max_length=200)
    prompt_text = models.TextField("Prompt")
    tags        = models.JSONField("Tags", default=list)
    version     = models.IntegerField("Version", default=1)
    rating      = models.CharField("Rating", max_length=12, choices=Rating.choices, default=Rating.OK)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Prompt"
        verbose_name_plural = "Prompt Library"
        ordering = ["agent", "use_case"]

    def __str__(self):
        return f"[{self.agent}] {self.title} v{self.version}"


# === QA LOG ===

class QALog(models.Model):

    class Result(models.TextChoices):
        PASS    = "pass",    "Pass"
        FAIL    = "fail",    "Fail"
        PARTIAL = "partial", "Partial"
        BLOCKED = "blocked", "Blocked"

    class IssueCategory(models.TextChoices):
        FUNCTIONAL  = "functional",  "Functional"
        SECURITY    = "security",    "Security"
        UI_UX       = "ui_ux",       "UI/UX"
        DATA        = "data",        "Data"
        PERFORMANCE = "performance", "Performance"
        COMPLIANCE  = "compliance",  "Compliance"

    class Severity(models.TextChoices):
        CRITICAL = "critical", "Critical"
        MAJOR    = "major",    "Major"
        MINOR    = "minor",    "Minor"
        COSMETIC = "cosmetic", "Cosmetic"

    AGENT_CHOICES = [
        ("chief-of-staff",       "Chief of Staff"),
        ("hustler-sales",        "Hustler (Sales)"),
        ("ai-orchestrator",      "AI Orchestrator"),
        ("money-manager",        "Money Manager"),
        ("ai-toolsmith",         "AI Toolsmith"),
        ("marketing-specialist", "Marketing Specialist"),
        ("customer-success",     "Customer Success"),
        ("data-analyst",         "Data Analyst"),
        ("legal-advisor",        "Legal Advisor"),
        ("seo-specialist",       "SEO Specialist"),
        ("content-writer-th",    "Content Writer (TH)"),
        ("frontend-designer",    "Frontend Designer"),
    ]

    output_type    = models.CharField("ประเภท Output", max_length=100)
    agent          = models.CharField("Agent", max_length=30, choices=AGENT_CHOICES)
    result         = models.CharField("ผลการ QA", max_length=10, choices=Result.choices)
    issue_category = models.CharField("หมวดปัญหา", max_length=15, choices=IssueCategory.choices, null=True, blank=True)
    severity       = models.CharField("ความรุนแรง", max_length=10, choices=Severity.choices, null=True, blank=True)
    notes          = models.TextField("บันทึก / รายละเอียดปัญหา", blank=True)
    reviewed_at    = models.DateTimeField("ตรวจสอบเมื่อ", null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "QA Log"
        verbose_name_plural = "QA Logs"
        ordering = ["-reviewed_at"]

    def __str__(self):
        return f"[{self.get_result_display()}] {self.agent} — {self.output_type}"


# === DEPLOYMENT — instance ของระบบที่รันอยู่จริงบน server ===

class Deployment(models.Model):
    """หนึ่ง AIProject มีได้หลาย Deployment (prod / staging / dev)

    ทะเบียนนี้เก็บข้อมูลที่เดิมอยู่แค่ในไฟล์ memory ของ AI —
    server ไหน path อะไร service ชื่ออะไร domain อะไร
    """

    class Environment(models.TextChoices):
        PRODUCTION = "production", "Production"
        STAGING    = "staging",    "Staging"
        DEV        = "dev",        "Development"

    project        = models.ForeignKey(AIProject, on_delete=models.CASCADE,
                                       verbose_name="โปรเจกต์", related_name="deployments")
    name           = models.CharField("ชื่อ Instance", max_length=120,
                                      help_text="เช่น QueueFlow Demo, Bergen Production")
    environment    = models.CharField("Environment", max_length=12,
                                      choices=Environment.choices, default=Environment.PRODUCTION)

    # ── ที่อยู่บน server ──
    server_host    = models.CharField("Server / IP", max_length=100, blank=True)
    project_path   = models.CharField("Path บน server", max_length=255, blank=True)
    service_name   = models.CharField("systemd service", max_length=100, blank=True)
    base_url       = models.URLField("URL หลัก", max_length=300, blank=True,
                                     help_text="เว้นว่างได้ถ้ายังไม่ผูก domain — จะข้ามการเช็ค")

    # ── source code ──
    repo_url       = models.URLField("Git repo", max_length=300, blank=True)
    branch         = models.CharField("Branch", max_length=80, blank=True, default="main")

    # ── การตรวจสุขภาพ ──
    is_monitored   = models.BooleanField("เปิดการเฝ้าดู", default=True)
    health_path    = models.CharField("Path สำหรับเช็คว่ามีชีวิต", max_length=200, default="/",
                                      help_text="ยิง GET ไปที่ base_url + path นี้")
    monitor_path   = models.CharField("Path API ตัวเลขธุรกิจ", max_length=200, blank=True,
                                      help_text="เช่น /api/monitor/ — เว้นว่างถ้าระบบยังไม่รองรับ")
    monitor_token  = models.CharField("Bearer token", max_length=255, blank=True)

    # ── ธง ──
    is_critical    = models.BooleanField("ระบบลูกค้าจริง (ห้ามแตะข้อมูล)", default=False)
    is_internal    = models.BooleanField("ระบบภายในของเราเอง", default=False)

    monthly_fee    = models.DecimalField("ค่าดูแล/เดือน (บาท)", max_digits=12, decimal_places=2, default=0)
    notes          = models.TextField("บันทึก", blank=True)

    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Deployment"
        verbose_name_plural = "Deployments"
        ordering = ["project__project_name", "environment", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_environment_display()})"

    # ── helper ──

    @property
    def check_url(self):
        if not self.base_url:
            return ""
        return self.base_url.rstrip("/") + "/" + self.health_path.lstrip("/")

    @property
    def monitor_url(self):
        if not self.base_url or not self.monitor_path:
            return ""
        return self.base_url.rstrip("/") + "/" + self.monitor_path.lstrip("/")

    @property
    def latest_check(self):
        return self.checks.order_by("-checked_at").first()

    @property
    def state(self):
        """up / down / idle — ใช้เลือกสีจุดบนการ์ด"""
        if not self.is_monitored or not self.base_url:
            return "idle"
        last = self.latest_check
        if last is None:
            return "idle"
        return "up" if last.is_up else "down"

    @property
    def recent_states(self):
        """ผลตรวจ 30 ครั้งล่าสุด เรียงเก่า→ใหม่ ใช้วาดแถบ timeline"""
        rows = list(self.checks.all())[:30]
        return [c.is_up for c in reversed(rows)]

    def uptime_pct(self, days=30):
        from django.utils import timezone
        from datetime import timedelta
        since = timezone.now() - timedelta(days=days)
        qs = self.checks.filter(checked_at__gte=since)
        total = qs.count()
        if not total:
            return None
        return round(qs.filter(is_up=True).count() * 100.0 / total, 1)


# === HEALTH CHECK — ผลตรวจแต่ละครั้ง ===

class HealthCheck(models.Model):

    deployment    = models.ForeignKey(Deployment, on_delete=models.CASCADE,
                                      verbose_name="Deployment", related_name="checks")
    checked_at    = models.DateTimeField("ตรวจเมื่อ", auto_now_add=True, db_index=True)
    is_up         = models.BooleanField("ขึ้นอยู่", default=False)
    status_code   = models.IntegerField("HTTP status", null=True, blank=True)
    response_ms   = models.IntegerField("เวลาตอบสนอง (ms)", null=True, blank=True)
    error         = models.TextField("ข้อผิดพลาด", blank=True)

    # ── ข้อมูลจาก /api/monitor/ (ถ้าระบบปลายทางรองรับ) ──
    version       = models.CharField("เวอร์ชัน / commit", max_length=80, blank=True)
    deployed_at   = models.DateTimeField("deploy เมื่อ", null=True, blank=True)
    metrics       = models.JSONField("ตัวเลขธุรกิจ", default=list, blank=True,
                                     help_text='[{"key","label","value","unit","alert"}]')

    class Meta:
        verbose_name = "Health Check"
        verbose_name_plural = "Health Checks"
        ordering = ["-checked_at"]
        indexes = [models.Index(fields=["deployment", "-checked_at"])]

    def __str__(self):
        mark = "UP" if self.is_up else "DOWN"
        return f"[{mark}] {self.deployment.name} — {self.checked_at:%Y-%m-%d %H:%M}"
