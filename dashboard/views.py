import json
import re
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from pages.models import ContactLead
from blog.models import Article
from portfolio.models import CaseStudy


# ── Internal docs registry ──────────────────────────────────────────────
INTERNAL_DOCS = [
    {
        "slug": "team-manual",
        "filename": "team_manual.html",
        "title": "คู่มือทีมงาน — 10 Agents System",
        "description": "ภาพรวมระบบ 10 agents, routing logic, workflows, approval matrix และตารางการทำงาน",
        "audience": "ทุก agent (Operations)",
        "icon": "fas fa-users-cog",
        "color": "primary",
    },
    {
        "slug": "openclaw-manual",
        "filename": "openclaw_manual.html",
        "title": "OpenClaw — คู่มือผลิตภัณฑ์",
        "description": "คู่มือเต็มของ OpenClaw — สถาปัตยกรรม, ฟีเจอร์, channels, multi-agent, การติดตั้ง, model การเงิน",
        "audience": "AI Orchestrator + ทุก agent ที่ขายของ",
        "icon": "fas fa-cogs",
        "color": "info",
    },
    {
        "slug": "product-strategy",
        "filename": "product_strategy.html",
        "title": "Product Strategy — ช่องว่างตลาดไทย AI",
        "description": "วิเคราะห์ตลาด, คู่แข่ง (Broadpang/Oho.chat), 5 Products, customer segments, channels, pricing, roadmap",
        "audience": "CEO + Marketing + Hustler",
        "icon": "fas fa-chart-line",
        "color": "success",
    },
    {
        "slug": "action-plan",
        "filename": "action_plan.html",
        "title": "Action Plan — แผนปฏิบัติการ",
        "description": "Roadmap และ action items ระยะสั้น/กลาง/ยาว สำหรับ launch business",
        "audience": "CEO + Chief of Staff",
        "icon": "fas fa-rocket",
        "color": "warning",
    },
    {
        "slug": "salepage",
        "filename": "salepage.html",
        "title": "Sales Page Reference",
        "description": "ต้นแบบ landing page ที่ใช้สร้างหน้าเว็บลูกค้าจริง — เก็บไว้เป็น design reference",
        "audience": "Marketing Specialist",
        "icon": "fas fa-bullhorn",
        "color": "danger",
    },
]


@staff_member_required
def coming_soon(request):
    return render(request, "dashboard/coming_soon.html", {
        "page_title": "Coming Soon",
    })


def _find_doc(slug):
    return next((d for d in INTERNAL_DOCS if d["slug"] == slug), None)


@staff_member_required
def docs_index(request):
    return render(request, "dashboard/docs_index.html", {"docs": INTERNAL_DOCS})


@staff_member_required
def docs_view(request, slug):
    doc = _find_doc(slug)
    if not doc:
        raise Http404("Doc not found")
    path = Path(settings.BASE_DIR) / "docs" / doc["filename"]
    if not path.exists():
        raise Http404(f"File missing: {doc['filename']}")
    return HttpResponse(path.read_bytes(), content_type="text/html; charset=utf-8")


