from __future__ import annotations

from django.db import models
from django.conf import settings
from decimal import Decimal
from datetime import date
from core.models.model_co_lookupTables import Grade

class ValuationGradeReference(models.Model):
    """
    Reference table containing allowable valuation grades.
    
    What this does:
    - Stores grade definitions with labels, descriptions, and sort order
    - Uses centralized Grade enum from model_co_lookupTables for consistency
    
    Why this exists:
    - Allows extended metadata (description, sort_order) beyond simple enum
    - Provides audit trail with created/updated timestamps
    - Can be managed via Django admin
    
    How to use:
    - Grade choices come from Grade enum (A+, A, B, C, D, F)
    - Add descriptions and sort order for UI presentation
    """

    code = models.CharField(
        max_length=2,
        unique=True,
        choices=Grade.choices,
        help_text='Canonical grade code selected from the fixed set (A+, A, B, C, D, F). Uses centralized Grade enum from model_co_lookupTables.'
    )
    label = models.CharField(
        max_length=50,
        help_text='Plain-language grade label for UI display.'  # WHAT: Human readable version of the grade for front-end rendering.
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Extended guidance on when to use this grade.'  # WHY: Provides business context for grade selection.
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text='Controls ordering of grades in dropdowns.'  # HOW: Used to present grades in a fixed order regardless of code.
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when this grade was created.'  # WHERE: Allows audit of grade reference lifecycle.
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when this grade was last updated.'  # WHERE: Tracks latest maintenance on grade definitions.
    )

    class Meta:
        db_table = 'core_valuation_grade_reference'
        verbose_name = 'Valuation Grade Reference'
        verbose_name_plural = 'Valuation Grade References'
        ordering = ['sort_order', 'code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['sort_order']),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.label}" if self.label else self.code


class Valuation(models.Model):
    """
    This model stores all property valuations with a source tag to differentiate
    between internal, broker, third-party, and other valuation sources.
    """
    # Core relationship
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='valuations',
        help_text='Link to hub; multiple valuations per asset are supported.',
    )
    # WHAT: Optional link to Master CRM contact/broker for sourcing attribution.
    # WHY: Lets us tie valuations back to the specific broker/contact who supplied them.
    # WHERE: Stored directly on the unified Valuation model to cover broker and other CRM-sourced valuations.
    # HOW: Nullable ForeignKey with SET_NULL so historical valuations persist if the CRM entry is deleted.
    broker_contact = models.ForeignKey(
        'core.MasterCRM',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='valuations',
        help_text='CRM contact (usually broker) associated with this valuation.'
    )
    grade = models.ForeignKey(
        'core.ValuationGradeReference',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_valuations',
        help_text='Reference grade applied to this valuation.'  # WHAT: Links valuation to a grade reference entry.
    )

    # Source tracking
    class Source(models.TextChoices):
        """Canonical source codes for valuation records."""

        INTERNAL_INITIAL_UW = ("internalInitialUW", "Internal Initial UW Valuation")  # WHAT: Initial underwriting valuation.
        INTERNAL = ("internal", "Internal Valuation")  # WHAT: Ongoing internal valuation.
        BROKER = ("broker", "Broker Valuation")  # WHAT: Broker provided valuation.
        DESKTOP = ("desktop", "Desktop Valuation")  # WHAT: Desktop valuation record.
        BPO_INTERIOR = ("BPOI", "BPOI")  # WHAT: Broker price opinion interior.
        BPO_EXTERIOR = ("BPOE", "BPOE")  # WHAT: Broker price opinion exterior.
        SELLER = ("seller", "Seller Provided")  # WHAT: Seller submitted valuation.
        APPRAISAL = ("appraisal", "Professional Appraisal")  # WHAT: Third-party professional appraisal.

    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        help_text='Source of this valuation.'
    )
    
    # Common valuation fields (renamed to be source-neutral)
    asis_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='As-is value of the property.'
    )
    arv_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='After-repair value of the property.'
    )
    value_date = models.DateField(
        null=True, 
        blank=True,
        help_text='Date of the valuation.'
    )
    rehab_est_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Total estimated rehabilitation costs.'
    )
    recommend_rehab = models.BooleanField(
        default=False,
        help_text='Whether to recommend rehabilitation.'
    )
    recommend_rehab_reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for recommending rehabilitation.'
    )
    # Detailed rehab estimates (from InternalValuation)
    # WHAT: Cost estimates and condition grades for each major rehab category
    # WHY: Allows granular tracking of rehab needs and quality assessment
    # HOW: Each category has a cost estimate (DecimalField) and condition grade (Grade enum)
    
    # Roof
    roof_est = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Estimated cost for roof repairs/replacement.'
    )
    roof_grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text='Condition grade for roof (A+ to F).'
    )
    
    # Kitchen
    kitchen_est = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Estimated cost for kitchen repairs/upgrades.'
    )
    kitchen_grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text='Condition grade for kitchen (A+ to F).'
    )
    
    # Bathrooms
    bath_est = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Estimated cost for bathroom repairs/upgrades.'
    )
    bath_grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text='Condition grade for bathrooms (A+ to F).'
    )
    
    # Flooring
    flooring_est = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Estimated cost for flooring repairs/replacement.'
    )
    flooring_grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text='Condition grade for flooring (A+ to F).'
    )
    
    # Windows
    windows_est = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Estimated cost for window repairs/replacement.'
    )
    windows_grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text='Condition grade for windows (A+ to F).'
    )
    
    # Appliances
    appliances_est = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Estimated cost for appliance repairs/replacement.'
    )
    appliances_grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text='Condition grade for appliances (A+ to F).'
    )
    
    # Plumbing
    plumbing_est = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Estimated cost for plumbing repairs.'
    )
    plumbing_grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text='Condition grade for plumbing (A+ to F).'
    )
    
    # Electrical
    electrical_est = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Estimated cost for electrical repairs/upgrades.'
    )
    electrical_grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text='Condition grade for electrical (A+ to F).'
    )
    
    # Landscaping
    landscaping_est = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Estimated cost for landscaping improvements.'
    )
    landscaping_grade = models.CharField(
        max_length=5,
        choices=Grade.choices,
        null=True,
        blank=True,
        help_text='Condition grade for landscaping (A+ to F).'
    )
    
    # Additional fields (from BrokerValues)
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text='Notes about the valuation.'
    )
    links = models.URLField(
        blank=True, 
        null=True,
        help_text='Links to supporting documentation or external resources.'
    )
    
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_valuations',
        help_text='User who created this valuation record.'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_valuations',
        help_text='User who last updated this valuation record.'
    )
    
    class Meta:
        db_table = 'acq_valuations'
        verbose_name = 'Valuation'
        verbose_name_plural = 'Valuations'
        ordering = ['-value_date', '-created_at']
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['source']),
            models.Index(fields=['value_date']),
            models.Index(fields=['broker_contact']),
            models.Index(fields=['grade']),
        ]
        # Allow multiple valuations per asset, but only one per source per date
        constraints = [
            models.UniqueConstraint(
                fields=['asset_hub', 'source', 'value_date'],
                name='unique_valuation_per_source_date'
            )
        ]
    
    def __str__(self):
        hub_id = self.asset_hub.id if self.asset_hub else 'No Hub'
        return f"{self.get_source_display()} for Hub #{hub_id} as of {self.value_date or 'N/A'}"


