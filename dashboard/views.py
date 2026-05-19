import json
import os
import re
from datetime import date, timedelta
from pathlib import Path
from django.utils.dateparse import parse_datetime

from django.conf import settings
from django.contrib import messages
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
from blog.models import Article, Category, Tag
from blog.forms import ArticleForm
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
        "description": "แผนพัฒนา Feature ทั้งหมด 29 เมนู — จากการประชุมทีม 14 AI Agents พร้อม Data Model และ KPI",
        "audience": "owner",
        "bi_icon": "bi-map-fill",
    },
]


@staff_member_required
def coming_soon(request):
    return render(request, "dashboard/coming_soon.html", {
        "page_title": "Coming Soon",
    })


@staff_member_required
def kpi_dashboard(request):
    from crm.models import Customer, Renewal
    from finance.models import Invoice
    from pages.models import ContactLead

    today = timezone.now().date()
    first_of_month = today.replace(day=1)

    # MRR = sum of active customer contract_value (monthly approximation)
    customers = Customer.objects.filter(is_active=True)
    mrr = customers.aggregate(t=Sum("contract_value"))["t"] or 0
    total_customers = customers.count()

    # Churn: customers churned this month (contract ended this month)
    churned = customers.filter(contract_end__lt=today, contract_end__gte=first_of_month).count()
    churn_rate = round(churned / total_customers * 100, 1) if total_customers else 0

    # Health distribution
    healthy = customers.filter(health_score__gte=70).count()
    at_risk = customers.filter(health_score__lt=40).count()

    # Lead conversion
    total_leads = ContactLead.objects.count()
    won_leads = ContactLead.objects.filter(status="closed_won").count()
    conversion_rate = round(won_leads / total_leads * 100, 1) if total_leads else 0

    # Revenue this month (paid invoices)
    revenue_mtd = Invoice.objects.filter(
        status="paid", paid_at__date__gte=first_of_month
    ).aggregate(t=Sum("total_payable"))["t"] or 0

    # Renewals at risk (30 days)
    renewals_at_risk = Renewal.objects.filter(
        renewal_date__lte=today + timedelta(days=30),
        renewal_date__gte=today,
        status__in=["upcoming", "at_risk"]
    ).count()

    # NPS average
    from django.db.models import Avg
    avg_nps = customers.aggregate(n=Avg("nps_score"))["n"] or 0

    return render(request, "dashboard/kpi_dashboard.html", {
        "mrr": mrr,
        "total_customers": total_customers,
        "churn_rate": churn_rate,
        "healthy": healthy,
        "at_risk": at_risk,
        "conversion_rate": conversion_rate,
        "revenue_mtd": revenue_mtd,
        "renewals_at_risk": renewals_at_risk,
        "avg_nps": round(avg_nps, 1),
        "today": today,
    })



