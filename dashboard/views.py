from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone

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
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    leads_this_month = ContactLead.objects.filter(created_at__gte=month_start).count()
    leads_last_month = ContactLead.objects.filter(
        created_at__gte=last_month_start, created_at__lt=month_start
    ).count()

    published_articles = Article.objects.filter(status="published").count()
    total_views = Article.objects.aggregate(total=Sum("views_count"))["total"] or 0
    active_cases = CaseStudy.objects.filter(status="published").count()

    # leads chart — last 30 days
    days_ago_30 = now - timedelta(days=30)
    leads_by_day = (
        ContactLead.objects.filter(created_at__gte=days_ago_30)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    by_day_map = {row["day"].isoformat(): row["count"] for row in leads_by_day}
    chart_labels = []
    chart_data = []
    for i in range(29, -1, -1):
        d = (now - timedelta(days=i)).date()
        chart_labels.append(d.strftime("%d %b"))
        chart_data.append(by_day_map.get(d.isoformat(), 0))

    recent_leads = ContactLead.objects.order_by("-created_at")[:10]

    top_articles = (
        Article.objects.filter(status="published").order_by("-views_count")[:5]
    )

    leads_delta = leads_this_month - leads_last_month
    leads_delta_pct = (
        round((leads_delta / leads_last_month) * 100) if leads_last_month else 0
    )

    return render(request, "dashboard/index.html", {
        "leads_this_month": leads_this_month,
        "leads_last_month": leads_last_month,
        "leads_delta": leads_delta,
        "leads_delta_pct": leads_delta_pct,
        "published_articles": published_articles,
        "total_views": total_views,
        "active_cases": active_cases,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "recent_leads": recent_leads,
        "top_articles": top_articles,
    })
