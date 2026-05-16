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
