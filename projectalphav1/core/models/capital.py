"""
core.models.capital
- Shared capital-structure models used across apps (AM, ACQ, Treasury, Reporting).
- Mirrors DebtFacility while we transition from am_module.

Docs reviewed:
- Django model options (managed, db_table): https://docs.djangoproject.com/en/stable/ref/models/options/
- Django models: https://docs.djangoproject.com/en/stable/topics/db/models/
"""

from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models


class DebtFacility(models.Model):
    """Shared Debt Facility model (currently managed=True, as core now owns and manages the debt_facility table).
    This mirrors am_module.models.capital.DebtFacility fields so other apps can
    begin importing from core without changing the physical table yet.
    """

    facility_name = models.CharField(max_length=255)
    firm_name = models.CharField(max_length=255)
    firm_email = models.EmailField(null=True)
    firm_phone = models.CharField(max_length=255, null=True)

    commitment_size = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
    )

    # Fixed to SOFR for now
    rate_index = models.CharField(max_length=16, default="SOFR", null=True)
    sofr_rate = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )

    spread_bps = models.PositiveIntegerField(null=True)

    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True  # core now owns and manages the debt_facility table
        db_table = "debt_facility"
        ordering = ["-created_at"]
        verbose_name = "Debt Facility"
        verbose_name_plural = "Debt Facilities"

class JVEquityPartner(models.Model):
    """Shared Equity Partner model (currently managed=True, as core now owns and manages the equity_partner table).
    This mirrors am_module.models.capital.EquityPartner fields so other apps can
    begin importing from core without changing the physical table yet.

    """

    jv_name = models.CharField(max_length=255)
    partner_firm_name = models.CharField(max_length=255)
    partner_firm_email = models.EmailField(null=True)
    partner_firm_phone = models.CharField(max_length=255, null=True)

    commitment_size = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
    )
        
    lp_percentage = models.PositiveIntegerField(null=True)
    gp_percentage = models.PositiveIntegerField(null=True)

    lp_promote = models.PositiveIntegerField(null=True)
    gp_promote = models.PositiveIntegerField(null=True)
    
    lp_contribution_paydown = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
    )
    
    gp_contribution_paydown = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
    )
    lp_pref = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
    )
    
    am_fees = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
    )
    
    acq_fees = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        null=True,
    )
    
    fund_start_date = models.DateField(null=True)
    fund_maturity_date = models.DateField(null=True)
    
    class Meta:
        managed = True  # core now owns and manages the equity_partner table
        db_table = "equity_partner"
        verbose_name = "Equity Partner"
        verbose_name_plural = "Equity Partners"


    

    