"""
Historical Property Cash Flow Model

What: Model for tracking annual actual operating performance
Why: Essential for valuation, underwriting, and performance analysis
Where: projectalphav1/core/models/propertycfs.py
How: Many-to-One with AssetIdHub; includes income, expense, and calculated metrics
"""
from django.db import models
from decimal import Decimal


class HistoricalPropertyCashFlow(models.Model):
    """
    Historical property-level cash flows (income and expenses) by year.
    
    What: Tracks annual actual operating performance for your owned/managed assets.
    Why: Essential for valuation, underwriting, and performance analysis (historical NOI, operating expense ratios).
    Where: Many-to-One with AssetIdHub (multiple years per asset).
    How: Create one record per asset per year; use helpers to calculate NOI, EGI, etc.
    """
    # Many-to-One link to asset
    asset_hub = models.ForeignKey(
        'AssetIdHub',
        on_delete=models.CASCADE,
        related_name='historical_cashflows',
        help_text='Asset this historical cash flow data belongs to.'
    )
    
    # Year for this data
    year = models.PositiveIntegerField(
        help_text='Calendar year for this cash flow data (e.g., 2024).'
    )

    # ----- Income -----
    gross_potential_rent_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Gross potential rent (GPR) - fully occupied rent for the year.'
    )
    cam_income = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='CAM income for the year.'
    )
    other_income = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Other income (parking, laundry, pet fees, etc.).'
    )
    vacancy_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Vacancy percentage for the year (as decimal, e.g., 5.00 for 5%).'
    )

    # ----- Operating Expenses -----
    admin = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Administrative expenses.'
    )
    insurance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Property insurance costs.'
    )
    utilities_water = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Water utility expenses.'
    )
    utilities_sewer = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Sewer utility expenses.'
    )
    utilities_electric = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Electric utility expenses.'
    )
    utilities_gas = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Gas utility expenses.'
    )
    trash = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Trash removal expenses.'
    )
    utilities_other = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Other utility expenses.'
    )
    property_management = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Property management fees.'
    )
    repairs_maintenance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Repairs and maintenance costs.'
    )
    marketing = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Marketing and leasing costs.'
    )
    property_taxes = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Property taxes.'
    )
    hoa_fees = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='HOA fees (if applicable).'
    )
    security_property_preservation = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Security expenses.'
    )
    landscaping = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Landscaping and grounds maintenance.'
    )
    pool_maintenance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Pool maintenance costs.'
    )
   
    other_expense = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Other miscellaneous operating expenses.'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes about this year\'s performance.'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_historical_property_cashflow'
        verbose_name = 'Historical Property Cash Flow'
        verbose_name_plural = 'Historical Property Cash Flows'
        ordering = ['asset_hub', '-year']
        constraints = [
            models.UniqueConstraint(fields=['asset_hub', 'year'], name='uq_asset_hub_year')
        ]
        indexes = [
            models.Index(fields=['asset_hub', 'year']),
        ]
    
    def __str__(self):
        """String representation showing asset and year."""
        return f"{self.asset_hub} - {self.year}"
    
    # ----- Calculated helpers -----
    def vacancy_loss(self) -> Decimal:
        """
        Calculate Vacancy Loss based on vacancy percentage.
        
        What: Gross Potential Rent * (Vacancy % / 100)
        Why: Calculates dollar amount of lost revenue due to vacancy
        How: vacancy_pct is stored as percentage (e.g., 5.00 for 5%)
        
        Returns:
            Decimal: Vacancy loss amount rounded to 2 decimals.
        """
        gpr = self.gross_potential_rent_revenue or Decimal('0.00')
        vacancy_pct = self.vacancy_pct or Decimal('0.00')
        
        gpr = gpr if isinstance(gpr, Decimal) else Decimal(str(gpr))
        vacancy_pct = vacancy_pct if isinstance(vacancy_pct, Decimal) else Decimal(str(vacancy_pct))
        
        # vacancy_pct is stored as percentage (e.g., 5.00 for 5%), so divide by 100
        vacancy_loss_amt = gpr * (vacancy_pct / Decimal('100'))
        
        return vacancy_loss_amt.quantize(Decimal('0.01'))
    
    def effective_gross_rent_revenue(self) -> Decimal:
        """
        Calculate Effective Gross Rent Revenue.
        
        What: Gross Potential Rent - Vacancy Loss
        Why: Shows actual rent revenue after accounting for vacancy
        How: Uses calculated vacancy_loss() method
        
        Returns:
            Decimal: Effective gross rent revenue rounded to 2 decimals.
        """
        gpr = self.gross_potential_rent_revenue or Decimal('0.00')
        gpr = gpr if isinstance(gpr, Decimal) else Decimal(str(gpr))
        
        vacancy = self.vacancy_loss()
        
        return (gpr - vacancy).quantize(Decimal('0.01'))
    
    def effective_gross_income(self) -> Decimal:
        """
        Calculate Effective Gross Income (EGI).
        
        What: Effective Gross Rent Revenue + Other Income
        Why: Shows total actual income after vacancy (rent + other sources)
        How: Uses effective_gross_rent_revenue() + other_income + cam_income
        
        Returns:
            Decimal: EGI rounded to 2 decimals.
        """
        effective_rent = self.effective_gross_rent_revenue()
        other = self.other_income or Decimal('0.00')
        cam = self.cam_income or Decimal('0.00')
        
        other = other if isinstance(other, Decimal) else Decimal(str(other))
        cam = cam if isinstance(cam, Decimal) else Decimal(str(cam))
        
        return (effective_rent + other + cam).quantize(Decimal('0.01'))
    
    def total_operating_expenses(self) -> Decimal:
        """
        Calculate total operating expenses (sum of all expense fields).
        
        Returns:
            Decimal: Total opex rounded to 2 decimals.
        """
        expense_fields = [
            self.admin, self.insurance, self.utilities_water, self.utilities_sewer,
            self.utilities_electric, self.utilities_gas, self.trash, self.utilities_other,
            self.property_management, self.repairs_maintenance, self.marketing,
            self.property_taxes, self.hoa_fees, self.security_property_preservation, self.landscaping,
            self.pool_maintenance, self.other_expense
        ]
        
        total = Decimal('0.00')
        for expense in expense_fields:
            if expense:
                exp = expense if isinstance(expense, Decimal) else Decimal(str(expense))
                total += exp
        
        return total.quantize(Decimal('0.01'))
    
    def total_utilities(self) -> Decimal:
        """
        Calculate total utilities expenses.
        
        What: Sum of water, sewer, electric, gas, trash, and other utilities
        Why: Provide grouped utilities total for UI and analysis
        Returns:
            Decimal: Total utilities rounded to 2 decimals.
        """
        util_fields = [
            self.utilities_water,
            self.utilities_sewer,
            self.utilities_electric,
            self.utilities_gas,
            self.trash,
            self.utilities_other,
        ]

        total = Decimal('0.00')
        for v in util_fields:
            if v:
                total += v if isinstance(v, Decimal) else Decimal(str(v))

        return total.quantize(Decimal('0.01'))

    def net_operating_income(self) -> Decimal:
        """
        Calculate Net Operating Income (NOI).
        
        What: EGI - Total Operating Expenses
        Why: Key valuation metric (NOI / Cap Rate = Value).
        
        Returns:
            Decimal: NOI rounded to 2 decimals.
        """
        egi = self.effective_gross_income()
        opex = self.total_operating_expenses()
        
        return (egi - opex).quantize(Decimal('0.01'))
    
    def operating_expense_ratio(self) -> Decimal:
        """
        Calculate Operating Expense Ratio (OER).
        
        What: Total Opex / EGI
        Why: Measures operating efficiency (lower is better).
        
        Returns:
            Decimal: OER as percentage (e.g., 45.50 for 45.5%), or 0.00 if EGI is zero.
        """
        egi = self.effective_gross_income()
        if egi <= 0:
            return Decimal('0.00')
        
        opex = self.total_operating_expenses()
        ratio = (opex / egi) * Decimal('100')
        
        return ratio.quantize(Decimal('0.01'))
    
    def cap_rate(self) -> Decimal:
        """
        Calculate Cap Rate using latest valuation.
        
        What: (NOI / Market Value) * 100
        Why: Standard unlevered return metric
        How: Uses latest `Valuation` record for this `asset_hub` (by `value_date` desc or created order)
        Returns:
            Decimal: Cap rate percent (e.g., 6.25 for 6.25%). 0.00 if value unavailable/non-positive.
        """
        try:
            from .valuations import Valuation  # local import to avoid circulars
        except Exception:
            return Decimal('0.00')

        noi = self.net_operating_income()
        # Get most recent valuation by value_date desc, fallback to latest created
        valuation = (
            Valuation.objects
            .filter(asset_hub=self.asset_hub)
            .order_by('-value_date', '-id')
            .first()
        )
        if not valuation or not valuation.asis_value:
            return Decimal('0.00')

        value = valuation.asis_value if isinstance(valuation.asis_value, Decimal) else Decimal(str(valuation.asis_value))
        if value <= 0:
            return Decimal('0.00')

        cap = (noi / value) * Decimal('100')
        return cap.quantize(Decimal('0.01'))