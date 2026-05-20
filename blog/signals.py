from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="blog.Article")
def sync_article_to_calendar(sender, instance, **kwargs):
    try:
        from dashboard.models import CalendarEvent
    except ImportError:
        return

    event_date = instance.published_at or instance.created_at
    if not event_date:
        return

    is_done = instance.status == "published"
    status_label = {"published": "เผยแพร่แล้ว", "waiting": "รอเขียน", "draft": "Draft"}.get(instance.status, instance.status)

    # ลอง lookup ด้วย FK ก่อน (reliable)
    ev = CalendarEvent.objects.filter(article=instance).first()

    if ev:
        CalendarEvent.objects.filter(article=instance).update(
            title=instance.title,
            is_completed=is_done,
            description=f"{status_label}: {instance.title}",
            start_datetime=event_date,
        )
    else:
        # fallback: title match สำหรับ event เก่าที่ยังไม่มี FK
        ev_by_title = CalendarEvent.objects.filter(
            category="article", title=instance.title, is_system=True
        ).first()

        if ev_by_title:
            ev_by_title.article       = instance
            ev_by_title.is_completed  = is_done
            ev_by_title.description   = f"{status_label}: {instance.title}"
            ev_by_title.start_datetime = event_date
            ev_by_title.save(update_fields=["article", "is_completed", "description", "start_datetime"])
        else:
            # สร้างใหม่
            CalendarEvent.objects.create(
                title=instance.title,
                category="article",
                is_system=True,
                article=instance,
                start_datetime=event_date,
                end_datetime=None,
                all_day=True,
                is_completed=is_done,
                description=f"{status_label}: {instance.title}",
                created_by=None,
            )
