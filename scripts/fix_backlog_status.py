import os
import sys
import django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from marketing.models import ContentBacklog
from blog.models import Article
from dashboard.models import CalendarEvent

fixed = 0
linked = 0

print("=== Step 1: backlog มี backlog_ref แต่ article published แล้ว ===")
for backlog in ContentBacklog.objects.exclude(status="done"):
    published = backlog.articles.filter(status="published")
    if published.exists():
        print(f"  Fix #{backlog.pk} '{backlog.topic[:50]}' → done")
        ContentBacklog.objects.filter(pk=backlog.pk).update(status="done")
        fixed += 1

print(f"Fixed via backlog_ref: {fixed}")
print()

print("=== Step 2: published articles ที่ไม่มี backlog_ref — หา backlog ที่ topic ตรงกัน ===")
orphan_articles = Article.objects.filter(status="published", backlog_ref__isnull=True)
for art in orphan_articles:
    # ลอง exact match ก่อน
    match = ContentBacklog.objects.filter(
        topic=art.title,
        status__in=["pending", "in_progress", "review"],
    ).first()
    if not match:
        # ลอง contains match (title อยู่ใน topic หรือกลับกัน)
        match = ContentBacklog.objects.filter(
            topic__icontains=art.title[:30],
            status__in=["pending", "in_progress", "review"],
        ).first()
    if match:
        print(f"  Link Article #{art.pk} → Backlog #{match.pk} '{match.topic[:50]}'")
        art.backlog_ref = match
        art.save(update_fields=["backlog_ref"])
        ContentBacklog.objects.filter(pk=match.pk).update(status="done")
        # link CalendarEvent ถ้ามี
        if match.calendar_event_id:
            CalendarEvent.objects.filter(pk=match.calendar_event_id).update(
                article=art,
                is_completed=True,
                description=f"เผยแพร่แล้ว: {art.title}",
            )
        linked += 1

print(f"Linked+fixed orphan articles: {linked}")
print()

print("=== ผลสรุป ===")
counts = {}
for item in ContentBacklog.objects.all():
    counts[item.status] = counts.get(item.status, 0) + 1
print("Status counts:", counts)
print("Done.")
