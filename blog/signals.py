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

    # 1. FK lookup (reliable — event เชื่อมกับ article โดยตรง)
    ev = CalendarEvent.objects.filter(article=instance).first()

    if ev:
        CalendarEvent.objects.filter(article=instance).update(
            title=instance.title,
            is_completed=is_done,
            description=f"{status_label}: {instance.title}",
            start_datetime=event_date,
        )

    else:
        # 2. Backlog chain — ใช้ backlog_ref.calendar_event เชื่อมกลับ
        ev_via_backlog = None
        if instance.backlog_ref_id:
            try:
                backlog = instance.backlog_ref
                if backlog.calendar_event_id:
                    ev_via_backlog = backlog.calendar_event
            except Exception:
                pass

        if ev_via_backlog:
            ev_via_backlog.article        = instance
            ev_via_backlog.is_completed   = is_done
            ev_via_backlog.description    = f"{status_label}: {instance.title}"
            ev_via_backlog.start_datetime = event_date
            ev_via_backlog.save(update_fields=["article", "is_completed", "description", "start_datetime"])

        else:
            # 3. Title exact match สำหรับ event เก่าที่ยังไม่มี FK หรือ backlog
            ev_by_title = CalendarEvent.objects.filter(
                category="article", title=instance.title, is_system=True
            ).first()

            if ev_by_title:
                ev_by_title.article        = instance
                ev_by_title.is_completed   = is_done
                ev_by_title.description    = f"{status_label}: {instance.title}"
                ev_by_title.start_datetime = event_date
                ev_by_title.save(update_fields=["article", "is_completed", "description", "start_datetime"])

            else:
                # 4. สร้างใหม่
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

    # Auto-close backlog เมื่อ published
    if is_done and instance.backlog_ref_id:
        try:
            from marketing.models import ContentBacklog
            ContentBacklog.objects.filter(
                pk=instance.backlog_ref_id,
            ).exclude(status="done").update(status="done")
        except Exception:
            pass