class ComparableProperty(models.Model):
    """
    Parent model for comparable properties (sales and lease).
    
    What: Stores shared property characteristics for all comparables.
    Why: Normalizes common fields to avoid duplication between sales and lease comps.
    Where: Extended by SalesComparable and LeaseComparable via OneToOne relationships.
    How: Create once per property, then attach sales OR lease data (or both if needed).
    """
    # Link to subject property
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.CASCADE,
        related_name='comparable_properties',
        help_text='Link to hub; multiple comparables per asset are supported.'
    )
    as_of_date = models.DateField(help_text='Date the comparable was ascertained.')
    property_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Name of the comparable property (e.g., apartment complex name).'
    )
    # Address fields
    street_address = models.CharField(max_length=255, help_text='Street address of the comparable property.')
    city = models.CharField(max_length=100, help_text='City of the comparable property.')
    state = models.CharField(max_length=2, help_text='State of the comparable property.')
    zip_code = models.CharField(max_length=10, help_text='Zip code of the comparable property.')
    
    # Property characteristics
    distance_from_subject = models.IntegerField(
        null=True,
        blank=True,
        help_text='Distance from the subject property in feet.'
    )
    property_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Type of the comparable property (e.g., SFR, Multi-Family, Retail).'
    )
    property_style = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Style of the comparable property (e.g., Colonial, Ranch).'
    )
    
    # Unit details
    beds = models.IntegerField(null=True, blank=True, help_text='Number of bedrooms.')
    baths = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='Number of bathrooms (e.g., 2.5).'
    )
    units = models.IntegerField(null=True, blank=True, help_text='Number of units in the property.')
    
    # Size metrics
    gross_square_ft_building = models.IntegerField(
        null=True,
        blank=True,
        help_text='For commercial...this is total sq feet including common areas. Gross square footage of the building.'
    )
    livable_square_ft_building = models.IntegerField(
        null=True,
        blank=True,
        help_text='Livable square footage of the building/ if SFR or non commercial this is just the basic total sq feet.'
    )
    year_built = models.IntegerField(null=True, blank=True, help_text='Year the property was built.')
    total_lot_size = models.IntegerField(
        null=True,
        blank=True,
        help_text='Total lot size in square feet.'
    )
    market_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Type of the market (e.g., SFR, Multi-Family, Retail).'
    )
    submarket = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Submarket of the comparable property.'
    )
    building_class = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Building class of the comparable property.'
    )   





    # Notes
    notes = models.TextField(blank=True, null=True, help_text='Additional notes about this comparable.')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_comparable_property'
        verbose_name = 'Comparable Property'
        verbose_name_plural = 'Comparable Properties'
        ordering = ['-as_of_date', 'street_address']
        indexes = [
            models.Index(fields=['asset_hub', 'as_of_date']),
            models.Index(fields=['property_type']),
        ]
    
    def __str__(self):
        """String representation showing address and date."""
        return f"{self.street_address}, {self.city} ({self.as_of_date})"


