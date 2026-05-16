import json
import os
import re
from datetime import date, timedelta
from pathlib import Path
from django.utils.dateparse import parse_datetime

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt

from pages.models import ContactLead
from blog.models import Article
from portfolio.models import CaseStudy
from dashboard.models import CalendarEvent


# ── Internal docs registry ──────────────────────────────────────────────
INTERNAL_DOCS = [
    {
        "slug": "team-manual",
        "filename": "team_manual.html",
        "title": "Team Manual",
        "description": "ภาพรวมระบบ 10 agents, routing logic, workflows, approval matrix และตารางการทำงาน",
        "audience": "all",
        "bi_icon": "bi-people-fill",
    },
    {
        "slug": "openclaw-manual",
        "filename": "openclaw_manual.html",
        "title": "OpenClaw Manual",
        "description": "คู่มือเต็มของ OpenClaw — สถาปัตยกรรม, ฟีเจอร์, channels, multi-agent, การติดตั้ง, model การเงิน",
        "audience": "tech",
        "bi_icon": "bi-terminal-fill",
    },
    {
        "slug": "product-strategy",
        "filename": "product_strategy.html",
        "title": "Product Strategy",
        "description": "วิเคราะห์ตลาด, คู่แข่ง, 5 Products, customer segments, channels, pricing, roadmap",
        "audience": "owner",
        "bi_icon": "bi-rocket-takeoff-fill",
    },
    {
        "slug": "action-plan",
        "filename": "action_plan.html",
        "title": "Action Plan",
        "description": "Roadmap และ action items ระยะสั้น/กลาง/ยาว สำหรับ launch business",
        "audience": "all",
        "bi_icon": "bi-kanban-fill",
    },
    {
        "slug": "salepage",
        "filename": "salepage.html",
        "title": "Salepage Copy",
        "description": "ต้นแบบ landing page ที่ใช้สร้างหน้าเว็บลูกค้าจริง — เก็บไว้เป็น design reference",
        "audience": "sales",
        "bi_icon": "bi-megaphone-fill",
    },
    {
        "slug": "feature-roadmap",
        "filename": "feature_roadmap.html",
        "title": "Feature Roadmap",
        "description": "แผนพัฒนา Feature ทั้งหมด 29 เมนู — จากการประชุมทีม 13 AI Agents พร้อม Data Model และ KPI",
        "audience": "owner",
        "bi_icon": "bi-map-fill",
    },
]


@staff_member_required
def coming_soon(request):
    return render(request, "dashboard/coming_soon.html", {
        "page_title": "Coming Soon",
    })


def redirect_to(url_name):
    """Return a view function that redirects to url_name (used in urls.py)."""
    @staff_member_required
    def _view(request, *args, **kwargs):
        return redirect(reverse_lazy(url_name))
    return _view


def _find_doc(slug):
    return next((d for d in INTERNAL_DOCS if d["slug"] == slug), None)


@staff_member_required
def docs_index(request):
    return render(request, "dashboard/docs_index.html", {
        "docs": INTERNAL_DOCS,
        "active_slug": None,
    })


@xframe_options_exempt
@staff_member_required
def docs_content(request, slug):
    doc = _find_doc(slug)
    if not doc:
        return HttpResponse("<p class='text-danger'>ไม่พบเอกสาร</p>", status=404)
    doc_path = BASE_DIR / "docs" / doc["filename"]
    if not doc_path.exists():
        return HttpResponse("<p class='text-danger'>ไฟล์เอกสารหายไป</p>", status=404)
    html = doc_path.read_text(encoding="utf-8")
    return HttpResponse(html, content_type="text/html; charset=utf-8")


