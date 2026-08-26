import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from dashboard.models import CalendarEvent
from blog.models import Article
from crm.models import ContactLead as Lead

print("=" * 60)
print("1. TASK หนูดีสร้าง (CalendarEvent is_system=True, category!=article)")
print("=" * 60)
tasks = CalendarEvent.objects.filter(is_system=True).exclude(category="article").order_by("-start_datetime")
for e in tasks:
    status = "done" if e.is_completed else "pending"
    print(f"  [{status}] {e.category} | {e.title[:55]}")
print(f"  รวม: {tasks.count()} tasks\n")

print("=" * 60)
print("2. ARTICLE EVENT (CalendarEvent category=article)")
print("=" * 60)
art_events = CalendarEvent.objects.filter(category="article").order_by("-start_datetime")
for e in art_events[:10]:
    status = "done" if e.is_completed else "pending"
    has_fk = "มี FK" if e.article_id else "ไม่มี FK"
    print(f"  [{status}] {has_fk} | {e.title[:50]}")
if art_events.count() > 10:
    print(f"  ... และอีก {art_events.count() - 10} รายการ")
print(f"  รวม: {art_events.count()} events\n")

print("=" * 60)
print("3. LEAD EVENT (auto-generate จาก CRM — ไม่มีใน CalendarEvent DB)")
print("=" * 60)
try:
    leads = Lead.objects.all()
    print(f"  Lead ใน CRM: {leads.count()} รายการ")
    print("  (Lead events render จาก CRM โดยตรง ไม่บันทึกใน CalendarEvent)")
except Exception as e:
    print(f"  ไม่พบ Lead model: {e}")

print()
print("=" * 60)
print("4. ARTICLE EVENT จาก Article (auto-generate — ไม่มีใน CalendarEvent DB)")
print("=" * 60)
published = Article.objects.filter(status="published").count()
print(f"  Published articles: {published} บทความ")
print("  (Article events render จาก Article.published_at โดยตรง ไม่บันทึกใน CalendarEvent)")
print("  (ต่างจาก CalendarEvent category=article ที่บันทึกจริงใน DB)")
