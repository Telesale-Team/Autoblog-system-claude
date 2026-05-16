from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Customer, Quote, Renewal
from .forms import CustomerForm, QuoteForm, RenewalForm


# === CUSTOMERS ===

@staff_member_required
def customer_list(request):
    from django.utils import timezone
    from django.db.models import Sum
    customers = Customer.objects.filter(is_active=True).order_by("-created_at")
    total_value = customers.aggregate(t=Sum("contract_value"))["t"] or 0
    return render(request, "crm/customer_list.html", {
        "customers": customers,
        "total_value": total_value,
        "today": timezone.now().date(),
    })


@staff_member_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, "crm/customer_detail.html", {"customer": customer})


@staff_member_required
def customer_add(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "เพิ่มลูกค้าใหม่เรียบร้อย")
        return redirect("crm:customer_list")
    return render(request, "crm/customer_form.html", {"form": form, "title": "เพิ่มลูกค้าใหม่"})


@staff_member_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดตข้อมูลลูกค้าแล้ว")
        return redirect("crm:customer_detail", pk=pk)
    return render(request, "crm/customer_form.html", {"form": form, "title": "แก้ไขข้อมูลลูกค้า", "customer": customer})


# === QUOTES ===

@staff_member_required
def quote_list(request):
    quotes = Quote.objects.select_related("lead").order_by("-created_at")
    return render(request, "crm/quote_list.html", {"quotes": quotes})


@staff_member_required
def quote_add(request):
    form = QuoteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "สร้างใบเสนอราคาแล้ว")
        return redirect("crm:quote_list")
    return render(request, "crm/quote_form.html", {"form": form, "title": "สร้างใบเสนอราคาใหม่"})


@staff_member_required
def quote_detail(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    return render(request, "crm/quote_detail.html", {"quote": quote})


@staff_member_required
def quote_edit(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    form = QuoteForm(request.POST or None, instance=quote)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดตใบเสนอราคาแล้ว")
        return redirect("crm:quote_detail", pk=pk)
    return render(request, "crm/quote_form.html", {"form": form, "title": "แก้ไขใบเสนอราคา", "quote": quote})


# === RENEWALS ===

@staff_member_required
def renewal_list(request):
    renewals = Renewal.objects.select_related("customer").order_by("renewal_date")
    return render(request, "crm/renewal_list.html", {"renewals": renewals})


@staff_member_required
def renewal_add(request):
    form = RenewalForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "เพิ่ม Renewal รายการใหม่แล้ว")
        return redirect("crm:renewal_list")
    return render(request, "crm/renewal_form.html", {"form": form, "title": "เพิ่ม Renewal"})


@staff_member_required
def renewal_edit(request, pk):
    renewal = get_object_or_404(Renewal, pk=pk)
    form = RenewalForm(request.POST or None, instance=renewal)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดต Renewal แล้ว")
        return redirect("crm:renewal_list")
    return render(request, "crm/renewal_form.html", {"form": form, "title": "แก้ไข Renewal", "renewal": renewal})