@staff_member_required
def docs_view(request, slug):
    doc = _find_doc(slug)
    if not doc:
        raise Http404("Doc not found")
    return render(request, "dashboard/docs_index.html", {
        "docs": INTERNAL_DOCS,
        "active_slug": slug,
    })


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
def team_view(request):
    agents = [
        {
            "number": "01",
            "name": "Chief of Staff",
            "alias": "หนูดี",
            "alias_example": "หนูดี - สรุปสถานะธุรกิจวันนี้",
            "activate": "หนูดี",
            "icon": "bi-person-badge-fill",
            "color": "gold",
            "role": "Orchestrator หลัก — routing ทุก request, สรุปภาพรวม",
            "use_when": "ไม่รู้จะถามใคร / ต้องการ Executive Summary / สั่งงานหลายทีมพร้อมกัน",
            "stage": "now",
        },
        {
            "number": "02",
            "name": "Hustler (Sales)",
            "alias": "Activate Hustler",
            "alias_example": "Activate Hustler - เขียน proposal ลูกค้าคลินิก",
            "activate": "Activate Hustler",
            "icon": "bi-briefcase-fill",
            "color": "navy",
            "role": "ปิดดีล B2B, qualify lead, เขียน proposal, handle objections",
            "use_when": "ต้องการเขียน proposal / negotiate / ตอบคำถามลูกค้าเรื่องราคา",
            "stage": "now",
        },
        {
            "number": "13",
            "name": "Frontend Designer",
            "alias": "ลอย",
            "alias_example": "ลอย - ออกแบบหน้า services ให้ดูมืออาชีพขึ้น",
            "activate": "ลอย",
            "icon": "bi-palette-fill",
            "color": "gold",
            "role": "Design System, UI/UX, Color Palette, Component Library",
            "use_when": "ออกแบบหน้าเว็บ / ปรับสี layout / สร้าง component ใหม่",
            "stage": "now",
        },
        {
            "number": "12",
            "name": "Content Writer (TH)",
            "alias": "Activate Content Writer",
            "alias_example": "Activate Content Writer - เขียนบทความ AI กับ SME ไทย",
            "activate": "Activate Content Writer",
            "icon": "bi-pencil-fill",
            "color": "navy",
            "role": "เขียนบทความไทยคุณภาพสูง SEO + lead generation",
            "use_when": "เขียน blog post / ปรับ tone content / rewrite ให้เป็นภาษาไทยธรรมชาติ",
            "stage": "now",
        },
        {
            "number": "11",
            "name": "SEO Specialist",
            "alias": "Activate SEO Specialist",
            "alias_example": "Activate SEO Specialist - วิจัย keyword AI automation ไทย",
            "activate": "Activate SEO Specialist",
            "icon": "bi-search",
            "color": "navy",
            "role": "Keyword research ไทย, on-page SEO, ranking strategy",
            "use_when": "ก่อนเขียนบทความทุกครั้ง / audit SEO / เช็ค Google ranking",
            "stage": "now",
        },
        {
            "number": "07",
            "name": "Marketing Specialist",
            "alias": "Activate Marketing Specialist",
            "alias_example": "Activate Marketing Specialist - วาง content calendar เดือนนี้",
            "activate": "Activate Marketing Specialist",
            "icon": "bi-megaphone-fill",
            "color": "navy",
            "role": "กลยุทธ์การตลาด, content calendar, lead generation, brand",
            "use_when": "วาง campaign / content plan / social media strategy",
            "stage": "now",
        },
        {
            "number": "03",
            "name": "AI Orchestrator",
            "alias": "Activate AI Orchestrator",
            "alias_example": "Activate AI Orchestrator - ออกแบบระบบ AI chatbot สำหรับคลินิก",
            "activate": "Activate AI Orchestrator",
            "icon": "bi-cpu-fill",
            "color": "navy",
            "role": "Technical lead, สร้างระบบ AI, architecture, tech stack",
            "use_when": "สร้างระบบ AI ให้ลูกค้า / เลือก tech stack / แก้ปัญหา technical",
            "stage": "now",
        },
        {
            "number": "05",
            "name": "AI Toolsmith",
            "alias": "Activate AI Toolsmith",
            "alias_example": "Activate AI Toolsmith - สร้าง prompt template สำหรับ chatbot คลินิก",
            "activate": "Activate AI Toolsmith",
            "icon": "bi-tools",
            "color": "navy",
            "role": "Prompt library, template, reusable tools และ skills",
            "use_when": "สร้าง prompt ใหม่ / ปรับ template / build skill ที่ใช้ซ้ำได้",
            "stage": "now",
        },
        {
            "number": "06",
            "name": "QA Agent",
            "alias": "Activate QA Agent",
            "alias_example": "Activate QA Agent - review บทความนี้ก่อน publish",
            "activate": "Activate QA Agent",
            "icon": "bi-shield-check",
            "color": "navy",
            "role": "ตรวจคุณภาพ output ทุกชิ้นก่อน deliver",
            "use_when": "ก่อน publish บทความ / ก่อนส่ง proposal / review code/design",
            "stage": "now",
        },
        {
            "number": "04",
            "name": "Money Manager",
            "alias": "Activate Money Manager",
            "alias_example": "Activate Money Manager - ตั้งราคา LINE AI Pro ให้เหมาะกับตลาดไทย",
            "activate": "Activate Money Manager",
            "icon": "bi-cash-coin",
            "color": "muted",
            "role": "การเงิน, บัญชี, ภาษี, pricing, cash flow",
            "use_when": "ตั้งราคา / ทำ invoice / คำนวณ VAT / วาง budget",
            "stage": "mrr30k",
        },
        {
            "number": "08",
            "name": "Customer Success",
            "alias": "Activate Customer Success",
            "alias_example": "Activate Customer Success - ลูกค้าจะต่อสัญญาไหม",
            "activate": "Activate Customer Success",
            "icon": "bi-heart-fill",
            "color": "muted",
            "role": "ดูแลลูกค้าหลังการขาย, retention, churn prevention, upsell",
            "use_when": "ลูกค้า at risk / ต่อสัญญา / upsell / NPS",
            "stage": "mrr50k",
        },
        {
            "number": "09",
            "name": "Data Analyst",
            "alias": "Activate Data Analyst",
            "alias_example": "Activate Data Analyst - ทำไม leads เดือนนี้ลด",
            "activate": "Activate Data Analyst",
            "icon": "bi-bar-chart-fill",
            "color": "muted",
            "role": "วิเคราะห์ข้อมูล, dashboard, insight จาก sales/marketing data",
            "use_when": "metrics ขึ้น/ลงผิดปกติ / ต้องการ cohort analysis / trend",
            "stage": "mrr100k",
        },
        {
            "number": "10",
            "name": "Legal Advisor",
            "alias": "Activate Legal Advisor",
            "alias_example": "Activate Legal Advisor - ตรวจสัญญา service agreement นี้",
            "activate": "Activate Legal Advisor",
            "icon": "bi-file-earmark-text-fill",
            "color": "muted",
            "role": "สัญญา, PDPA compliance, NDA, ข้อพิพาท",
            "use_when": "ตรวจสัญญา / NDA / data privacy / compliance",
            "stage": "mrr200k",
        },
    ]

    stage_labels = {
        "now":     "ใช้งานได้เลย",
        "mrr30k":  "Unlock ที่ MRR ฿30K",
        "mrr50k":  "Unlock ที่ MRR ฿50K",
        "mrr100k": "Unlock ที่ MRR ฿100K",
        "mrr200k": "Unlock ที่ MRR ฿200K",
    }

    # Group agents by stage, preserving stage_labels order
    stages = []
    for stage_key, stage_label in stage_labels.items():
        members = [a for a in agents if a["stage"] == stage_key]
        if members:
            stages.append({
                "key": stage_key,
                "label": stage_label,
                "is_active": stage_key == "now",
                "agents": members,
            })

    return render(request, "dashboard/team.html", {
        "agents": agents,
        "stage_labels": stage_labels,
        "stages": stages,
    })


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


