from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(_("Company Name"), max_length=150)
    tax_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Tax Number"))
    address = models.CharField(_("Address"), max_length=255, blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=50, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.name


class Branch(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(_("Branch Name"), max_length=100)
    address = models.CharField(_("Address"), max_length=255, blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = _("Branch")
        verbose_name_plural = _("Branches")

    def __str__(self):
        return f"{self.name} ({self.company.name})"
