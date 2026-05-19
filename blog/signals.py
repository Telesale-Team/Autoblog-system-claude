from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="blog.Article")
def sync_article_to_calendar(sender, instance, **kwargs):
    """
    เมื่อบทความถูก save:
    - published → สร้าง/อัปเดต CalendarEvent category='article'
    - draft/waiting → ลบ CalendarEvent (ถ้ามี)
    """
    try:
        from dashboard.models import CalendarEvent
    except ImportError:
        return

    event_date = instance.published_at or instance.created_at

    if event_date:
        status_label = {"published": "เผยแพร่แล้ว", "waiting": "รอเขียน", "draft": "Draft"}.get(instance.status, instance.status)
        CalendarEvent.objects.update_or_create(
            category="article",
            title=instance.title,
            defaults={
                "start_datetime": event_date,
                "end_datetime":   None,
                "all_day":        True,
                "is_system":      True,
                "is_completed":   instance.status == "published",
                "description":    f"{status_label}: {instance.title}",
                "created_by":     None,
            },
        )