# ── Calendar ─────────────────────────────────────────────────────────────────

@staff_member_required
def calendar_view(request):
    now = timezone.now()
    events = []

    # ── 1. Published Articles (from DB) ──────────────────────────────────────
    published = Article.objects.filter(
        status="published", published_at__isnull=False
    ).values("title", "published_at")
    for art in published:
        events.append({
            "title": f"📝 {art['title'][:40]}",
            "start": timezone.localtime(art["published_at"]).date().isoformat(),
            "color": "#198754",
            "category": "article",
            "description": "บทความ published",
        })

    # ── 2. Lead activities (created_at) ──────────────────────────────────────
    leads_qs = ContactLead.objects.values("name", "company", "status", "created_at")
    for lead in leads_qs:
        company = lead["company"] or lead["name"]
        events.append({
            "title": f"👤 {company[:30]}",
            "start": timezone.localtime(lead["created_at"]).date().isoformat(),
            "color": "#0d6efd",
            "category": "lead",
            "description": f"Lead เข้า — {lead['status']}",
        })

    # ── 3+4. System events จาก DB (milestones + recurring) ──────────────────
    system_qs = CalendarEvent.objects.filter(is_system=True).values(
        "pk", "title", "start_datetime", "category", "description", "color", "is_completed", "assigned_to"
    )
    for evt in system_qs:
        events.append({
            "id":           evt["pk"],
            "title":        evt["title"],
            "start":        timezone.localtime(evt["start_datetime"]).date().isoformat(),
            "category":     evt["category"],
            "description":  evt["description"],
            "is_completed": evt["is_completed"],
            "assigned_to":  evt["assigned_to"],
        })

    # ── 5. Content Backlog scheduled items ───────────────────────────────────
    backlog_items = _parse_backlog()
    pending_items = [i for i in backlog_items if i["status"] in ("pending", "review")]
    # Schedule pending items 1 per week starting next Monday
    next_monday = now.date() + timedelta(days=(7 - now.weekday()) % 7 or 7)
    for idx, item in enumerate(pending_items):
        sched_date = next_monday + timedelta(weeks=idx)
        status_icon = "👁️" if item["status"] == "review" else "🗓️"
        events.append({
            "title": f"{status_icon} {item['topic'][:38]}",
            "start": sched_date.isoformat(),
            "color": "#856404" if item["status"] == "review" else "#495057",
            "category": "backlog",
            "description": f"[{item['status']}] {item['keyword']}",
        })

    # ── 6. Calendar stats สำหรับ Stat Cards ─────────────────────────────────
    _sys = CalendarEvent.objects.filter(is_system=True)
    cal_stats = {
        "total":   _sys.count(),
        "done":    _sys.filter(is_completed=True).count(),
        "pending": _sys.filter(is_completed=False).count(),
        "by_cat": {
            c: _sys.filter(category=c).count()
            for c in ["action", "milestone", "recurring", "content_plan", "delivery", "meeting"]
        },
    }

    return render(request, "dashboard/calendar.html", {
        "events_json":       json.dumps(events, ensure_ascii=False),
        "category_choices":  CalendarEvent.CATEGORY_CHOICES,
        "cal_stats":         cal_stats,
    })


