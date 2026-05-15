"""
add_calendar_task — เพิ่มงานเข้าตารางงาน calendar

รูปแบบที่ต้องมีครบ (ถ้าขาดจะแจ้งเตือน):
  - ชื่องาน      (required)
  - วันที่|เวลา  --date YYYY-MM-DD  (default: วันนี้)
  - ประเภทงาน   --category <cat>   (default: action)
  - รายละเอียด  --description "..."
  - ผู้ทำงาน    --assigned "ชื่อ"   (default: หนูดี)

Usage:
  python manage.py add_calendar_task "ชื่องาน" --date 2026-05-15 --category action --description "รายละเอียด" --assigned "หนูดี"
"""
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from django.utils import timezone
from dashboard.models import CalendarEvent


REQUIRED_FIELDS = ["title", "date", "category", "description", "assigned_to"]


class Command(BaseCommand):
    help = "เพิ่มงานเข้าตารางงาน calendar — ต้องครบ 5 fields"

    def add_arguments(self, parser):
        parser.add_argument("title",         help="ชื่องาน/หัวข้อ (required)")
        parser.add_argument("--date",        default=None, help="วันที่ YYYY-MM-DD (default: วันนี้)")
        parser.add_argument("--time",        default="00:00", help="เวลา HH:MM (default: 00:00)")
        parser.add_argument(
            "--category",
            default="action",
            choices=[c[0] for c in CalendarEvent.CATEGORY_CHOICES],
            help="ประเภทงาน (default: action)",
        )
        parser.add_argument("--description", default="", help="รายละเอียดงาน (ใช้ | คั่นรายการย่อย)")
        parser.add_argument("--assigned",    default="หนูดี", help="ผู้ทำงาน (default: หนูดี)")

    def handle(self, *args, **options):
        # ── ตรวจสอบ fields ที่ขาด ──────────────────────────────────
        missing = []
        if not options["description"].strip():
            missing.append("รายละเอียด (--description)")
        if not options["assigned"].strip():
            missing.append("ผู้ทำงาน (--assigned)")

        if missing:
            self.stderr.write("ข้อมูลไม่ครบ — ขาด: " + ", ".join(missing))
            return

        # ── วันที่ + เวลา ───────────────────────────────────────────
        date_str = options["date"]
        if date_str:
            d = parse_date(date_str)
            if not d:
                self.stderr.write(f"วันที่ไม่ถูกต้อง: {date_str}")
                return
        else:
            d = timezone.now().date()

        time_str = options["time"]
        try:
            h, m = [int(x) for x in time_str.split(":")]
        except Exception:
            h, m = 0, 0

        all_day = (h == 0 and m == 0)
        start_dt = timezone.make_aware(
            timezone.datetime(d.year, d.month, d.day, h, m, 0)
        )

        # ── สร้าง event ─────────────────────────────────────────────
        evt = CalendarEvent.objects.create(
            title=options["title"],
            start_datetime=start_dt,
            all_day=all_day,
            category=options["category"],
            description=options["description"].strip(),
            assigned_to=options["assigned"].strip(),
            is_system=True,
        )

        self.stdout.write(self.style.SUCCESS(
            f"Added: [{evt.category}] {evt.title} | {d} {time_str} | {evt.assigned_to}"
        ))