class SalesComparable(models.Model):
    """
    Sales-specific data for a comparable property.
    
    What: Extends ComparableProperty with sales transaction data.
    Why: Isolates sales-specific fields (prices, dates, DOM) from lease comps.
    Where: OneToOne with ComparableProperty.
    How: Create after ComparableProperty exists; attach sales details.
    """
    # OneToOne link to parent
    comparable_property = models.OneToOneField(
        ComparableProperty,
        on_delete=models.CASCADE,
        related_name='sales_data',
        help_text='Link to parent comparable property.'
    )
    
    # Listing data
    current_listed_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Current listed price of the comparable property.'
    )
    current_listed_date = models.DateField(
        null=True,
        blank=True,
        help_text='Current listed date of the comparable property.'
    )
    
    # Sale data
    last_sales_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Last sales price of the comparable property.'
    )
    last_sales_date = models.DateField(
        null=True,
        blank=True,
        help_text='Last sales date of the comparable property.'
    )
    
    # Sales comp quality rating
    # Will add feature to quantify based on distance, bed/bath match, sale recency, price similarity
    # Like a perfect rating: same block, same bed/baths, same style, sold last month, similar price/sqft
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    comp_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text='Sales comp quality: 1 (poor match) to 5 (excellent match). Based on distance, bed/bath, sale recency, price similarity.'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_sales_comparable'
        verbose_name = 'Sales Comparable'
        verbose_name_plural = 'Sales Comparables'
        ordering = ['-last_sales_date']
    
    def __str__(self):
        """String representation showing sale price and date."""
        price = f"${self.last_sales_price:,.0f}" if self.last_sales_price else "N/A"
        return f"Sale: {price} on {self.last_sales_date or 'N/A'}"
    
    # ----- Calculated helpers (sales-specific) -----
    def last_sale_price_per_unit(self) -> Decimal:
        """
        Calculate last sale price per unit.

        What: Divides `last_sales_price` by `units` from parent.
        Why: Useful for normalizing comparable sale across multi-unit properties.
        How: Uses Decimal arithmetic; returns Decimal('0.00') if inputs are missing/zero.

        Returns:
            Decimal: Price per unit rounded to 2 decimals.
        """
        if not self.last_sales_price or not self.comparable_property.units or self.comparable_property.units <= 0:
            return Decimal('0.00')
        price = self.last_sales_price if isinstance(self.last_sales_price, Decimal) else Decimal(str(self.last_sales_price))
        units = Decimal(str(self.comparable_property.units))
        return (price / units).quantize(Decimal('0.01'))

    def last_sale_price_per_gross_sqft(self) -> Decimal:
        """
        Calculate last sale price per gross building square foot.

        What: Divides `last_sales_price` by `gross_square_ft_building` from parent.
        Why: Normalizes comparable sale by building size (gross).
        How: Uses Decimal; returns Decimal('0.00') if inputs are missing/zero.

        Returns:
            Decimal: Price per gross sqft rounded to 2 decimals.
        """
        if not self.last_sales_price or not self.comparable_property.gross_square_ft_building or self.comparable_property.gross_square_ft_building <= 0:
            return Decimal('0.00')
        price = self.last_sales_price if isinstance(self.last_sales_price, Decimal) else Decimal(str(self.last_sales_price))
        sqft = Decimal(str(self.comparable_property.gross_square_ft_building))
        return (price / sqft).quantize(Decimal('0.01'))

    def last_sale_price_per_livable_sqft(self) -> Decimal:
        """
        Calculate last sale price per livable building square foot.

        What: Divides `last_sales_price` by `livable_square_ft_building` from parent.
        Why: Normalizes comparable sale by usable/livable area.
        How: Uses Decimal; returns Decimal('0.00') if inputs are missing/zero.

        Returns:
            Decimal: Price per livable sqft rounded to 2 decimals.
        """
        if not self.last_sales_price or not self.comparable_property.livable_square_ft_building or self.comparable_property.livable_square_ft_building <= 0:
            return Decimal('0.00')
        price = self.last_sales_price if isinstance(self.last_sales_price, Decimal) else Decimal(str(self.last_sales_price))
        sqft = Decimal(str(self.comparable_property.livable_square_ft_building))
        return (price / sqft).quantize(Decimal('0.01'))

    def days_on_market(self) -> int:
        """
        Calculate Days on Market (DOM) using `as_of_date` from parent and `current_listed_date`.

        What: Number of days between the listing date and the as-of date.
        Why: Useful for market activity and pricing analysis of comparables.
        How: If either date is missing or inconsistent (as_of before listed), returns 0.

        Returns:
            int: Non-negative integer days on market.
        """
        # Ensure dates exist
        if not self.current_listed_date or not self.comparable_property.as_of_date:
            return 0
        # Compute delta; clamp to 0 if as_of predates listing
        try:
            delta_days = (self.comparable_property.as_of_date - self.current_listed_date).days  # type: ignore[operator]
            return delta_days if delta_days > 0 else 0
        except Exception:
            # On any unexpected date issue, default to 0
            return 0