# ── Settings ─────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


def _read_env():
    """Read .env key-value pairs as dict."""
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def _write_env_key(key, value):
    """Update or append a single key in .env (preserves all other lines)."""
    text = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""
    lines = text.splitlines()
    pattern = re.compile(rf"^{re.escape(key)}\s*=")
    replaced = False
    new_lines = []
    for ln in lines:
        if pattern.match(ln):
            new_lines.append(f"{key}={value}")
            replaced = True
        else:
            new_lines.append(ln)
    if not replaced:
        new_lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


@staff_member_required
def settings_index(request):
    env = _read_env()
    use_mysql = env.get("USE_MYSQL", "False").lower() == "true"
    return render(request, "dashboard/settings.html", {
        "use_mysql":    use_mysql,
        "db_host":      env.get("DB_HOST", ""),
        "db_port":      env.get("DB_PORT", "3306"),
        "db_name":      env.get("DB_NAME", ""),
        "db_user":      env.get("DB_USER", ""),
        "db_pass_set":  bool(env.get("DB_PASSWORD", "")),
        "tab":          "database",
    })


@staff_member_required
@require_POST
def settings_test_db(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    host     = data.get("host", "").strip()
    port     = int(data.get("port") or 3306)
    name     = data.get("name", "").strip()
    user     = data.get("user", "").strip()
    password = data.get("password", "")

    if not all([host, name, user]):
        return JsonResponse({"ok": False, "error": "Host, Database Name และ Username ต้องกรอกให้ครบ"})

    try:
        import pymysql
        conn = pymysql.connect(
            host=host, port=port, db=name,
            user=user, password=password,
            connect_timeout=5,
        )
        conn.close()
        return JsonResponse({"ok": True, "message": f"Connected — MySQL at {host}:{port}/{name}"})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)})


