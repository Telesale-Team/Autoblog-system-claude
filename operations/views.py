from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import AIProject, PromptLibrary, QALog
from .forms import AIProjectForm, PromptLibraryForm, QALogForm


# === AI PROJECTS ===

@staff_member_required
def project_list(request):
    projects = AIProject.objects.select_related("customer").filter(is_active=True).order_by("-created_at")
    return render(request, "operations/project_list.html", {
        "projects": projects,
        "status_choices": AIProject.Status.choices,
    })


@staff_member_required
def project_detail(request, pk):
    project = get_object_or_404(AIProject, pk=pk)
    return render(request, "operations/project_detail.html", {"project": project})


@staff_member_required
def project_add(request):
    form = AIProjectForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "สร้าง AI Project ใหม่แล้ว")
        return redirect("operations:project_list")
    return render(request, "operations/project_form.html", {"form": form, "title": "สร้าง AI Project ใหม่"})


@staff_member_required
def project_edit(request, pk):
    project = get_object_or_404(AIProject, pk=pk)
    form = AIProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดต AI Project แล้ว")
        return redirect("operations:project_detail", pk=pk)
    return render(request, "operations/project_form.html", {"form": form, "title": "แก้ไข AI Project", "project": project})


# === PROMPT LIBRARY ===

@staff_member_required
def prompt_list(request):
    prompts = PromptLibrary.objects.order_by("agent", "use_case")
    return render(request, "operations/prompt_list.html", {"prompts": prompts})


@staff_member_required
def prompt_add(request):
    form = PromptLibraryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "เพิ่ม Prompt ใหม่แล้ว")
        return redirect("operations:prompt_list")
    return render(request, "operations/prompt_form.html", {"form": form, "title": "เพิ่ม Prompt ใหม่"})


@staff_member_required
def prompt_edit(request, pk):
    prompt = get_object_or_404(PromptLibrary, pk=pk)
    form = PromptLibraryForm(request.POST or None, instance=prompt)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดต Prompt แล้ว")
        return redirect("operations:prompt_list")
    return render(request, "operations/prompt_form.html", {"form": form, "title": "แก้ไข Prompt", "prompt": prompt})


# === QA LOG ===

@staff_member_required
def qa_list(request):
    logs = QALog.objects.order_by("-reviewed_at")
    return render(request, "operations/qa_list.html", {"logs": logs})


@staff_member_required
def qa_add(request):
    form = QALogForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "บันทึก QA Log แล้ว")
        return redirect("operations:qa_list")
    return render(request, "operations/qa_form.html", {"form": form, "title": "บันทึก QA ใหม่"})


@staff_member_required
def qa_edit(request, pk):
    log = get_object_or_404(QALog, pk=pk)
    form = QALogForm(request.POST or None, instance=log)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดต QA Log แล้ว")
        return redirect("operations:qa_list")
    return render(request, "operations/qa_form.html", {"form": form, "title": "แก้ไข QA Log", "log": log})


# === PROJECT MONITOR ===

@staff_member_required
def monitor(request):
    """หน้ารวมสถานะระบบที่เรา deploy ให้ลูกค้า — /owner/projects/

    จัดกลุ่ม 2 ชั้น:
      ชั้น 1  ผลิตภัณฑ์ (deploy ซ้ำได้) / งานรับทำ / ระบบภายในเรา
      ชั้น 2  ซ้อนตามบริการที่ขายบนเว็บ (pages.Service)
    """
    from pages.models import Service
    from .models import Deployment

    deployments = (Deployment.objects
                   .select_related("project", "project__service", "project__customer")
                   .prefetch_related("checks"))

    # ── แยกระบบภายในออกก่อน — ไม่ผูกกับบริการที่ขาย ──
    internal = [d for d in deployments if d.is_internal]
    external = [d for d in deployments if not d.is_internal]

    # ── จัดกลุ่มตามบริการ ──
    by_service = {}
    unassigned = []
    for d in external:
        svc = d.project.service if d.project else None
        if svc is None:
            unassigned.append(d)
        else:
            by_service.setdefault(svc.id, []).append(d)

    def build_tier(delivery_type):
        rows = []
        for svc in Service.objects.filter(delivery_type=delivery_type).order_by("display_order"):
            rows.append({
                "service": svc,
                "deployments": by_service.get(svc.id, []),
                "up":   sum(1 for d in by_service.get(svc.id, []) if d.state == "up"),
                "down": sum(1 for d in by_service.get(svc.id, []) if d.state == "down"),
            })
        return rows

    product_rows = build_tier("product")
    custom_rows  = build_tier("custom")

    all_ext = external
    summary = {
        "services":    Service.objects.count(),
        "deployments": len(all_ext),
        "up":          sum(1 for d in all_ext if d.state == "up"),
        "down":        sum(1 for d in all_ext if d.state == "down"),
        "mrr":         sum(d.monthly_fee for d in all_ext),
    }
    uptimes = [d.uptime_pct() for d in all_ext if d.uptime_pct() is not None]
    summary["uptime"] = round(sum(uptimes) / len(uptimes), 1) if uptimes else None

    return render(request, "operations/monitor.html", {
        "product_rows": product_rows,
        "custom_rows":  custom_rows,
        "internal":     internal,
        "unassigned":   unassigned,
        "summary":      summary,
    })


@staff_member_required
def monitor_detail(request, pk):
    """รายละเอียด deployment เดียว — ทะเบียน + ประวัติสถานะ"""
    from .models import Deployment

    dep = get_object_or_404(
        Deployment.objects.select_related("project", "project__service", "project__customer"),
        pk=pk,
    )
    checks = dep.checks.order_by("-checked_at")[:120]
    return render(request, "operations/monitor_detail.html", {
        "dep":     dep,
        "checks":  checks,
        "latest":  dep.latest_check,
        "uptime":  dep.uptime_pct(),
    })