class LeaseComparable(models.Model):
    """
    Lease-specific data for a comparable property.
    
    What: Extends ComparableProperty with lease/rent data.
    Why: Isolates lease-specific fields (rent, lease terms, CAM) from sales comps.
    Where: OneToOne with ComparableProperty.
    How: Create after ComparableProperty exists; attach lease details.
    """
    # OneToOne link to parent
    comparable_property = models.OneToOneField(
        ComparableProperty,
        on_delete=models.CASCADE,
        related_name='lease_data',
        help_text='Link to parent comparable property.'
    )
    # Lease/Rent data
    monthly_rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly rent amount.'
    )
    lease_start_date = models.DateField(
        null=True,
        blank=True,
        help_text='Lease start date.'
    )
    lease_end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Lease end date.'
    )
    lease_term_months = models.IntegerField(
        null=True,
        blank=True,
        help_text='Lease term in months.'
    )
    lease_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Type of lease (e.g., NNN, Gross, Modified Gross).'
    )
    lease_escalation = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Lease escalation percentage.'
    )
    lease_escalation_frequency = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Lease escalation frequency (e.g., Annual, Semi-Annual, Quarterly).'
    )
    # CAM (Common Area Maintenance) charges
    cam_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly CAM charge.'
    )
    
   
    # Lease comp quality rating
    # Will add feature to quantify based on rent similarity, lease terms, amenities, location, tenant quality
    # Like a perfect rating: similar rent/sqft, same lease type, comparable amenities, same submarket, recent lease
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    comp_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text='Lease comp quality: 1 (poor match) to 5 (excellent match). Based on rent similarity, lease terms, amenities, location.'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_lease_comparable'
        verbose_name = 'Lease Comparable'
        verbose_name_plural = 'Lease Comparables'
        ordering = ['-lease_start_date']
    
    def __str__(self):
        """String representation showing rent and lease term."""
        rent = f"${self.monthly_rent:,.2f}/mo" if self.monthly_rent else "N/A"
        return f"Lease: {rent} ({self.lease_term_months or '?'} months)"
    
    # ----- Calculated helpers (lease-specific) -----
    def annual_rent(self) -> Decimal:
        """
        Calculate annual rent (monthly rent * 12).

        Returns:
            Decimal: Annual rent rounded to 2 decimals.
        """
        if not self.monthly_rent:
            return Decimal('0.00')
        monthly = self.monthly_rent if isinstance(self.monthly_rent, Decimal) else Decimal(str(self.monthly_rent))
        return (monthly * Decimal('12')).quantize(Decimal('0.01'))
    
    def rent_per_sqft(self) -> Decimal:
        """
        Calculate monthly rent per square foot (uses livable sqft from parent).

        Returns:
            Decimal: Rent per sqft rounded to 2 decimals.
        """
        if not self.monthly_rent or not self.comparable_property.livable_square_ft_building or self.comparable_property.livable_square_ft_building <= 0:
            return Decimal('0.00')
        monthly = self.monthly_rent if isinstance(self.monthly_rent, Decimal) else Decimal(str(self.monthly_rent))
        sqft = Decimal(str(self.comparable_property.livable_square_ft_building))
        return (monthly / sqft).quantize(Decimal('0.01'))
    
    def cam_per_sqft(self) -> Decimal:
        """
        Calculate monthly CAM per square foot (uses livable sqft from parent).

        Returns:
            Decimal: CAM per sqft rounded to 2 decimals.
        """
        if not self.cam_monthly or not self.comparable_property.livable_square_ft_building or self.comparable_property.livable_square_ft_building <= 0:
            return Decimal('0.00')
        cam = self.cam_monthly if isinstance(self.cam_monthly, Decimal) else Decimal(str(self.cam_monthly))
        sqft = Decimal(str(self.comparable_property.livable_square_ft_building))
        return (cam / sqft).quantize(Decimal('0.01'))
    
    def annual_cam(self) -> Decimal:
        """
        Calculate annual CAM (monthly CAM * 12).

        Returns:
            Decimal: Annual CAM rounded to 2 decimals.
        """
        if not self.cam_monthly:
            return Decimal('0.00')
        cam = self.cam_monthly if isinstance(self.cam_monthly, Decimal) else Decimal(str(self.cam_monthly))
        return (cam * Decimal('12')).quantize(Decimal('0.01'))


