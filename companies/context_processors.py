from .models import Company

def active_company(request):
    active_company = None
    company_id = request.session.get("active_company_id")
    if company_id:
        active_company = Company.objects.filter(pk=company_id, user=request.user, is_active=True).first()
    return {"active_company": active_company}