@staff_member_required
def design_system_view(request):
    spacings = [(f"sp-{n}", n * 4) for n in [1, 2, 3, 4, 6, 8, 12, 16]]
    icons = [
        ("bi-people-fill", "Leads"), ("bi-kanban-fill", "Pipeline"), ("bi-people", "Customers"),
        ("bi-arrow-repeat", "Renewals"), ("bi-file-earmark-text", "Quote"), ("bi-megaphone", "Campaign"),
        ("bi-calendar3", "Calendar"), ("bi-pencil-square", "Blog"), ("bi-search", "Keywords"),
        ("bi-receipt", "Invoice"), ("bi-wallet2", "Expense"), ("bi-currency-exchange", "Revenue"),
        ("bi-bar-chart-fill", "Analytics"), ("bi-speedometer2", "KPI"), ("bi-file-earmark-lock2", "Contract"),
        ("bi-robot", "AI Project"), ("bi-collection", "Prompts"), ("bi-clipboard2-check", "QA"),
        ("bi-palette", "Design"), ("bi-chat-square-text", "Standup"), ("bi-plus-lg", "Add"),
        ("bi-pencil", "Edit"), ("bi-trash", "Delete"), ("bi-check-lg", "Done"),
    ]
    return render(request, "dashboard/design_system.html", {
        "spacings": spacings,
        "icons": icons,
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

    # ── Analytics data (merged) ──────────────────────────────────────────────
    from django.db.models.functions import TruncWeek
    from blog.models import Category

    leads_by_source = list(
        ContactLead.objects.values("source")
        .annotate(count=Count("id")).order_by("-count")
    )
    status_order = ["new", "contacted", "qualified", "proposal", "closed_won", "closed_lost"]
    status_counts = {
        row["status"]: row["count"]
        for row in ContactLead.objects.values("status").annotate(count=Count("id"))
    }
    leads_funnel = [
        {"status": s, "label": dict(ContactLead.STATUS_CHOICES).get(s, s), "count": status_counts.get(s, 0)}
        for s in status_order
    ]
    top_articles_views = list(
        Article.objects.filter(status="published").order_by("-views_count")
        .values("title", "views_count", "category__name")[:8]
    )
    weeks_ago_12 = now - timedelta(weeks=12)
    weekly_leads_map = {
        row["week"].date().isoformat(): row["count"]
        for row in ContactLead.objects.filter(created_at__gte=weeks_ago_12)
        .annotate(week=TruncWeek("created_at")).values("week").annotate(count=Count("id"))
    }
    weekly_articles_map = {
        row["week"].date().isoformat(): row["count"]
        for row in Article.objects.filter(status="published", published_at__gte=weeks_ago_12)
        .annotate(week=TruncWeek("published_at")).values("week").annotate(count=Count("id"))
    }
    week_labels, week_leads_data, week_articles_data = [], [], []
    for i in range(11, -1, -1):
        wm = (now - timedelta(weeks=i)).date()
        wm = wm - timedelta(days=wm.weekday())
        week_labels.append(wm.strftime("%d %b"))
        week_leads_data.append(weekly_leads_map.get(wm.isoformat(), 0))
        week_articles_data.append(weekly_articles_map.get(wm.isoformat(), 0))

    return render(request, "dashboard/index.html", {
        "leads_today": leads_today, "leads_today_sources": leads_today_sources,
        "active_pipeline": active_pipeline, "pipeline_by_status": pipeline_by_status,
        "total_views": total_views,
        "articles_this_week": articles_this_week, "article_weekly_goal": article_weekly_goal,
        "mql_total": mql_total, "today_actions": today_actions,
        "chart_labels": chart_labels, "chart_data": chart_data,
        "leads_this_month": leads_this_month, "leads_delta_pct": leads_delta_pct,
        "published_articles": published_articles, "active_cases": active_cases,
        "recent_leads": recent_leads, "top_articles": top_articles,
        # analytics merged
        "leads_by_source": leads_by_source,
        "source_labels":   json.dumps([r["source"] for r in leads_by_source]),
        "source_data":     json.dumps([r["count"]  for r in leads_by_source]),
        "leads_funnel":    leads_funnel,
        "funnel_labels":   json.dumps([r["label"] for r in leads_funnel]),
        "funnel_data":     json.dumps([r["count"] for r in leads_funnel]),
        "top_articles_views": top_articles_views,
        "week_labels":        json.dumps(week_labels),
        "week_leads_data":    json.dumps(week_leads_data),
        "week_articles_data": json.dumps(week_articles_data),
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

    from marketing.models import ContentBacklog
    backlog_pending = list(ContentBacklog.objects.exclude(status="done").order_by("num"))
    backlog_done    = list(ContentBacklog.objects.filter(status="done").order_by("num"))

    return render(request, "dashboard/blog_list.html", {
        "articles":        articles,
        "status_filter":   status_filter,
        "draft_count":     draft_count,
        "backlog_pending": backlog_pending,
        "backlog_done":    backlog_done,
        "backlog_total":   ContentBacklog.objects.count(),
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


@staff_member_required
def article_edit(request, pk=None):
    article = get_object_or_404(Article, pk=pk) if pk else None
    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            obj = form.save(commit=False)
            if not pk:
                obj.author = request.user
            if obj.status == "published" and not obj.published_at:
                obj.published_at = timezone.now()
            obj.save()
            form.save_m2m()
            return redirect("dashboard:article_edit", pk=obj.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, "dashboard/article_edit.html", {
        "form": form,
        "article": article,
        "is_new": article is None,
        "categories": Category.objects.order_by("display_order", "name"),
        "all_articles": Article.objects.order_by("-created_at")[:50],
    })


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

    PENDING_COLOR = "#3b82f6"   # Blue-500 — งานยังไม่ทำ
    DONE_COLOR    = "#64748b"   # Slate-500 — งานเสร็จแล้ว

    # ── 1. Published Articles (from DB) ──────────────────────────────────────
    published = Article.objects.filter(
        status="published", published_at__isnull=False
    ).values("title", "published_at")
    for art in published:
        events.append({
            "title": f"📝 {art['title'][:40]}",
            "start": timezone.localtime(art["published_at"]).date().isoformat(),
            "color":        DONE_COLOR,
            "is_completed": True,
            "category": "article",
            "description": "บทความ published",
        })

    # ── 2. Lead activities (created_at) ──────────────────────────────────────
    leads_qs = ContactLead.objects.values("name", "company", "status", "created_at")
    for lead in leads_qs:
        company  = lead["company"] or lead["name"]
        is_done  = lead["status"] in ("closed_won", "closed_lost")
        events.append({
            "title": f"👤 {company[:30]}",
            "start": timezone.localtime(lead["created_at"]).date().isoformat(),
            "color":        DONE_COLOR if is_done else PENDING_COLOR,
            "is_completed": is_done,
            "category": "lead",
            "description": f"Lead เข้า — {lead['status']}",
        })

    # ── 3+4. System events จาก DB (milestones + recurring + action) ──────────
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
            "color":        PENDING_COLOR,
            "is_completed": False,
            "category": "backlog",
            "description": f"[{item['status']}] {item['keyword']}",
        })

    # ── 6. Calendar stats สำหรับ Stat Cards ─────────────────────────────────
    _sys = CalendarEvent.objects.filter(is_system=True)
    _sys_total = _sys.count()
    cal_stats = {
        "total":   _sys_total,
        "done":    _sys.filter(is_completed=True).count(),
        "pending": _sys.filter(is_completed=False).count(),
        "by_cat": {
            c: _sys.filter(category=c).count()
            for c in ["action", "milestone", "recurring", "content_plan", "delivery", "meeting"]
        },
    }

    from dashboard.models import Note
    notes = Note.objects.all()

    # Tooltip description ของแต่ละ category
    cat_tooltip_map = {
        "general":      "งานทั่วไปที่สร้างเอง",
        "priority":     "งานสำคัญที่ต้องทำก่อน",
        "meeting":      "นัดประชุม ทั้งภายในและภายนอก",
        "delivery":     "งานส่งมอบให้ลูกค้า",
        "personal":     "งานส่วนตัว ไม่เกี่ยวธุรกิจ",
        "milestone":    "แผนงานหลัก Roadmap ธุรกิจ",
        "action":       "งาน Action ที่ต้องลงมือทำ",
        "recurring":    "งานประจำที่เกิดซ้ำทุกวัน/สัปดาห์",
        "content_plan": "แผน Content สำหรับ Blog และ Social",
        "backlog":      "หัวข้อ Content ที่รอเขียน",
        "article":      "บทความที่ publish แล้ว",
        "lead":         "Leads ที่เข้ามาในระบบ",
    }

    # Icon mapping for filter toolbar
    cat_icon_map = {
        "general":      "bi-pin-fill",
        "priority":     "bi-exclamation-circle-fill",
        "meeting":      "bi-people-fill",
        "delivery":     "bi-box-seam",
        "personal":     "bi-person-heart",
        "milestone":    "bi-flag-fill",
        "action":       "bi-lightning-charge-fill",
        "recurring":    "bi-arrow-repeat",
        "content_plan": "bi-file-text-fill",
        "backlog":      "bi-calendar2-week",
        "article":      "bi-newspaper",
        "lead":         "bi-person-check-fill",
    }
    # Count งานแต่ละ category จาก DB
    from django.db.models import Count as DbCount
    cat_counts = {
        row["category"]: row["c"]
        for row in CalendarEvent.objects.filter(is_system=True)
                                        .values("category")
                                        .annotate(c=DbCount("id"))
    }
    # article อยู่ใน CalendarEvent แล้ว (sync จาก signal) — ไม่บวกซ้ำ
    cat_counts["article"] = _sys.filter(category="article").count()

    # total_count = เดียวกับ cal_stats.total
    total_count = _sys_total

    # สร้าง category_filters จาก CATEGORY_CHOICES + article + lead
    _extra_cats = []  # article อยู่ใน CATEGORY_CHOICES แล้ว
    category_filters = [
        {
            "value":   value,
            "label":   label,
            "icon":    cat_icon_map.get(value, "bi-circle"),
            "count":   cat_counts.get(value, 0),
            "tooltip": cat_tooltip_map.get(value, label),
        }
        for value, label in list(CalendarEvent.CATEGORY_CHOICES) + _extra_cats
        if cat_counts.get(value, 0) > 0   # แสดงเฉพาะ category ที่มี event
    ]

    return render(request, "dashboard/calendar.html", {
        "events_json":       json.dumps(events, ensure_ascii=False),
        "category_choices":  CalendarEvent.CATEGORY_CHOICES,
        "category_filters":  category_filters,
        "total_count":       total_count,
        "cal_stats":         cal_stats,
        "notes":             notes,
        "note_colors":       Note.Color.choices,
        "docs_count":        len(INTERNAL_DOCS),
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

    # Auto-restart peyo-agent service (production) หรือแจ้ง dev
    import subprocess, shutil
    restarted = False
    if shutil.which("systemctl"):
        result = subprocess.run(
            ["sudo", "systemctl", "restart", "peyo-agent"],
            capture_output=True, timeout=15
        )
        restarted = (result.returncode == 0)

    if restarted:
        msg = "บันทึกและ restart service แล้ว — การตั้งค่าใหม่มีผลทันที"
    else:
        msg = "บันทึกลง .env แล้ว — กรุณา restart server: sudo systemctl restart peyo-agent"

    return JsonResponse({"ok": True, "message": msg})


# ── Notes API ────────────────────────────────────────────────────────────────

@staff_member_required
def api_notes(request):
    from dashboard.models import Note
    if request.method == "GET":
        notes = list(Note.objects.values("id", "title", "content", "color", "pinned", "updated_at"))
        for n in notes:
            n["updated_at"] = n["updated_at"].strftime("%d %b %Y %H:%M")
        return JsonResponse(notes, safe=False)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        note = Note.objects.create(
            title   = data.get("title", "").strip() or "Note",
            content = data.get("content", "").strip(),
            color   = data.get("color", "gold"),
            pinned  = data.get("pinned", False),
        )
        return JsonResponse({"id": note.pk, "ok": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)


@staff_member_required
def api_note_detail(request, pk):
    from dashboard.models import Note
    note = get_object_or_404(Note, pk=pk)

    if request.method == "PATCH":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        if "title"   in data: note.title   = data["title"].strip() or note.title
        if "content" in data: note.content = data["content"]
        if "color"   in data: note.color   = data["color"]
        if "pinned"  in data: note.pinned  = data["pinned"]
        note.save()
        return JsonResponse({"ok": True})

    if request.method == "DELETE":
        note.delete()
        return JsonResponse({"ok": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)


# ── Calendar API ─────────────────────────────────────────────────────────────


@staff_member_required
def api_calendar_events(request):
    if request.method == "GET":
        start = request.GET.get("start")
        end   = request.GET.get("end")
        # ดึง user events: created_by=request.user หรือ created_by=None (สร้างจาก management command)
        qs = CalendarEvent.objects.filter(
            Q(created_by=request.user) | Q(created_by__isnull=True),
            is_system=False,
        )
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
            title          = title,
            start_datetime = parse_datetime(start) or timezone.now(),
            end_datetime   = parse_datetime(data["end"]) if data.get("end") else None,
            all_day        = data.get("allDay", True),
            category       = data.get("category", "general"),
            description    = data.get("description", ""),
            color          = data.get("color", ""),
            assigned_to    = data.get("assigned_to", ""),
            is_system      = False,
            created_by     = request.user,
        )
        return JsonResponse(evt.to_fc(), status=201)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@staff_member_required
def api_ep_articles(request):
    """คืน published articles ที่ title ขึ้นต้นด้วย 'EP X:' → { "EP 4": "/blog/slug/" }"""
    import re as _re
    from blog.models import Article
    result = {}
    for a in Article.objects.filter(status="published").only("title", "slug"):
        m = _re.match(r"^(EP \d+):", a.title)
        if m:
            result[m.group(1)] = f"/blog/{a.slug}/"
    return JsonResponse(result)


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


# ── Website Content Manager ───────────────────────────────────────────────────

@staff_member_required
def website_content_view(request):
    from pages.models import (Service, SiteSetting, ContactTopic,
                              AboutPage, AboutStat, AboutValue, AboutCheckpoint, AboutExpertise,
                              HomePage, HomePain, HomeProcess, HomeTestimonial, HomeFAQ)
    from portfolio.models import CaseStudy
    from blog.models import Article
    from marketing.models import ContentBacklog
    backlog_qs = ContentBacklog.objects.exclude(status="done").filter(articles__isnull=True).order_by("num")[:30]
    return render(request, "dashboard/website_content.html", {
        "services":     Service.objects.all().order_by("display_order"),
        "portfolio":    CaseStudy.objects.all().order_by("display_order", "-published_at"),
        "about_page":   AboutPage.get(),
        "home_page":    HomePage.get(),
        "home_pains":   HomePain.objects.all(),
        "home_process": HomeProcess.objects.all(),
        "home_testis":  HomeTestimonial.objects.all(),
        "home_faqs":    HomeFAQ.objects.all(),
        "stats":        AboutStat.objects.all(),
        "values":       AboutValue.objects.all(),
        "checkpoints":  AboutCheckpoint.objects.all(),
        "expertise":    AboutExpertise.objects.all(),
        "site":         SiteSetting.get(),
        "topics":       ContactTopic.objects.all(),
        "articles":     Article.objects.all().order_by("-created_at")[:20],
        "backlog_items": backlog_qs,
        "active_tab":   request.GET.get("tab", "home"),
    })


@staff_member_required
def blog_category_add(request):
    """Quick-add category via AJAX — ใช้จากหน้า article edit"""
    if request.method == "POST":
        import json
        from blog.models import Category
        from django.utils.text import slugify
        data = json.loads(request.body)
        name  = data.get("name", "").strip()
        color = data.get("color", "secondary")
        if not name:
            return JsonResponse({"ok": False, "error": "กรุณาใส่ชื่อหมวดหมู่"}, status=400)
        slug = slugify(name)[:120] or f"cat-{name[:20]}"
        i = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f"{slugify(name)[:110]}-{i}"; i += 1
        cat = Category.objects.create(name=name, slug=slug, color=color)
        return JsonResponse({"ok": True, "id": cat.pk, "name": cat.name})
    return JsonResponse({"ok": False}, status=405)


@staff_member_required
def portfolio_image_add(request, pk):
    from portfolio.models import CaseStudy, CaseStudyImage
    from django.shortcuts import get_object_or_404
    cs = get_object_or_404(CaseStudy, pk=pk)
    if request.method == "POST" and request.FILES.get("image"):
        img = CaseStudyImage.objects.create(
            case_study   = cs,
            image        = request.FILES["image"],
            caption      = request.POST.get("caption", "").strip(),
            display_order= CaseStudyImage.objects.filter(case_study=cs).count(),
        )
        return JsonResponse({
            "ok": True, "id": img.pk,
            "url": img.image.url,
            "caption": img.caption,
        })
    return JsonResponse({"ok": False, "error": "ไม่มีไฟล์"}, status=400)


@staff_member_required
def portfolio_image_delete(request, pk):
    from portfolio.models import CaseStudyImage
    from django.shortcuts import get_object_or_404
    if request.method == "POST":
        img = get_object_or_404(CaseStudyImage, pk=pk)
        img.image.delete(save=False)
        img.delete()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False}, status=405)


@staff_member_required
def blog_tag_delete(request, pk):
    if request.method == "POST":
        from blog.models import Tag
        from django.shortcuts import get_object_or_404
        tag = get_object_or_404(Tag, pk=pk)
        name = tag.name
        tag.delete()
        return JsonResponse({"ok": True, "name": name})
    return JsonResponse({"ok": False}, status=405)


@staff_member_required
def blog_category_delete(request, pk):
    if request.method == "POST":
        from blog.models import Category
        from django.shortcuts import get_object_or_404
        cat = get_object_or_404(Category, pk=pk)
        if cat.articles.exists():
            return JsonResponse({"ok": False, "error": f'มีบทความอยู่ใน "{cat.name}" ไม่สามารถลบได้'}, status=400)
        name = cat.name
        cat.delete()
        return JsonResponse({"ok": True, "name": name})
    return JsonResponse({"ok": False}, status=405)


@staff_member_required
def blog_tag_add(request):
    if request.method == "POST":
        import json
        from blog.models import Tag
        from django.utils.text import slugify
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        if not name:
            return JsonResponse({"ok": False, "error": "กรุณาใส่ชื่อ Tag"}, status=400)
        if Tag.objects.filter(name=name).exists():
            tag = Tag.objects.get(name=name)
            return JsonResponse({"ok": True, "id": tag.pk, "name": tag.name, "exists": True})
        slug = slugify(name)[:70] or f"tag-{name[:20]}"
        i = 1
        while Tag.objects.filter(slug=slug).exists():
            slug = f"{slugify(name)[:60]}-{i}"; i += 1
        tag = Tag.objects.create(name=name, slug=slug)
        return JsonResponse({"ok": True, "id": tag.pk, "name": tag.name})
    return JsonResponse({"ok": False}, status=405)


@staff_member_required
def website_service_create(request):
    from pages.models import Service
    if request.method == "POST":
        name  = request.POST.get("name", "บริการใหม่").strip() or "บริการใหม่"
        # สร้าง slug จากชื่อ
        import re
        slug = re.sub(r"[^\w\s-]", "", name.lower())
        slug = re.sub(r"\s+", "-", slug).strip("-")
        # ป้องกัน slug ซ้ำ
        base_slug, i = slug, 1
        while Service.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"; i += 1
        svc = Service.objects.create(
            name=name, slug=slug,
            tagline=request.POST.get("tagline", "").strip(),
            description=request.POST.get("description", "").strip(),
            icon=request.POST.get("icon", "bi-stars").strip(),
            cover_image_url=request.POST.get("cover_image_url", "").strip(),
            price_start=int(request.POST.get("price_start", 0) or 0),
            price_label=request.POST.get("price_label", "เริ่มต้น").strip(),
            features=request.POST.get("features", "").strip(),
            display_order=int(request.POST.get("display_order", 99) or 99),
            is_featured="is_featured" in request.POST,
            status=request.POST.get("status", "draft"),
        )
        messages.success(request, f'สร้าง "{svc.name}" แล้ว')
        return redirect("dashboard:website_service_edit", pk=svc.pk)
    # GET — แสดงฟอร์มเปล่า
    from pages.models import Service
    blank = Service(
        name="", slug="", tagline="", description="",
        icon="bi-stars", cover_image_url="",
        price_start=0, price_label="เริ่มต้น",
        features="", display_order=99, status="draft",
    )
    return render(request, "dashboard/service_edit.html", {
        "svc": blank,
        "is_create": True,
        "all_services": Service.objects.all().order_by("display_order"),
    })


@staff_member_required
def website_service_edit(request, pk):
    from pages.models import Service
    from django.shortcuts import get_object_or_404
    svc = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        svc.name            = request.POST.get("name", svc.name).strip()
        svc.slug            = request.POST.get("slug", svc.slug).strip()
        svc.tagline         = request.POST.get("tagline", svc.tagline).strip()
        svc.description     = request.POST.get("description", svc.description).strip()
        svc.icon            = request.POST.get("icon", svc.icon).strip()
        svc.cover_image_url = request.POST.get("cover_image_url", svc.cover_image_url).strip()
        svc.price_start     = int(request.POST.get("price_start", svc.price_start) or 0)
        svc.price_label     = request.POST.get("price_label", svc.price_label).strip()
        svc.features        = request.POST.get("features", svc.features).strip()
        svc.display_order   = int(request.POST.get("display_order", svc.display_order) or 0)
        svc.is_featured     = "is_featured" in request.POST
        svc.status          = request.POST.get("status", svc.status)
        svc.save()
        messages.success(request, f'บันทึก "{svc.name}" แล้ว')
        return redirect("dashboard:website_service_edit", pk=svc.pk)
    return render(request, "dashboard/service_edit.html", {
        "svc": svc,
        "all_services": Service.objects.all().order_by("display_order"),
    })


@staff_member_required
@require_POST
def website_service_toggle(request, pk):
    from pages.models import Service
    from django.shortcuts import get_object_or_404
    svc = get_object_or_404(Service, pk=pk)
    svc.status = "draft" if svc.status == "published" else "published"
    svc.save()
    return JsonResponse({"status": svc.status})


@staff_member_required
def website_portfolio_create(request):
    from portfolio.models import CaseStudy
    from portfolio.models import slugify_th
    if request.method == "POST":
        title = request.POST.get("project_title", "Case Study ใหม่").strip() or "Case Study ใหม่"
        slug  = slugify_th(title)[:220]
        base_slug, i = slug, 1
        while CaseStudy.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{i}"; i += 1
        cs = CaseStudy.objects.create(
            project_title  = title,
            slug           = slug,
            client_name    = request.POST.get("client_name", "").strip(),
            industry       = request.POST.get("industry", "other"),
            cover_image_url= request.POST.get("cover_image_url", "").strip(),
            problem        = request.POST.get("problem", "").strip(),
            solution       = request.POST.get("solution", "").strip(),
            result         = request.POST.get("result", "").strip(),
            roi_metric     = request.POST.get("roi_metric", "").strip(),
            testimonial    = request.POST.get("testimonial", "").strip(),
            testimonial_by = request.POST.get("testimonial_by", "").strip(),
            tech_stack     = request.POST.get("tech_stack", "").strip(),
            duration       = request.POST.get("duration", "").strip(),
            meta_title     = request.POST.get("meta_title", "").strip(),
            meta_description=request.POST.get("meta_description", "").strip(),
            display_order  = int(request.POST.get("display_order", 99) or 99),
            is_featured    = "is_featured" in request.POST,
            status         = request.POST.get("status", "draft"),
        )
        messages.success(request, f'สร้าง "{cs.project_title}" แล้ว')
        return redirect("dashboard:website_portfolio_edit", pk=cs.pk)
    blank = CaseStudy(
        project_title="", slug="", client_name="", industry="other",
        cover_image_url="", problem="", solution="", result="",
        roi_metric="", testimonial="", testimonial_by="",
        tech_stack="", duration="", meta_title="", meta_description="",
        display_order=99, status="draft",
    )
    return render(request, "dashboard/portfolio_edit.html", {
        "cs": blank, "is_create": True,
        "industry_choices": CaseStudy.INDUSTRY_CHOICES,
        "all_portfolio": CaseStudy.objects.all().order_by("display_order", "-published_at"),
    })


@staff_member_required
def website_portfolio_edit(request, pk):
    from portfolio.models import CaseStudy
    from django.shortcuts import get_object_or_404
    cs = get_object_or_404(CaseStudy, pk=pk)
    if request.method == "POST":
        cs.project_title   = request.POST.get("project_title", cs.project_title).strip()
        cs.slug            = request.POST.get("slug", cs.slug).strip()
        cs.client_name     = request.POST.get("client_name", cs.client_name).strip()
        cs.industry        = request.POST.get("industry", cs.industry)
        cs.cover_image_url = request.POST.get("cover_image_url", cs.cover_image_url).strip()
        cs.problem         = request.POST.get("problem", cs.problem).strip()
        cs.solution        = request.POST.get("solution", cs.solution).strip()
        cs.result          = request.POST.get("result", cs.result).strip()
        cs.roi_metric      = request.POST.get("roi_metric", cs.roi_metric).strip()
        cs.testimonial     = request.POST.get("testimonial", cs.testimonial).strip()
        cs.testimonial_by  = request.POST.get("testimonial_by", cs.testimonial_by).strip()
        cs.tech_stack      = request.POST.get("tech_stack", cs.tech_stack).strip()
        cs.duration        = request.POST.get("duration", cs.duration).strip()
        cs.meta_title      = request.POST.get("meta_title", cs.meta_title).strip()
        cs.meta_description= request.POST.get("meta_description", cs.meta_description).strip()
        cs.display_order   = int(request.POST.get("display_order", cs.display_order) or 0)
        cs.is_featured     = "is_featured" in request.POST
        cs.status          = request.POST.get("status", cs.status)
        cs.save()
        messages.success(request, f'บันทึก "{cs.project_title}" แล้ว')
        return redirect("dashboard:website_portfolio_edit", pk=cs.pk)
    return render(request, "dashboard/portfolio_edit.html", {
        "cs": cs, "is_create": False,
        "industry_choices": CaseStudy.INDUSTRY_CHOICES,
        "all_portfolio": CaseStudy.objects.all().order_by("display_order", "-published_at"),
    })


@staff_member_required
@require_POST
def website_portfolio_toggle(request, pk):
    from portfolio.models import CaseStudy
    from django.shortcuts import get_object_or_404
    cs = get_object_or_404(CaseStudy, pk=pk)
    cs.status = "draft" if cs.status == "published" else "published"
    cs.save()
    return JsonResponse({"status": cs.status})


@staff_member_required
@require_POST
def website_backlog_add(request):
    """เพิ่ม Content Backlog item ใหม่"""
    from marketing.models import ContentBacklog
    import json
    data    = json.loads(request.body)
    topic   = data.get("topic", "").strip()
    keyword = data.get("keyword", "").strip()
    priority= data.get("priority", "P2")
    if not topic:
        return JsonResponse({"ok": False, "error": "กรุณาใส่หัวข้อ"}, status=400)
    num = (ContentBacklog.objects.order_by("-num").values_list("num", flat=True).first() or 0) + 1
    item = ContentBacklog.objects.create(
        num=num, topic=topic, keyword=keyword,
        priority=priority, status="pending",
    )
    return JsonResponse({
        "ok": True, "id": item.pk,
        "topic": item.topic, "keyword": item.keyword,
        "priority": item.priority, "status": item.status,
        "status_display": item.get_status_display(),
    })


@staff_member_required
@require_POST
def website_backlog_to_blog(request, pk):
    """ส่ง Backlog item เข้า Blog list ด้วย status=waiting"""
    from marketing.models import ContentBacklog
    from blog.models import Article, Category
    from django.shortcuts import get_object_or_404
    import re

    item = get_object_or_404(ContentBacklog, pk=pk)

    # ตรวจว่ามี Article ที่ link กับ backlog นี้แล้วหรือยัง
    if Article.objects.filter(backlog_ref=item).exists():
        messages.warning(request, f'"{item.topic[:40]}" อยู่ใน Blog list แล้ว')
        return redirect("/owner/website-content/?tab=blog")

    # สร้าง slug — ใช้ Django slugify (ASCII only) + fallback เป็น backlog-{pk}
    from django.utils.text import slugify
    slug_base = slugify(item.topic)[:180] or f"backlog-{item.pk}"
    slug = slug_base
    i = 1
    while Article.objects.filter(slug=slug).exists():
        slug = f"{slug_base}-{i}"; i += 1

    # ใช้ category แรกที่มี หรือสร้าง default
    cat = Category.objects.first()
    if not cat:
        cat = Category.objects.create(name="ทั่วไป", slug="general")

    article = Article.objects.create(
        title       = item.topic,
        slug        = slug,
        author      = request.user,
        category    = cat,
        status      = "waiting",
        backlog_ref = item,
        excerpt     = f"Target keyword: {item.keyword}" if item.keyword else "",
        content     = "",
    )
    # อัปเดต backlog status เป็น in_progress
    item.status = "in_progress"
    item.save()

    messages.success(request, f'เพิ่ม "{article.title[:40]}" เข้า Blog list แล้ว (รอเขียน)')
    return redirect("/owner/website-content/?tab=blog")


@staff_member_required
@require_POST
def website_article_toggle(request, pk):
    from blog.models import Article
    from django.shortcuts import get_object_or_404
    art = get_object_or_404(Article, pk=pk)
    art.status = "draft" if art.status == "published" else "published"
    art.save()
    return JsonResponse({"status": art.status})


@staff_member_required
@require_POST
def website_homepage_save(request):
    from pages.models import HomePage
    obj = HomePage.get()
    for f in ["hero_title","hero_subtitle","hero_cta_text","hero_cta2_text",
              "pain_title","pain_subtitle","process_title","process_subtitle",
              "testi_title","faq_title","cta_title","cta_subtitle","cta_button"]:
        val = request.POST.get(f, "").strip()
        if val:
            setattr(obj, f, val)
    obj.save()
    messages.success(request, "บันทึกเนื้อหาหน้าแรกแล้ว")
    return redirect("/owner/website-content/?tab=home")


@staff_member_required
@require_POST
def website_homepain_save(request, pk):
    from pages.models import HomePain
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(HomePain, pk=pk)
    obj.icon        = request.POST.get("icon", obj.icon).strip()
    obj.title       = request.POST.get("title", obj.title).strip()
    obj.description = request.POST.get("description", obj.description).strip()
    obj.save()
    messages.success(request, f'บันทึก "{obj.title}" แล้ว')
    return redirect("/owner/website-content/?tab=home")


@staff_member_required
@require_POST
def website_homeprocess_save(request, pk):
    from pages.models import HomeProcess
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(HomeProcess, pk=pk)
    obj.step_num    = request.POST.get("step_num", obj.step_num).strip()
    obj.title       = request.POST.get("title", obj.title).strip()
    obj.description = request.POST.get("description", obj.description).strip()
    obj.icon        = request.POST.get("icon", obj.icon).strip()
    obj.save()
    messages.success(request, f'บันทึก Step {obj.step_num} แล้ว')
    return redirect("/owner/website-content/?tab=home")


@staff_member_required
@require_POST
def website_hometesti_save(request, pk):
    from pages.models import HomeTestimonial
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(HomeTestimonial, pk=pk)
    obj.quote      = request.POST.get("quote", obj.quote).strip()
    obj.author     = request.POST.get("author", obj.author).strip()
    obj.role       = request.POST.get("role", obj.role).strip()
    obj.avatar_url = request.POST.get("avatar_url", obj.avatar_url).strip()
    obj.save()
    messages.success(request, f'บันทึก "{obj.author}" แล้ว')
    return redirect("/owner/website-content/?tab=home")


@staff_member_required
@require_POST
def website_homefaq_save(request, pk):
    from pages.models import HomeFAQ
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(HomeFAQ, pk=pk)
    obj.question = request.POST.get("question", obj.question).strip()
    obj.answer   = request.POST.get("answer", obj.answer).strip()
    obj.save()
    messages.success(request, "บันทึก FAQ แล้ว")
    return redirect("/owner/website-content/?tab=home")


@staff_member_required
@require_POST
def website_aboutpage_save(request):
    from pages.models import AboutPage
    obj = AboutPage.get()
    obj.hero_title      = request.POST.get("hero_title", obj.hero_title).strip()
    obj.hero_lead       = request.POST.get("hero_lead", obj.hero_lead).strip()
    obj.mission_title   = request.POST.get("mission_title", obj.mission_title).strip()
    obj.mission_body    = request.POST.get("mission_body", obj.mission_body).strip()
    obj.cta_title       = request.POST.get("cta_title", obj.cta_title).strip()
    obj.cta_subtitle    = request.POST.get("cta_subtitle", obj.cta_subtitle).strip()
    obj.cta_button_text = request.POST.get("cta_button_text", obj.cta_button_text).strip()
    obj.save()
    messages.success(request, "บันทึกเนื้อหาหน้า About แล้ว")
    return redirect("/owner/website-content/?tab=about")


@staff_member_required
@require_POST
def website_checkpoint_save(request, pk):
    from pages.models import AboutCheckpoint
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(AboutCheckpoint, pk=pk)
    obj.icon        = request.POST.get("icon", obj.icon).strip()
    obj.title       = request.POST.get("title", obj.title).strip()
    obj.description = request.POST.get("description", obj.description).strip()
    obj.save()
    messages.success(request, f'บันทึก "{obj.title}" แล้ว')
    return redirect("/owner/website-content/?tab=about")


@staff_member_required
@require_POST
def website_expertise_save(request, pk):
    from pages.models import AboutExpertise
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(AboutExpertise, pk=pk)
    obj.icon        = request.POST.get("icon", obj.icon).strip()
    obj.title       = request.POST.get("title", obj.title).strip()
    obj.description = request.POST.get("description", obj.description).strip()
    obj.tags        = request.POST.get("tags", obj.tags).strip()
    obj.save()
    messages.success(request, f'บันทึก "{obj.title}" แล้ว')
    return redirect("/owner/website-content/?tab=about")


@staff_member_required
@require_POST
def website_stats_save(request):
    from pages.models import AboutStat
    for key, val in request.POST.items():
        if key.startswith("number_"):
            AboutStat.objects.filter(pk=key.split("_", 1)[1]).update(number=val.strip())
        elif key.startswith("label_"):
            AboutStat.objects.filter(pk=key.split("_", 1)[1]).update(label=val.strip())
    messages.success(request, "บันทึกสถิติแล้ว")
    return redirect("/owner/website-content/?tab=stats")


@staff_member_required
@require_POST
def website_value_save(request, pk):
    from pages.models import AboutValue
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(AboutValue, pk=pk)
    obj.icon = request.POST.get("icon", obj.icon).strip()
    obj.title = request.POST.get("title", obj.title).strip()
    obj.description = request.POST.get("description", obj.description).strip()
    obj.save()
    messages.success(request, f'บันทึก "{obj.title}" แล้ว')
    return redirect("/owner/website-content/?tab=values")


@staff_member_required
@require_POST
def website_topic_save(request, pk):
    from pages.models import ContactTopic
    from django.shortcuts import get_object_or_404
    obj = get_object_or_404(ContactTopic, pk=pk)
    obj.icon  = request.POST.get("icon", obj.icon).strip()
    obj.name  = request.POST.get("name", obj.name).strip()
    obj.url   = request.POST.get("url", obj.url).strip()
    obj.save()
    messages.success(request, f'บันทึก "{obj.name}" แล้ว')
    return redirect("/owner/website-content/?tab=contact")


@staff_member_required
@require_POST
def website_contact_save(request):
    from pages.models import SiteSetting
    site = SiteSetting.get()
    fields = [
        "contact_email", "line_id", "phone", "business_hours",
        "contact_hero_title", "contact_hero_subtitle",
        "line_desc", "email_desc", "form_desc",
        "response_time", "guarantee",
    ]
    for f in fields:
        val = request.POST.get(f, "").strip()
        if val:
            setattr(site, f, val)
    site.save()
    messages.success(request, "บันทึกข้อมูล Contact แล้ว")
    return redirect("/owner/website-content/?tab=contact")