class LeaseComparableUnitMix(models.Model):
    """
    Unit mix data for multi-family/commercial comparable properties.
    
    What: Stores aggregated unit type data for lease comps (e.g., "20 1BR @ avg $1200/mo").
    Why: More common to get unit mix summaries than full rent rolls for lease comps.
    Where: Many-to-One with ComparableProperty (multiple unit types per property).
    How: Create parent ComparableProperty first, then add unit mix records. Mirrors UnitMix model.
    """
    # Many-to-One link to parent property
    comparable_property = models.ForeignKey(
        ComparableProperty,
        on_delete=models.CASCADE,
        related_name='lease_unit_mix',
        help_text='Link to parent comparable property; multiple unit types per property supported.'
    )
    
    # Unit characteristics (mirrors UnitMix model)
    unit_type = models.CharField(
        max_length=50,
        help_text="Type of unit (e.g., '1BR', '2BR', 'Studio', 'Retail', 'Office')"
    )
    unit_count = models.IntegerField(
        help_text="Number of units of this type"
    )
    unit_avg_sqft = models.IntegerField(
        help_text="Average square footage per unit of this type"
    )
    unit_avg_rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Average monthly rent per unit of this type"
    )
    
    # Calculated field: price per square foot (auto-computed on save)
    price_sqft = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        help_text="Calculated: unit_avg_rent / unit_avg_sqft (rent per sqft)"
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this unit type"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_lease_comparable_unit_mix'
        verbose_name = 'Lease Comparable Unit Mix'
        verbose_name_plural = 'Lease Comparable Unit Mix Records'
        ordering = ['comparable_property', 'unit_type']
        indexes = [
            models.Index(fields=['comparable_property', 'unit_type']),
        ]
    
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


