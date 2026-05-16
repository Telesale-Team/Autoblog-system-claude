from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Campaign, Keyword
from .forms import CampaignForm, KeywordForm


# === CAMPAIGNS ===

@staff_member_required
def campaign_list(request):
    campaigns = Campaign.objects.order_by("-start_date")
    return render(request, "marketing/campaign_list.html", {"campaigns": campaigns})


@staff_member_required
def campaign_add(request):
    form = CampaignForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "สร้าง Campaign ใหม่แล้ว")
        return redirect("marketing:campaign_list")
    return render(request, "marketing/campaign_form.html", {"form": form, "title": "สร้าง Campaign ใหม่"})


@staff_member_required
def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    form = CampaignForm(request.POST or None, instance=campaign)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดต Campaign แล้ว")
        return redirect("marketing:campaign_list")
    return render(request, "marketing/campaign_form.html", {"form": form, "title": "แก้ไข Campaign", "campaign": campaign})


# === CONTENT CALENDAR ===



# === KEYWORDS ===

@staff_member_required
def keyword_list(request):
    keywords = Keyword.objects.select_related("article").order_by("current_rank")
    return render(request, "marketing/keyword_list.html", {"keywords": keywords})


@staff_member_required
def keyword_add(request):
    form = KeywordForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "เพิ่ม Keyword แล้ว")
        return redirect("marketing:keyword_list")
    return render(request, "marketing/keyword_form.html", {"form": form, "title": "เพิ่ม Keyword ใหม่"})


@staff_member_required
def keyword_edit(request, pk):
    keyword = get_object_or_404(Keyword, pk=pk)
    form = KeywordForm(request.POST or None, instance=keyword)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดต Keyword แล้ว")
        return redirect("marketing:keyword_list")
    return render(request, "marketing/keyword_form.html", {"form": form, "title": "แก้ไข Keyword", "keyword": keyword})
