# -*- coding: utf-8 -*-
r"""บันทึกงานคอร์ส Python 101 ลง Calendar DB (ห้ามใส่ emoji ใน title)"""
import os, sys, django
from datetime import datetime, timedelta

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from django.utils import timezone
from dashboard.models import CalendarEvent
from blog.models import Article

ep0 = Article.objects.filter(slug="python-101-ep0").first()
today = timezone.localtime().date()

rows = [
    # (title, offset_days, category, description, is_completed, article)
    ("สร้าง Category Python สำหรับคนเริ่มต้น + เขียน EP0 ปฐมนิเทศคอร์ส", 0, "article",
     "Category slug=python-101 / Article #43 slug=python-101-ep0 layout=docs status=draft "
     "รอเจ้าของตรวจแล้วกด publish เอง", True, ep0),
    ("รอ CEO ตรวจ EP0 แล้วตัดสินใจ ระบบ Series/EP บนเว็บ", 1, "action",
     "ตัวเลือก A: สร้าง Series model + episode_no (ได้หน้าสารบัญคอร์ส /blog/series/, ปุ่มก่อนหน้า-ถัดไป, "
     "sidebar ลิสต์ EP, แถบความคืบหน้า) | ตัวเลือก B: ใช้ tag ไปก่อน", False, None),
    ("เขียน Python 101 EP1 ติดตั้ง Python และรันโค้ดบรรทัดแรก", 3, "article",
     "โครง 8 ส่วนต่อ EP ตามแม่พิมพ์ที่ตกลงไว้ + ภาพปกหนูดี + diagram ทุก h2", False, None),
]

for title, offset, cat, desc, done, art in rows:
    start = timezone.make_aware(
        datetime.combine(today + timedelta(days=offset), datetime.min.time())
    )
    ev, created = CalendarEvent.objects.get_or_create(
        title=title,
        start_datetime=start,
        defaults={
            "all_day": True,
            "category": cat,
            "description": desc,
            "is_completed": done,
            "article": art,
            "assigned_to": "หนูดี",
        },
    )
    print(("created" if created else "exists "), "|", ev.start_datetime.date(), "|", ev.title)