class LeaseComparableRentRoll(models.Model):
    """
    Unit-level rent roll data for multi-family/commercial comparable properties.
    
    What: Stores per-unit lease details for multi-family or commercial comparables (rare).
    Why: Multi-family properties need unit-by-unit rent roll analysis, not just property-level summary.
    Where: Many-to-One with ComparableProperty (multiple units per property).
    How: Create parent ComparableProperty first, then add unit records. Similar to RentRoll model.
    Note: Use LeaseComparableUnitMix for aggregated data (more common); use this for full rent rolls.
    """
    # Many-to-One link to parent property
    comparable_property = models.ForeignKey(
        ComparableProperty,
        on_delete=models.CASCADE,
        related_name='lease_units',
        help_text='Link to parent comparable property; multiple units per property supported.'
    )
    
    # Unit identification
    unit_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Unit number or identifier (e.g., "101", "2A", "Suite 200").'
    )
    
    # Unit characteristics
    beds = models.IntegerField(
        null=True,
        blank=True,
        help_text='Number of bedrooms in this unit (overrides property-level if specified).'
    )
    baths = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text='Number of bathrooms in this unit (e.g., 2.5).'
    )
    unit_sqft = models.IntegerField(
        null=True,
        blank=True,
        help_text='Square footage of this unit.'
    )
    
    # Lease terms (per unit)
    monthly_rent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly rent for this unit.'
    )
    lease_start_date = models.DateField(
        null=True,
        blank=True,
        help_text='Lease start date for this unit.'
    )
    lease_end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Lease end date for this unit.'
    )
    lease_term_months = models.IntegerField(
        null=True,
        blank=True,
        help_text='Lease term in months for this unit.'
    )
    lease_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Type of lease for this unit (e.g., NNN, Gross, Modified Gross).'
    )
    
    # Escalations and CAM (per unit)
    lease_escalation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Lease escalation percentage for this unit (e.g., 3.00 for 3%).'
    )
    lease_escalation_frequency = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Escalation frequency (e.g., Annual, Semi-Annual, Quarterly).'
    )
    cam_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly CAM charge for this unit.'
    )
    
    # Occupancy status
    is_occupied = models.BooleanField(
        default=True,
        help_text='Whether this unit is currently occupied.'
    )
    tenant_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Tenant name (optional, for tracking).'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes about this unit lease.'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_lease_comparable_unit'
        verbose_name = 'Lease Comparable Unit'
        verbose_name_plural = 'Lease Comparable Units'
        ordering = ['comparable_property', 'unit_number']
        indexes = [
            models.Index(fields=['comparable_property', 'unit_number']),
            models.Index(fields=['is_occupied']),
        ]
    
    def __str__(self):
        """String representation showing unit number and rent."""
        unit = self.unit_number or 'Unit'
        rent = f"${self.monthly_rent:,.2f}/mo" if self.monthly_rent else "N/A"
        return f"{unit}: {rent}"
    
    # ----- Calculated helpers (unit-specific) -----
    def annual_rent(self) -> Decimal:
        """
        Calculate annual rent for this unit (monthly rent * 12).

        Returns:
            Decimal: Annual rent rounded to 2 decimals.
        """
        if not self.monthly_rent:
            return Decimal('0.00')
        monthly = self.monthly_rent if isinstance(self.monthly_rent, Decimal) else Decimal(str(self.monthly_rent))
        return (monthly * Decimal('12')).quantize(Decimal('0.01'))
    
    def rent_per_sqft(self) -> Decimal:
        """
        Calculate monthly rent per square foot for this unit.

        Returns:
            Decimal: Rent per sqft rounded to 2 decimals.
        """
        if not self.monthly_rent or not self.unit_sqft or self.unit_sqft <= 0:
            return Decimal('0.00')
        monthly = self.monthly_rent if isinstance(self.monthly_rent, Decimal) else Decimal(str(self.monthly_rent))
        sqft = Decimal(str(self.unit_sqft))
        return (monthly / sqft).quantize(Decimal('0.01'))
    
    def cam_per_sqft(self) -> Decimal:
        """
        Calculate monthly CAM per square foot for this unit.

        Returns:
            Decimal: CAM per sqft rounded to 2 decimals.
        """
        if not self.cam_monthly or not self.unit_sqft or self.unit_sqft <= 0:
            return Decimal('0.00')
        cam = self.cam_monthly if isinstance(self.cam_monthly, Decimal) else Decimal(str(self.cam_monthly))
        sqft = Decimal(str(self.unit_sqft))
        return (cam / sqft).quantize(Decimal('0.01'))
    
    def annual_cam(self) -> Decimal:
        """
        Calculate annual CAM for this unit (monthly CAM * 12).

        Returns:
            Decimal: Annual CAM rounded to 2 decimals.
        """
        if not self.cam_monthly:
            return Decimal('0.00')
        cam = self.cam_monthly if isinstance(self.cam_monthly, Decimal) else Decimal(str(self.cam_monthly))
        return (cam * Decimal('12')).quantize(Decimal('0.01'))



