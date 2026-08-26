import django
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'E:\Project Peyo Peyo\Agent Skill Claude')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_automate.settings')
django.setup()

from dashboard.models import CalendarEvent, Note
from django.utils import timezone

today = timezone.now()

print("=== CALENDAR (วันนี้เป็นต้นไป) ===")
events = CalendarEvent.objects.filter(start_datetime__gte=today).order_by('start_datetime')[:20]
if events:
    for e in events:
        status = "DONE" if e.is_completed else "TODO"
        print(f"[{e.start_datetime.strftime('%Y-%m-%d')}] [{status}] {e.title}")
else:
    print("(ไม่มีงานค้าง)")

print()
print("=== NOTES (ล่าสุด) ===")
notes = Note.objects.all().order_by('-updated_at')[:10]
if notes:
    for n in notes:
        print(f"[{n.updated_at.strftime('%Y-%m-%d')}] {n.title}")
        print(f"  {n.content[:100]}")
        print()
else:
    print("(ไม่มี notes)")