@staff_member_required
def index(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    # ── KPI 1: Lead ใหม่วันนี้ + source breakdown ───────────────────────────
    leads_today = ContactLead.objects.filter(created_at__gte=today_start).count()
    leads_today_sources = list(
        ContactLead.objects.filter(created_at__gte=today_start)
        .values("source")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # ── KPI 2: Active Pipeline (non-closed leads) ────────────────────────────
    active_pipeline = ContactLead.objects.exclude(
        status__in=["closed_won", "closed_lost"]
    ).count()
    pipeline_by_status = list(
        ContactLead.objects.exclude(status__in=["closed_won", "closed_lost"])
        .values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    # ── KPI 3: Blog views สะสม (proxy — no GA) ──────────────────────────────
    total_views = Article.objects.aggregate(total=Sum("views_count"))["total"] or 0

    # ── KPI 4: บทความสัปดาห์นี้ vs เป้า 2 ชิ้น ─────────────────────────────
    articles_this_week = Article.objects.filter(
        status="published", published_at__gte=week_start
    ).count()
    article_weekly_goal = 2

    # ── KPI 5: MQL สะสม (leads ทั้งหมด) ────────────────────────────────────
    mql_total = ContactLead.objects.count()

    # ── KPI 6: วันนี้ต้องทำ (auto action list) ──────────────────────────────
    stale_count = ContactLead.objects.filter(
        status__in=["new", "contacted"],
        updated_at__lt=now - timedelta(days=3),
    ).count()
    new_lead_count = ContactLead.objects.filter(status="new").count()
    today_actions = []
    if stale_count > 0:
        today_actions.append({
            "type": "danger",
            "icon": "bi-exclamation-circle-fill",
            "text": f"Follow up {stale_count} lead ที่ไม่ได้ติดต่อ > 3 วัน",
            "url": "leads/?status=new",
        })
    if articles_this_week < article_weekly_goal:
        gap = article_weekly_goal - articles_this_week
        today_actions.append({
            "type": "warning",
            "icon": "bi-pencil-fill",
            "text": f"เขียนบทความเพิ่มอีก {gap} ชิ้น ให้ครบ {article_weekly_goal}/สัปดาห์",
            "url": "blog/",
        })
    if new_lead_count > 0:
        today_actions.append({
            "type": "primary",
            "icon": "bi-person-check-fill",
            "text": f"Qualify {new_lead_count} new lead",
            "url": "leads/?status=new",
        })
    hot_leads = ContactLead.objects.filter(
        status="proposal",
        updated_at__lt=now - timedelta(days=5),
    ).count()
    if hot_leads > 0:
        today_actions.append({
            "type": "orange",
            "icon": "bi-fire",
            "text": f"Hot lead {hot_leads} ราย อยู่ใน Proposal > 5 วัน — รีบโทร!",
            "url": "pipeline/",
        })

    # ── Chart: Leads 30 วัน ──────────────────────────────────────────────────
    days_ago_30 = now - timedelta(days=30)
    leads_by_day = (
        ContactLead.objects.filter(created_at__gte=days_ago_30)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    by_day_map = {row["day"].isoformat(): row["count"] for row in leads_by_day}
    chart_labels, chart_data = [], []
    for i in range(29, -1, -1):
        d = (now - timedelta(days=i)).date()
        chart_labels.append(d.strftime("%d %b"))
        chart_data.append(by_day_map.get(d.isoformat(), 0))

    # ── Supporting data ──────────────────────────────────────────────────────
    leads_this_month = ContactLead.objects.filter(created_at__gte=month_start).count()
    leads_last_month = ContactLead.objects.filter(
        created_at__gte=last_month_start, created_at__lt=month_start
    ).count()
    leads_delta = leads_this_month - leads_last_month
    leads_delta_pct = (
        round((leads_delta / leads_last_month) * 100) if leads_last_month else 0
    )
    published_articles = Article.objects.filter(status="published").count()
    active_cases = CaseStudy.objects.filter(status="published").count()
    recent_leads = ContactLead.objects.order_by("-created_at")[:10]
    top_articles = Article.objects.filter(status="published").order_by("-views_count")[:5]

    return render(request, "dashboard/index.html", {
        # KPI 1
        "leads_today": leads_today,
        "leads_today_sources": leads_today_sources,
        # KPI 2
        "active_pipeline": active_pipeline,
        "pipeline_by_status": pipeline_by_status,
        # KPI 3
        "total_views": total_views,
        # KPI 4
        "articles_this_week": articles_this_week,
        "article_weekly_goal": article_weekly_goal,
        # KPI 5
        "mql_total": mql_total,
        # KPI 6
        "today_actions": today_actions,
        # chart
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        # supporting
        "leads_this_month": leads_this_month,
        "leads_delta_pct": leads_delta_pct,
        "published_articles": published_articles,
        "total_views": total_views,
        "active_cases": active_cases,
        "recent_leads": recent_leads,
        "top_articles": top_articles,
    })


# ── Leads ───────────────────────────────────────────────────────────────────

@staff_member_required
def leads_list(request):
    status_filter = request.GET.get("status", "")
    leads = ContactLead.objects.all()
    if status_filter:
        leads = leads.filter(status=status_filter)
    leads = leads.order_by("-created_at")

    new_count = ContactLead.objects.filter(status="new").count()

    return render(request, "dashboard/leads_list.html", {
        "leads": leads,
        "status_filter": status_filter,
        "status_choices": ContactLead.STATUS_CHOICES,
        "new_count": new_count,
    })


@staff_member_required
@require_POST
def lead_update_status(request, pk):
    lead = get_object_or_404(ContactLead, pk=pk)
    try:
        data = json.loads(request.body)
        new_status = data.get("status", "")
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    valid_statuses = [s[0] for s in ContactLead.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse({"error": "Invalid status"}, status=400)

    lead.status = new_status
    lead.save(update_fields=["status", "updated_at"])
    return JsonResponse({"ok": True, "status": lead.status, "status_display": lead.get_status_display()})


# ── Blog ────────────────────────────────────────────────────────────────────

@staff_member_required
def blog_list(request):
    status_filter = request.GET.get("status", "")
    articles = Article.objects.select_related("author", "category").all()
    if status_filter:
        articles = articles.filter(status=status_filter)
    articles = articles.order_by("-created_at")

    draft_count = Article.objects.filter(status="draft").count()

    return render(request, "dashboard/blog_list.html", {
        "articles": articles,
        "status_filter": status_filter,
        "draft_count": draft_count,
    })


@staff_member_required
@require_POST
def article_toggle_status(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.status == "published":
        article.status = "draft"
    else:
        article.status = "published"
        if not article.published_at:
            article.published_at = timezone.now()
    article.save(update_fields=["status", "published_at", "updated_at"])
    return JsonResponse({"ok": True, "status": article.status, "status_display": article.get_status_display()})


# ── Pipeline ─────────────────────────────────────────────────────────────────

PIPELINE_STAGES = [
    ("new",        "New",        "bg-warning text-dark"),
    ("contacted",  "Contacted",  "bg-info text-dark"),
    ("qualified",  "Qualified",  "bg-primary"),
    ("proposal",   "Proposal",   "bg-orange"),
    ("closed_won", "Closed Won", "bg-success"),
    ("closed_lost","Closed Lost","bg-secondary"),
]

@staff_member_required
def pipeline_view(request):
    now = timezone.now()
    all_leads = ContactLead.objects.order_by("-updated_at")
    leads_by_stage = {}
    for status, _, _ in PIPELINE_STAGES:
        leads_by_stage[status] = []
    for lead in all_leads:
        if lead.status in leads_by_stage:
            leads_by_stage[lead.status].append(lead)

    pipeline_value = (
        ContactLead.objects.exclude(status__in=["closed_won", "closed_lost"])
        .aggregate(total=Sum("deal_value"))["total"] or 0
    )
    won_value = (
        ContactLead.objects.filter(status="closed_won")
        .aggregate(total=Sum("deal_value"))["total"] or 0
    )
    hot_leads_pks = list(
        ContactLead.objects.filter(
            status="proposal",
            updated_at__lt=now - timedelta(days=5),
        ).values_list("pk", flat=True)
    )
    stale_pks = list(
        ContactLead.objects.filter(
            status__in=["new", "contacted"],
            updated_at__lt=now - timedelta(days=3),
        ).values_list("pk", flat=True)
    )

    stages_with_leads = [
        {
            "status": status,
            "label": label,
            "badge_cls": badge_cls,
            "leads": leads_by_stage[status],
        }
        for status, label, badge_cls in PIPELINE_STAGES
    ]

    return render(request, "dashboard/pipeline.html", {
        "stages_with_leads": stages_with_leads,
        "pipeline_value": pipeline_value,
        "won_value": won_value,
        "hot_leads_pks": hot_leads_pks,
        "stale_pks": stale_pks,
        "status_choices": ContactLead.STATUS_CHOICES,
    })


@staff_member_required
@require_POST
def lead_update_deal_value(request, pk):
    lead = get_object_or_404(ContactLead, pk=pk)
    try:
        data = json.loads(request.body)
        value = data.get("deal_value")
        lead.deal_value = value if value not in (None, "") else None
        lead.save(update_fields=["deal_value", "updated_at"])
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({"error": "Invalid value"}, status=400)
    return JsonResponse({"ok": True, "deal_value": str(lead.deal_value or "")})


# ── Revenue ──────────────────────────────────────────────────────────────────

@staff_member_required
def revenue_view(request):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    won_total = ContactLead.objects.filter(status="closed_won").aggregate(
        total=Sum("deal_value"))["total"] or 0
    won_this_month = ContactLead.objects.filter(
        status="closed_won", updated_at__gte=month_start
    ).aggregate(total=Sum("deal_value"))["total"] or 0
    won_last_month = ContactLead.objects.filter(
        status="closed_won",
        updated_at__gte=last_month_start, updated_at__lt=month_start,
    ).aggregate(total=Sum("deal_value"))["total"] or 0

    pipeline_value = ContactLead.objects.exclude(
        status__in=["closed_won", "closed_lost"]
    ).aggregate(total=Sum("deal_value"))["total"] or 0

    won_count = ContactLead.objects.filter(status="closed_won").count()
    lost_count = ContactLead.objects.filter(status="closed_lost").count()
    win_rate = round(won_count / (won_count + lost_count) * 100) if (won_count + lost_count) > 0 else 0

    recent_won = ContactLead.objects.filter(status="closed_won").order_by("-updated_at")[:10]

    rev_delta_pct = (
        round((float(won_this_month) - float(won_last_month)) / float(won_last_month) * 100)
        if won_last_month else 0
    )

    return render(request, "dashboard/revenue.html", {
        "won_total": won_total,
        "won_this_month": won_this_month,
        "won_last_month": won_last_month,
        "rev_delta_pct": rev_delta_pct,
        "pipeline_value": pipeline_value,
        "won_count": won_count,
        "lost_count": lost_count,
        "win_rate": win_rate,
        "recent_won": recent_won,
    })


# ── Analytics ────────────────────────────────────────────────────────────────

@staff_member_required
def analytics_view(request):
    from blog.models import Category
    from django.db.models.functions import TruncWeek

    now = timezone.now()

    # Leads by source
    leads_by_source = list(
        ContactLead.objects.values("source")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Leads by status (funnel)
    status_order = ["new", "contacted", "qualified", "proposal", "closed_won", "closed_lost"]
    status_counts = {
        row["status"]: row["count"]
        for row in ContactLead.objects.values("status").annotate(count=Count("id"))
    }
    leads_funnel = [
        {"status": s, "label": dict(ContactLead.STATUS_CHOICES).get(s, s), "count": status_counts.get(s, 0)}
        for s in status_order
    ]

    # Articles by category
    articles_by_cat = list(
        Article.objects.filter(status="published")
        .values("category__name")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Top 10 articles by views
    top_articles = list(
        Article.objects.filter(status="published")
        .order_by("-views_count")
        .values("title", "views_count", "category__name")[:10]
    )

    # Weekly leads — last 12 weeks
    weeks_ago_12 = now - timedelta(weeks=12)
    weekly_leads_qs = (
        ContactLead.objects.filter(created_at__gte=weeks_ago_12)
        .annotate(week=TruncWeek("created_at"))
        .values("week")
        .annotate(count=Count("id"))
        .order_by("week")
    )
    weekly_leads_map = {row["week"].date().isoformat(): row["count"] for row in weekly_leads_qs}

    # Weekly articles published — last 12 weeks
    weekly_articles_qs = (
        Article.objects.filter(status="published", published_at__gte=weeks_ago_12)
        .annotate(week=TruncWeek("published_at"))
        .values("week")
        .annotate(count=Count("id"))
        .order_by("week")
    )
    weekly_articles_map = {row["week"].date().isoformat(): row["count"] for row in weekly_articles_qs}

    week_labels, week_leads_data, week_articles_data = [], [], []
    for i in range(11, -1, -1):
        week_start = (now - timedelta(weeks=i)).date()
        # normalize to Monday
        week_monday = week_start - timedelta(days=week_start.weekday())
        week_labels.append(week_monday.strftime("%d %b"))
        week_leads_data.append(weekly_leads_map.get(week_monday.isoformat(), 0))
        week_articles_data.append(weekly_articles_map.get(week_monday.isoformat(), 0))

    return render(request, "dashboard/analytics.html", {
        "leads_by_source": leads_by_source,
        "source_labels": json.dumps([r["source"] for r in leads_by_source]),
        "source_data":   json.dumps([r["count"]  for r in leads_by_source]),
        "leads_funnel":  leads_funnel,
        "funnel_labels": json.dumps([r["label"] for r in leads_funnel]),
        "funnel_data":   json.dumps([r["count"] for r in leads_funnel]),
        "articles_by_cat":   articles_by_cat,
        "cat_labels": json.dumps([r["category__name"] or "—" for r in articles_by_cat]),
        "cat_data":   json.dumps([r["count"] for r in articles_by_cat]),
        "top_articles":      top_articles,
        "top_article_labels": json.dumps([r["title"][:40] for r in top_articles]),
        "top_article_data":   json.dumps([r["views_count"] for r in top_articles]),
        "week_labels":        json.dumps(week_labels),
        "week_leads_data":    json.dumps(week_leads_data),
        "week_articles_data": json.dumps(week_articles_data),
    })


# ── Content Backlog ──────────────────────────────────────────────────────────

def _parse_backlog():
    backlog_path = Path(settings.BASE_DIR) / "content_backlog" / "BACKLOG.md"
    if not backlog_path.exists():
        return []
    text = backlog_path.read_text(encoding="utf-8")

    # Find the Queue table — between "## 📝 Queue" and "## " next section
    queue_match = re.search(r"## [^\n]*Queue[^\n]*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if not queue_match:
        return []

    items = []
    for line in queue_match.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|") or re.match(r"^\|[-| ]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 8 or cells[0] == "#":
            continue
        num, status_raw, priority, topic, keyword, notes, added, owner = (cells + [""] * 8)[:8]
        status = re.sub(r"`", "", status_raw).strip()
        items.append({
            "num":      num.strip(),
            "status":   status,
            "priority": priority.strip(),
            "topic":    topic.strip(),
            "keyword":  keyword.strip(),
            "notes":    notes.strip(),
            "added":    added.strip(),
        })
    return items


@staff_member_required
def backlog_view(request):
    items = _parse_backlog()
    status_filter = request.GET.get("status", "")
    if status_filter:
        items = [i for i in items if i["status"] == status_filter]

    counts = {}
    for item in _parse_backlog():
        counts[item["status"]] = counts.get(item["status"], 0) + 1

    return render(request, "dashboard/backlog.html", {
        "items": items,
        "status_filter": status_filter,
        "counts": counts,
        "total": sum(counts.values()),
    })
