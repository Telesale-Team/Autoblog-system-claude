from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from blog.models import Article
from .forms import ContactForm


def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_utm(request):
    return {
        "utm_source": request.GET.get("utm_source", ""),
        "utm_medium": request.GET.get("utm_medium", ""),
        "utm_campaign": request.GET.get("utm_campaign", ""),
    }


def home(request):
    featured_articles = Article.objects.filter(
        status="published", is_featured=True
    ).select_related("author", "category")[:3]
    recent_articles = Article.objects.filter(
        status="published"
    ).select_related("author", "category")[:6]
    return render(request, "pages/homepage.html", {
        "featured_articles": featured_articles,
        "recent_articles": recent_articles,
    })


def about(request):
    return render(request, "pages/about.html")


def services(request):
    from .models import Service
    all_services = Service.objects.filter(status="published").order_by("display_order")
    return render(request, "pages/services.html", {"services": all_services})


def service_detail(request, slug):
    from django.shortcuts import get_object_or_404
    from .models import Service
    svc = get_object_or_404(Service, slug=slug, status="published")
    others = Service.objects.filter(status="published").exclude(slug=slug).order_by("display_order")[:4]
    form = ContactForm(initial={"message": f"สนใจบริการ: {svc.name}\n\n"})
    if request.method == "POST":
        data = request.POST.copy()
        if not data.get("email") or data["email"] == "no-email@aibizth.ai":
            data["email"] = f"{data.get('phone','no-phone').replace('-','')}@aibizth.ai"
        form = ContactForm(data)
        if form.is_valid():
            lead = form.save(
                ip_address=get_client_ip(request),
                source="portfolio",
                utm=get_utm(request),
            )
            try:
                send_mail(
                    subject=f"[Lead บริการ] {svc.name} — {lead.name}",
                    message=(
                        f"บริการ: {svc.name}\nชื่อ: {lead.name}\nอีเมล: {lead.email}\n"
                        f"เบอร์: {lead.phone}\nบริษัท: {lead.company}\n\nข้อความ:\n{lead.message}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_NOTIFY_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "ส่งข้อความเรียบร้อย เราจะติดต่อกลับภายใน 24 ชั่วโมงครับ")
            return redirect("pages:service_detail", slug=slug)
    return render(request, "pages/service_detail.html", {
        "svc": svc,
        "others": others,
        "form": form,
    })


def contact(request):
    if request.method == "POST":
        data = request.POST.copy()
        if not data.get("email") or data["email"] == "no-email@aibizth.ai":
            data["email"] = f"{data.get('phone','no-phone').replace('-','')}@aibizth.ai"
        form = ContactForm(data)
        if form.is_valid():
            lead = form.save(
                ip_address=get_client_ip(request),
                source=request.GET.get("source", "landing"),
                utm=get_utm(request),
            )
            try:
                send_mail(
                    subject=f"[Lead ใหม่] {lead.name} — {lead.email}",
                    message=(
                        f"ชื่อ: {lead.name}\nอีเมล: {lead.email}\nเบอร์: {lead.phone}\n"
                        f"บริษัท: {lead.company}\nที่มา: {lead.source}\n\nข้อความ:\n{lead.message}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_NOTIFY_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "ส่งข้อความเรียบร้อย เราจะติดต่อกลับภายใน 24 ชั่วโมงครับ")
            return redirect("pages:contact")
    else:
        form = ContactForm()
    return render(request, "pages/contact.html", {"form": form})
