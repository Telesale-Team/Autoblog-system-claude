import json
import re
from datetime import date, timedelta
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

    return render(request, "dashboard/team.html", {
        "agents": agents,
        "stage_labels": stage_labels,
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
            "start": art["published_at"].date().isoformat(),
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
            "start": lead["created_at"].date().isoformat(),
            "color": "#0d6efd",
            "category": "lead",
            "description": f"Lead เข้า — {lead['status']}",
        })

    # ── 3. Recurring schedule (Communication Cadence) ────────────────────────
    # Generate for current month + next 3 months
    for week_offset in range(14):
        monday = (now + timedelta(weeks=week_offset)).date()
        monday -= timedelta(days=monday.weekday())
        friday = monday + timedelta(days=4)
        first_of_month = monday.replace(day=1)

        # Daily stand-up Mon–Fri (show only Mon as weekly marker)
        events.append({
            "title": "☀️ Daily Stand-up",
            "start": monday.isoformat(),
            "color": "#6c757d",
            "category": "recurring",
            "description": "Daily 09:00 — แต่ละ agent ส่ง stand-up",
        })
        # Weekly review every Friday
        events.append({
            "title": "📊 Weekly Review",
            "start": friday.isoformat(),
            "color": "#6f42c1",
            "category": "recurring",
            "description": "ทุกศุกร์ 17:00 — CEO + CoS + 3 agents",
        })

    # Monthly review on 1st of each month (next 4 months)
    for m_offset in range(4):
        target = (now + timedelta(days=30 * m_offset)).date().replace(day=1)
        events.append({
            "title": "📅 Monthly Review",
            "start": target.isoformat(),
            "color": "#fd7e14",
            "category": "recurring",
            "description": "Monthly Business Review — all agents",
        })

    # ── 4. Milestones จาก docs/action_plan.html + docs/product_strategy.html ──
    # Day 1 = 2026-05-15 (วันเริ่ม)
    milestones = [
        # ═══ 60-DAY ACTION PLAN ═══════════════════════════════════════════════

        # Phase 1: Setup (Day 1-7) → May 15-21
        ("2026-05-15", "⚙️ [Day 1] ติดตั้ง Infrastructure", "milestone",
         "Install Node.js 24, OpenClaw, test localhost:18789"),
        ("2026-05-16", "📱 [Day 2] สร้าง LINE Official Account", "action",
         "Enable Messaging API + credentials"),
        ("2026-05-17", "🔗 [Day 3] เชื่อม LINE → OpenClaw", "action",
         "Channel Access Token + webhook"),
        ("2026-05-18", "🤖 [Day 4] เขียน System Prompt + 20+ FAQ", "action",
         "AI persona + knowledge base พร้อม"),
        ("2026-05-19", "🖥️ [Day 5] Deploy บน VPS ($6/เดือน)", "action",
         "DigitalOcean VPS + live demo server running"),
        ("2026-05-21", "✅ [Day 7] Demo Production-Ready", "milestone",
         "ทดสอบ 20+ scenarios ครบ — Gate 1 ผ่าน"),

        # Phase 2: Demo Creation (Day 8-14) → May 22-28
        ("2026-05-22", "🎬 [Day 8] สร้าง Demo 3 แบบ", "action",
         "E-commerce / Clinic / Hotel — 20+ FAQ each"),
        ("2026-05-24", "📹 [Day 10] ถ่าย Video Demo 60 วินาที", "action",
         "Thai voiceover + CapCut — highest conversion format"),
        ("2026-05-25", "📄 [Day 11] สร้าง Sales Materials", "action",
         "One-pager + Proposal template + Invoice + Service agreement"),
        ("2026-05-27", "🌐 [Day 13] ตั้ง LinkedIn + Facebook Page + Salepage", "action",
         "Online presence พร้อม — Netlify / GitHub Pages"),
        ("2026-05-28", "✅ [Day 14] Sales Materials ครบ", "milestone",
         "Demo + Content + Sales Kit — Gate 2 ผ่าน"),

        # Phase 3: Outreach (Day 15-28) → May 29 - Jun 11
        ("2026-05-29", "📢 [Day 15] Publish Content ชุดแรก", "action",
         "LinkedIn post + video, FB post, TikTok — 3 platforms"),
        ("2026-05-31", "📋 [Day 17] สร้าง Prospect List 100 ราย", "action",
         "50 คลินิก + 50 e-commerce shops → Google Sheets CRM"),
        ("2026-06-02", "💬 [Day 19] ส่ง Cold Message 30 ราย", "action",
         "Personalized DM Facebook/LINE — expect 10-20 replies"),
        ("2026-06-04", "👥 [Day 22] Join 3 Facebook Groups", "action",
         "SME / e-commerce / clinics — answer questions, build authority"),
        ("2026-06-08", "📞 [Day 25] Discovery Calls 3+ ราย", "milestone",
         "คุยกับ prospect ที่สนใจ — Gate 3 target"),
        ("2026-06-11", "✅ [Day 28] 3+ Discovery Calls Done", "milestone",
         "Pipeline มี qualified leads — เริ่ม Phase 4"),

        # Phase 4: Close (Day 29-38) → Jun 12-21
        ("2026-06-12", "🎯 [Day 29] Demo Calls + ส่ง Proposal", "action",
         "ส่ง proposal ให้ 1-2 hot leads"),
        ("2026-06-16", "🤝 [Day 33] รับ Deposit ฿10,000!", "milestone",
         "50% setup fee — Project greenlit, onboarding เริ่ม"),
        ("2026-06-21", "✍️ [Day 38] Contract Signed", "milestone",
         "HelloSign + ฿10K received — Gate 4 ผ่าน"),

        # Phase 5: Delivery (Day 39-52) → Jun 22 - Jul 5
        ("2026-06-22", "🔧 [Day 39] เริ่ม Customize ระบบ", "action",
         "Gather requirements + migrate FAQ + customize for customer"),
        ("2026-06-26", "🚀 [Day 44] Deploy บน Customer VPS", "action",
         "Configure OA + test all integrations"),
        ("2026-07-01", "🧪 [Day 47] User Acceptance Testing", "action",
         "Customer tests 3 วัน + feedback → fix issues"),
        ("2026-07-03", "📚 [Day 48] Training ทีมลูกค้า", "action",
         "Dashboard + FAQ updates + escalation process"),
        ("2026-07-05", "🟢 [Day 52] GO LIVE!", "milestone",
         "ระบบ production + 48h close monitoring — Gate 5 ผ่าน"),

        # Phase 6: Get Paid (Day 53-60) → Jul 6-13
        ("2026-07-06", "🧾 [Day 53] ส่ง Invoice #2 ฿10,000", "action",
         "Final payment immediately after go-live"),
        ("2026-07-08", "💰 [Day 55] รับเงินครบ + MRR เริ่ม!", "milestone",
         "Setup รวม ฿20,000 + MRR ฿3,000/เดือน เริ่มนับ"),
        ("2026-07-09", "📊 [Day 56] สร้าง Case Study", "action",
         "Metrics + screenshots + testimonial → LinkedIn"),
        ("2026-07-13", "🔄 [Day 60] เริ่ม Cycle 2", "milestone",
         "Follow-up pipeline + ขอ referral + target deal #2 by Day 90"),

        # ═══ PRODUCT ROADMAP 6 เดือน ════════════════════════════════════════

        # Month 1-2 (May-Jun): LINE AI Pro
        ("2026-05-29", "🚀 LINE AI Pro — Launch!", "milestone",
         "Product #1: Setup ฿20K | MRR ฿3K/เดือน | Delivery 1-2 สัปดาห์"),
        ("2026-06-30", "🎯 เป้าปิด 2-3 ดีลแรก", "milestone",
         "Month 2 target — MRR เริ่มนับ + สร้าง 1 Case Study"),

        # Month 3-4 (Jul-Aug): Clinic + Omni AI
        ("2026-07-15", "🏥 Private AI Clinic — Launch!", "milestone",
         "Product #2: Setup ฿80K | MRR ฿8K | ตลาด 30,000+ คลินิก | PDPA-safe"),
        ("2026-07-15", "📡 Omni AI Agent — Launch!", "milestone",
         "Product #3: Setup ฿50K | MRR ฿6K | LINE+FB+IG+TikTok"),
        ("2026-08-15", "🎯 เป้า MRR ฿20,000/เดือน", "milestone",
         "Month 4 revenue target — 3 partners acquired"),

        # Month 5-6 (Sep-Oct): Workflow + Team AI + Scale
        ("2026-09-15", "⚙️ AI Workflow Bot — Launch!", "milestone",
         "Product #4: Setup ฿35K | MRR ฿4.5K | Daily reports + CRM + alerts"),
        ("2026-09-15", "👥 Team AI Assistant — Launch!", "milestone",
         "Product #5: Setup ฿40K | MRR ฿5K | Slack/Teams/LINE | saves 30min/person/day"),
        ("2026-10-01", "📈 Google Ads เริ่ม (฿5K-15K/เดือน)", "action",
         "High-intent keywords — start after case study ready"),
        ("2026-10-15", "🎯 เป้า MRR ฿50,000/เดือน", "milestone",
         "Month 6 target: 15+ customers | 5 case studies | 5 partners"),
        ("2026-10-15", "🏆 Activate Data Analyst + Customer Success", "milestone",
         "MRR ฿50K+ → เพิ่ม agents ตาม revenue milestone"),

        # Quarterly
        ("2026-09-01", "🔄 Quarterly Planning Q3", "recurring",
         "2-day strategy session — ทบทวน MRR + product mix + channels"),
    ]

    for start, title, category, desc in milestones:
        events.append({
            "title": title,
            "start": start,
            "category": category,
            "description": desc,
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

    return render(request, "dashboard/calendar.html", {
        "events_json": json.dumps(events, ensure_ascii=False),
    })
