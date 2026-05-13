from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from blog.models import Article
from portfolio.models import CaseStudy
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
    featured_articles = Article.objects.filter(status="published", is_featured=True)[:3]
    featured_cases = CaseStudy.objects.filter(status="published", is_featured=True)[:3]

    return render(request, "pages/home.html", {
        "featured_articles": featured_articles,
        "featured_cases": featured_cases,
    })


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
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
