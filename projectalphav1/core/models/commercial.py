"""
core.models.commercial

What: Commercial real estate models for multi-unit properties.
Why: Track unit mix, rent rolls, and commercial property metrics.
Where: projectalphav1/core/models/commercial.py
How: Django models with calculated fields and business logic.
"""

from django.db import models
from django.db.models import F, Sum, DecimalField, ExpressionWrapper
from django.core.validators import MinValueValidator
from decimal import Decimal

class UnitMix(models.Model):
    """
    Tracks unit mix data for commercial/multi-family properties.
    
    What: Stores unit type, count, square footage, and rent data.
    Why: Essential for commercial property valuation and analysis.
    Where: Used in commercial property analysis and rent roll calculations.
    How: Create one record per unit type per property.
    """
    asset_hub_id = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        related_name='unit_mixes',
        help_text="Asset this unit mix belongs to"
    )

    # Unit characteristics
    unit_type = models.CharField(
        max_length=50,
        help_text="Type of unit (e.g., '1BR', '2BR', 'Studio', 'Retail', 'Office')"
    )
    unit_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of units of this type"
    )
    unit_avg_sqft = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Average square footage per unit of this type"
    )
    unit_avg_rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Average monthly rent per unit of this type"
    )
    
    # Calculated field: price per square foot
    price_sqft = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        help_text="Calculated: unit_avg_rent / unit_avg_sqft (rent per sqft)"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or comments about this unit type"
    )
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Unit Mix"
        verbose_name_plural = "Unit Mix Records"
        ordering = ['unit_type']
    
    def __str__(self):
        """String representation showing unit type and count."""
        return f"{self.unit_type} ({self.unit_count} units)"
    
    def save(self, *args, **kwargs):
        """
        Override save to calculate price_sqft before saving.
        
        What: Automatically calculates rent per square foot.
        Why: Ensures price_sqft is always in sync with rent and sqft.
        How: Divides unit_avg_rent by unit_avg_sqft, handles division by zero.
        """
        # Calculate price per square foot (rent per sqft)
        if self.unit_avg_sqft and self.unit_avg_sqft > 0:
            # Convert to Decimal for precision
            rent = self.unit_avg_rent if isinstance(self.unit_avg_rent, Decimal) else Decimal(str(self.unit_avg_rent))
            sqft = Decimal(str(self.unit_avg_sqft))
            
            # Calculate and round to 2 decimal places
            self.price_sqft = (rent / sqft).quantize(Decimal('0.01'))
        else:
            # If sqft is 0 or None, set price_sqft to None
            self.price_sqft = None
        
        # Call parent save method
        super().save(*args, **kwargs)
    
    def get_total_sqft(self) -> int:
        """
        Calculate total square footage for all units of this type.
        
        Returns:
            int: unit_count * unit_avg_sqft
        """
        return self.unit_count * self.unit_avg_sqft
    
    def get_total_monthly_rent(self) -> Decimal:
        """
        Calculate total monthly rent for all units of this type.
        
        Returns:
            Decimal: unit_count * unit_avg_rent
        """
        rent = self.unit_avg_rent if isinstance(self.unit_avg_rent, Decimal) else Decimal(str(self.unit_avg_rent))
        return Decimal(str(self.unit_count)) * rent

    def get_total_annual_rent(self) -> Decimal:
        """
        Calculate total ANNUAL rent for all units of this type.

        What: Multiplies the monthly total by 12.
        Why: Common KPI used in underwriting and valuation (annualized rent roll).
        How: Reuses `get_total_monthly_rent()` and multiplies by Decimal('12').

        Returns:
            Decimal: (unit_count * unit_avg_rent) * 12, rounded to 2 decimals
        """
        monthly_total: Decimal = self.get_total_monthly_rent()
        return (monthly_total * Decimal('12')).quantize(Decimal('0.01'))

    @classmethod
    def total_monthly_rent_all(cls) -> Decimal:
        """
        Compute the total monthly rent across ALL `UnitMix` rows in the table.

        What: Database-level aggregation of `unit_count * unit_avg_rent` summed across rows.
        Why: Uses the database for performance on larger datasets; avoids Python-side loops.
        How: Uses `ExpressionWrapper` with `F` expressions and `Sum` aggregate.

        Returns:
            Decimal: Sum of monthly rent for all unit types across all properties (Decimal('0.00') if none).
        """
        expr = ExpressionWrapper(
            F('unit_count') * F('unit_avg_rent'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
        agg = cls.objects.aggregate(total=Sum(expr))
        return agg['total'] if agg['total'] is not None else Decimal('0.00')

    @staticmethod
    def total_monthly_rent_for(qs: models.QuerySet) -> Decimal:
        """
        Compute the total monthly rent for a provided queryset of `UnitMix` rows.

        What: Same aggregation as `total_monthly_rent_all`, but restricted to `qs`.
        Why: Lets callers scope by property, asset hub, or any filter.
        How: Call with `UnitMix.objects.filter(...)`.

        Args:
            qs (QuerySet): A queryset of `UnitMix` rows to aggregate.

        Returns:
            Decimal: Sum of monthly rent for all unit types in the queryset (Decimal('0.00') if none).
        """
        expr = ExpressionWrapper(
            F('unit_count') * F('unit_avg_rent'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
        agg = qs.aggregate(total=Sum(expr))
        return agg['total'] if agg['total'] is not None else Decimal('0.00')


class RentRoll(models.Model):
    """
    Tracks rent roll data for commercial/multi-family properties.
    
    What: Stores rent roll data for a specific property.
    Why: Essential for commercial property analysis and rent roll calculations.
    Where: Used in commercial property analysis and rent roll calculations.
    How: Create one record per property.
    """
    asset_hub_id = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        related_name='rent_rolls',
        help_text="Asset this rent roll belongs to"
    )
    
    tenant_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name of the tenant"
    )
    
    unit_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name of the unit"
    )
    sq_feet = models.IntegerField(
        null=True,
        blank=True,
        help_text="Square footage of the unit"
    )
    rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monthly rent amount"
    )
    # Optional monthly CAM (Common Area Maintenance) amount
    cam_month = models.IntegerField(
        null=True,
        blank=True,
        help_text="CAM month"
    )

    # Optional explicit lease term in months. If not provided, we compute it
    # from lease_start_date and lease_end_date in save().
    lease_term_months = models.IntegerField(
        null=True,
        blank=True,
        help_text="Lease term in months. If blank, will be auto-calculated from start/end dates."
    )

    lease_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Lease start date"
    )
    lease_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Lease end date"
    )

    lease_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Type of lease"
    )
    rent_increase_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Rent increase percentage"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or comments about this unit type"
    )

    # ----- Calculated helpers (not stored) -----
    def get_price_per_sqft(self) -> Decimal:
        """
        Calculate monthly rent price per square foot for this unit.

        Returns:
            Decimal: rent / sq_feet (0.00 if sq_feet is missing or zero)
        """
        if not self.sq_feet or self.sq_feet <= 0 or not self.rent:
            return Decimal('0.00')
        monthly_rent: Decimal = self.rent if isinstance(self.rent, Decimal) else Decimal(str(self.rent))
        sqft: Decimal = Decimal(str(self.sq_feet))
        return (monthly_rent / sqft).quantize(Decimal('0.01'))

    def get_annual_rent(self) -> Decimal:
        """
        Calculate annual rent for this unit (monthly rent * 12).

        Returns:
            Decimal: rent * 12, rounded to 2 decimals
        """
        if not self.rent:
            return Decimal('0.00')
        monthly_rent: Decimal = self.rent if isinstance(self.rent, Decimal) else Decimal(str(self.rent))
        return (monthly_rent * Decimal('12')).quantize(Decimal('0.01'))

    def get_cam_per_sqft(self) -> Decimal:
        """
        Calculate monthly CAM per square foot for this unit.

        Returns:
            Decimal: cam_month / sq_feet (0.00 if sq_feet is missing or zero)
        """
        if not self.sq_feet or self.sq_feet <= 0 or not self.cam_month:
            return Decimal('0.00')
        cam_month_amt: Decimal = Decimal(str(self.cam_month))
        sqft: Decimal = Decimal(str(self.sq_feet))
        return (cam_month_amt / sqft).quantize(Decimal('0.01'))

    def get_annual_cam(self) -> Decimal:
        """
        Calculate annual CAM for this unit (monthly CAM * 12).

        Returns:
            Decimal: cam_month * 12, rounded to 2 decimals
        """
        if not self.cam_month:
            return Decimal('0.00')
        cam_month_amt: Decimal = Decimal(str(self.cam_month))
        return (cam_month_amt * Decimal('12')).quantize(Decimal('0.01'))

    # ----- Persistence helper to auto-calc lease_term_months -----
    def save(self, *args, **kwargs):
        """
        Override save to auto-calculate lease_term_months when not provided.

        What:
            - If `lease_term_months` is None/blank and both start/end dates exist,
              compute the month span between them.
        Why:
            - Keeps a stored value for reporting/filtering without manual entry.
        How:
            - Month diff: (years*12 + months) plus 1 month when end day >= start day
              to approximate inclusive months; never negative.
        """
        if (self.lease_term_months is None) and self.lease_start_date and self.lease_end_date:
            years_delta = self.lease_end_date.year - self.lease_start_date.year  # type: ignore[union-attr]
            months_delta = self.lease_end_date.month - self.lease_start_date.month  # type: ignore[union-attr]
            total_months = years_delta * 12 + months_delta
            try:
                end_day = self.lease_end_date.day  # type: ignore[union-attr]
                start_day = self.lease_start_date.day  # type: ignore[union-attr]
                if end_day >= start_day:
                    total_months += 1
            except Exception:
                pass
            if total_months < 0:
                total_months = 0
            self.lease_term_months = total_months

        return super().save(*args, **kwargs)