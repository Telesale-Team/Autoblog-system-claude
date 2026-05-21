import os
import sys
import django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from dashboard.models import CalendarEvent

orphaned = CalendarEvent.objects.filter(
    category="article",
    article__isnull=True,
    is_system=True,
    is_completed=False,
)
print(f"Orphaned events found: {orphaned.count()}")

deleted_ids = []
kept_ids = []

for ev in orphaned:
    has_done_sibling = CalendarEvent.objects.filter(
        category="article",
        article__isnull=False,
        is_completed=True,
        start_datetime__date=ev.start_datetime.date(),
    ).exists()
    if has_done_sibling:
        deleted_ids.append(ev.id)
    else:
        kept_ids.append(ev.id)

print(f"Delete (has done sibling): {len(deleted_ids)} — {deleted_ids}")
print(f"Keep (no sibling):        {len(kept_ids)} — {kept_ids}")

CalendarEvent.objects.filter(id__in=deleted_ids).delete()
print(f"Deleted {len(deleted_ids)} orphaned events")

if kept_ids:
    CalendarEvent.objects.filter(id__in=kept_ids).update(
        is_completed=True,
        description="Closed: บทความเผยแพร่แล้ว",
    )
    print(f"Marked done: {len(kept_ids)} events")

print("Done.")
