from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Company
from .forms import CompanyForm
from django.http import JsonResponse


# 🏢 عرض قائمة الشركات الخاصة بالمستخدم الحالي
@login_required
def companies_list(request):
    companies = Company.objects.filter(user=request.user)
    return render(request, 'companies/companies_list.html', {'companies': companies})


# ➕ إنشاء شركة جديدة
@login_required
def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()
            request.session['current_company_id'] = company.id
            request.session['current_company_name'] = company.name
            messages.success(request, _("Company created and activated successfully."))
            return redirect('companies:companies_list')
    else:
        form = CompanyForm()
    return render(request, 'companies/create_company.html', {'form': form})


""" ✏️ تعديل شركة """
@login_required
def edit_company(request, pk):
    company = get_object_or_404(Company, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Company updated successfully."))
            return redirect('companies:companies_list')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'companies/edit_company.html', {'form': form, 'company': company}) 


# ❌ حذف شركة
@login_required
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk, user=request.user)
    if request.method == 'POST':
        company.delete()
        messages.success(request, _("Company deleted successfully."))
        return redirect('companies:companies_list')
    return render(request, 'companies/confirm_delete.html', {'company': company})


@login_required
def activate_company(request, pk):
    # نفعّل الشركة المطلوبة
    company = get_object_or_404(Company, pk=pk, user=request.user)
    
    # أولًا: نوقف أي شركات نشطة أخرى للمستخدم
    Company.objects.filter(user=request.user, is_active=True).exclude(pk=pk).update(is_active=False)

    # ثانيًا: نفعّل الشركة المطلوبة
    company.is_active = True
    company.save()

    # ثالثًا: نخزنها في الـ session
    request.session['active_company_id'] = company.id
    request.session['current_company_name'] = company.name  # ← أضف هذا السطر

    messages.success(request, _("Company activated successfully."))
    return redirect("companies:companies_list")


def close_company(request):
    company_id = request.session.get('active_company_id')

    if company_id:
        try:
            # نحاول نحصل على الشركة من قاعدة البيانات
            company = Company.objects.get(id=company_id, user=request.user)
            company.is_active = False
            company.save()
        except Company.DoesNotExist:
            pass

        # نحذف القيم من الـ session
        request.session.pop('active_company_id', None)
        request.session.pop('current_company_name', None)

        messages.success(request, _("Company closed successfully."))
    else:
        messages.info(request, _("No active company to close."))

    # ✅ نعمل redirect علشان الصفحة تتحدث
    return redirect('companies:companies_list')