@staff_member_required
@require_POST
def settings_save_db(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    use_mysql = data.get("use_mysql", False)
    _write_env_key("USE_MYSQL", "True" if use_mysql else "False")

    if use_mysql:
        _write_env_key("DB_HOST",     data.get("host", "").strip())
        _write_env_key("DB_PORT",     str(data.get("port") or 3306))
        _write_env_key("DB_NAME",     data.get("name", "").strip())
        _write_env_key("DB_USER",     data.get("user", "").strip())
        password = data.get("password", "")
        if password:
            _write_env_key("DB_PASSWORD", password)

    return JsonResponse({"ok": True, "message": "บันทึกลง .env แล้ว — กรุณา restart runserver"})


# ── Calendar API ─────────────────────────────────────────────────────────────


@staff_member_required
def api_calendar_events(request):
    if request.method == "GET":
        start = request.GET.get("start")
        end   = request.GET.get("end")
        qs = CalendarEvent.objects.filter(created_by=request.user)
        if start:
            qs = qs.filter(start_datetime__gte=start)
        if end:
            qs = qs.filter(start_datetime__lte=end)
        return JsonResponse([e.to_fc() for e in qs], safe=False)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        title = data.get("title", "").strip()
        start = data.get("start")
        if not title or not start:
            return JsonResponse({"error": "title และ start จำเป็น"}, status=400)

        evt = CalendarEvent.objects.create(
            title       = title,
            start_datetime = parse_datetime(start) or timezone.now(),
            end_datetime   = parse_datetime(data["end"]) if data.get("end") else None,
            all_day     = data.get("allDay", True),
            category    = data.get("category", "general"),
            description = data.get("description", ""),
            color       = data.get("color", ""),
            is_system   = False,
            created_by  = request.user,
        )
        return JsonResponse(evt.to_fc(), status=201)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@staff_member_required
def api_calendar_event_detail(request, pk):
    try:
        evt = CalendarEvent.objects.get(pk=pk)
    except CalendarEvent.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    # is_system events: staff ทุกคน edit ได้
    # user events: เฉพาะ created_by == request.user
    if not evt.is_system and evt.created_by != request.user:
        return JsonResponse({"error": "Not found"}, status=404)

    if request.method in ("PUT", "PATCH"):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if "title" in data:
            evt.title = data["title"].strip() or evt.title
        if "start" in data and data["start"]:
            evt.start_datetime = parse_datetime(data["start"]) or evt.start_datetime
        if "end" in data:
            evt.end_datetime = parse_datetime(data["end"]) if data["end"] else None
        if "allDay" in data:
            evt.all_day = data["allDay"]
        if "category" in data:
            evt.category = data["category"]
        if "description" in data:
            evt.description = data["description"]
        if "color" in data:
            evt.color = data["color"]
        if "is_completed" in data:
            evt.is_completed = bool(data["is_completed"])
        if "assigned_to" in data:
            evt.assigned_to = data["assigned_to"]
        evt.save()
        return JsonResponse(evt.to_fc())

    if request.method == "DELETE":
        evt.delete()
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)
