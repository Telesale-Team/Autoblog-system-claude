from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from .models import Invoice, Expense
from .forms import InvoiceForm, ExpenseForm


# === INVOICES ===

@staff_member_required
def invoice_list(request):
    invoices = Invoice.objects.select_related("customer").order_by("-issue_date")
    return render(request, "finance/invoice_list.html", {"invoices": invoices})


@staff_member_required
def invoice_add(request):
    form = InvoiceForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "สร้างใบแจ้งหนี้แล้ว")
        return redirect("finance:invoice_list")
    return render(request, "finance/invoice_form.html", {"form": form, "title": "สร้างใบแจ้งหนี้ใหม่"})


@staff_member_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, "finance/invoice_detail.html", {"invoice": invoice})


@staff_member_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = InvoiceForm(request.POST or None, instance=invoice)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดตใบแจ้งหนี้แล้ว")
        return redirect("finance:invoice_detail", pk=pk)
    return render(request, "finance/invoice_form.html", {"form": form, "title": "แก้ไขใบแจ้งหนี้", "invoice": invoice})


@staff_member_required
def invoice_mark_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == "POST":
        invoice.status = Invoice.Status.PAID
        invoice.paid_at = timezone.now()
        invoice.save()
        messages.success(request, f"ใบแจ้งหนี้ {invoice.invoice_number} บันทึกว่าชำระแล้ว")
    return redirect("finance:invoice_detail", pk=pk)


# === EXPENSES ===

@staff_member_required
def expense_list(request):
    expenses = Expense.objects.order_by("-date")
    return render(request, "finance/expense_list.html", {"expenses": expenses})


@staff_member_required
def expense_add(request):
    form = ExpenseForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "บันทึกรายจ่ายแล้ว")
        return redirect("finance:expense_list")
    return render(request, "finance/expense_form.html", {"form": form, "title": "บันทึกรายจ่ายใหม่"})


@staff_member_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    form = ExpenseForm(request.POST or None, request.FILES or None, instance=expense)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดตรายจ่ายแล้ว")
        return redirect("finance:expense_list")
    return render(request, "finance/expense_form.html", {"form": form, "title": "แก้ไขรายจ่าย", "expense": expense})
