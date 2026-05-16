from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Contract
from .forms import ContractForm


# === CONTRACTS ===

@staff_member_required
def contract_list(request):
    contracts = Contract.objects.select_related("customer").order_by("end_date")
    return render(request, "legal/contract_list.html", {"contracts": contracts})


@staff_member_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    return render(request, "legal/contract_detail.html", {"contract": contract})


@staff_member_required
def contract_add(request):
    form = ContractForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "เพิ่มสัญญาใหม่แล้ว")
        return redirect("legal:contract_list")
    return render(request, "legal/contract_form.html", {"form": form, "title": "เพิ่มสัญญาใหม่"})


@staff_member_required
def contract_edit(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    form = ContractForm(request.POST or None, request.FILES or None, instance=contract)
    if form.is_valid():
        form.save()
        messages.success(request, "อัพเดตสัญญาแล้ว")
        return redirect("legal:contract_detail", pk=pk)
    return render(request, "legal/contract_form.html", {"form": form, "title": "แก้ไขสัญญา", "contract": contract})
