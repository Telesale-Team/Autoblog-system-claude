from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CalendarEvent(models.Model):
    CATEGORY_CHOICES = [
        # User-created events
        ("general",      "ทั่วไป"),
        ("priority",     "งานสำคัญ"),
        ("meeting",      "ประชุม"),
        ("delivery",     "ส่งมอบงาน"),
        ("personal",     "ส่วนตัว"),
        # System events (is_system=True)
        ("milestone",    "Milestone / แผน"),
        ("action",       "งานต้องทำ (Task)"),
        ("recurring",    "Recurring / นัดประจำ"),
        ("content_plan", "Content Plan"),
        ("backlog",      "Content Backlog"),
    ]

    title          = models.CharField("หัวข้อ", max_length=200)
    start_datetime = models.DateTimeField("วันเริ่ม")
    end_datetime   = models.DateTimeField("วันสิ้นสุด", null=True, blank=True)
    all_day        = models.BooleanField("ทั้งวัน", default=True)
    category       = models.CharField("ประเภท", max_length=50, choices=CATEGORY_CHOICES, default="general")
    description    = models.TextField("รายละเอียด", blank=True)
    color          = models.CharField("สี", max_length=7, blank=True)
    is_system      = models.BooleanField("event ระบบ", default=False)
    is_completed   = models.BooleanField("เสร็จแล้ว", default=False)
    assigned_to    = models.CharField("ผู้ทำงาน", max_length=100, blank=True, default="")
    created_by     = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_datetime"]
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"

    def __str__(self):
        return self.title

    def to_fc(self):
        return {
            "id":          self.pk,
            "title":       self.title,
            "start":       self.start_datetime.isoformat(),
            "end":         self.end_datetime.isoformat() if self.end_datetime else None,
            "allDay":      self.all_day,
            "color":       self.color or self._default_color(),
            "extendedProps": {
                "category":    self.category,
                "description": self.description,
                "isSystem":    self.is_system,
                "isCompleted": self.is_completed,
                "assignedTo":  self.assigned_to,
            },
        }

    def _default_color(self):
        return {
            "general":  "#2563eb",
            "priority": "#c9a96e",
            "meeting":  "#7c3aed",
            "delivery": "#059669",
            "personal": "#64748b",
        }.get(self.category, "#1a2744")



# === NOTE ===

class Note(models.Model):

    class Color(models.TextChoices):
        GOLD   = "gold",   "Gold"
        BLUE   = "blue",   "Blue"
        GREEN  = "green",  "Green"
        RED    = "red",    "Red"
        PURPLE = "purple", "Purple"

    title      = models.CharField("หัวข้อ", max_length=200)
    content    = models.TextField("เนื้อหา", blank=True)
    color      = models.CharField("สี", max_length=10, choices=Color.choices, default=Color.GOLD)
    pinned     = models.BooleanField("ปักหมุด", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ["-pinned", "-updated_at"]

    def __str__(self):
        return self.title
