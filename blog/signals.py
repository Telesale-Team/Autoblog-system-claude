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

    if instance.status == "published" and event_date:
        CalendarEvent.objects.update_or_create(
            category="article",
            title=instance.title,
            defaults={
                "start_datetime": event_date,
                "end_datetime":   None,
                "all_day":        True,
                "is_system":      True,
                "is_completed":   False,
                "description":    f"บทความ: {instance.title}",
                "created_by":     None,
            },
        )
    else:
        # ลบ event ถ้าเปลี่ยนกลับเป็น draft/waiting
        CalendarEvent.objects.filter(
            category="article",
            title=instance.title,
            is_system=True,
        ).delete()
