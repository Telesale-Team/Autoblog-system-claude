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
