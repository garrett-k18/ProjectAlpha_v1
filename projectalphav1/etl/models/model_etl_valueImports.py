"""ETL staging models for valuation-related data (BPOs, appraisals)."""

from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from core.models import AssetIdHub
from core.models.valuations import Valuation
from core.models.model_co_lookupTables import (
    AppraisalPurpose,
    BpoType,
    CompRanking,
    CompType,
    Condition,
    CoolingType,
    FinancingType,
    FoundationType,
    Garage,
    HeatingType,
    LocationType,
    MarketTrend,
    MarketingTime,
    Occupancy,
    OwnershipType,
    PhotoType,
    Pride,
    PropertyRights,
    PropertyTypeDetail,
    RepairCategory,
    RepairType,
    RiskLevel,
    SalesStrategy,
    SalesType,
    Severity,
    Style,
    SubjectAppeal,
    Supply,
    ValuationType,
    View,
    WaterType,
    SewerType,
)


class ValuationETL(models.Model):
    """Unified valuation payload captured during ETL before syncing to core tables."""

    # Core relationships
    asset_hub = models.ForeignKey(
        AssetIdHub,
        on_delete=models.PROTECT,
        related_name="etl_valuations",
        help_text="Canonical hub join key for this valuation record.",
    )
    source = models.CharField(
        max_length=20,
        choices=Valuation.Source.choices,
        blank=True,
        null=True,
        help_text="Valuation source code aligned with core Valuation model choices.",
    )

    # Valuation metadata
    valuation_type = models.CharField(max_length=20, choices=ValuationType.choices, db_index=True)
    bpo_type = models.CharField(max_length=20, choices=BpoType.choices, blank=True)

    # Property identification
    property_address = models.CharField(max_length=255, db_index=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10, db_index=True)
    parcel_number = models.CharField(max_length=100, blank=True, db_index=True)

    # Order/loan information
    loan_number = models.CharField(max_length=50, blank=True, db_index=True)
    deal_name = models.CharField(max_length=100, blank=True)

    # Dates
    inspection_date = models.DateField(db_index=True)
    effective_date = models.DateField(blank=True, null=True)
    report_date = models.DateField(blank=True, null=True)

    # Property status
    occupancy_status = models.CharField(max_length=20, choices=Occupancy.choices, blank=True)
    property_appears_secure = models.BooleanField(default=True)

    # Financials
    yearly_taxes = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_monthly_rent_repaired = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Recent sale/listing
    sold_in_last_12_months = models.BooleanField(default=False)
    prior_sale_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    prior_sale_date = models.DateField(blank=True, null=True)
    currently_listed = models.BooleanField(default=False)
    listing_broker = models.CharField(max_length=255, blank=True)
    listing_agent_email = models.EmailField(blank=True)
    listing_agent_firm = models.CharField(max_length=255, blank=True)
    initial_list_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    initial_list_date = models.DateField(blank=True, null=True)
    current_list_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    days_on_market = models.IntegerField(blank=True, null=True, help_text="Days on market")
    listing_currently_pending = models.BooleanField(default=False)
    pending_contract_date = models.DateField(blank=True, null=True)

    # Property characteristics
    living_area = models.IntegerField(blank=True, null=True)
    total_rooms = models.IntegerField(blank=True, null=True)
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, help_text="Total bathrooms (e.g., 2.5)")
    year_built = models.IntegerField(blank=True, null=True)
    effective_age = models.IntegerField(blank=True, null=True)
    foundation_type = models.CharField(max_length=30, choices=FoundationType.choices, blank=True)
    basement_square_feet = models.IntegerField(blank=True, null=True)
    lot_size_acres = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, help_text="Lot size in acres (convert from sq ft if needed: acres = sq_ft / 43560)")
    property_type = models.CharField(max_length=20, choices=PropertyTypeDetail.choices, blank=True)
    style = models.CharField(max_length=20, choices=Style.choices, blank=True)
    number_of_units = models.IntegerField(default=1)
    condition = models.CharField(max_length=20, choices=Condition.choices, blank=True)

    # Features (condensed)
    has_pool = models.BooleanField(default=False)
    has_deck = models.BooleanField(default=False)
    has_fireplace = models.BooleanField(default=False)
    has_fencing = models.BooleanField(default=False)
    garage = models.CharField(max_length=20, choices=Garage.choices, blank=True)
    garage_spaces = models.IntegerField(blank=True, null=True)
    parking_spaces = models.IntegerField(blank=True, null=True)
    parking_type = models.CharField(max_length=50, blank=True)
    cooling_type = models.CharField(max_length=50, choices=CoolingType.choices, blank=True)
    heating_type = models.CharField(max_length=50, choices=HeatingType.choices, blank=True)
    water_type = models.CharField(max_length=20, choices=WaterType.choices, blank=True)
    sewer_type = models.CharField(max_length=20, choices=SewerType.choices, blank=True)
    hoa_fees_monthly = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    hoa_fees_annual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    subdivision = models.CharField(max_length=255, blank=True)
    school_district = models.CharField(max_length=255, blank=True)

    # Data source
    data_source = models.CharField(max_length=50, blank=True)
    data_source_id = models.CharField(max_length=50, blank=True)

    # Valuation estimates
    as_is_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    as_repaired_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    quick_sale_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    quick_sale_value_repaired = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    land_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    estimated_marketing_time = models.CharField(max_length=20, choices=MarketingTime.choices, blank=True)
    typical_marketing_time_days = models.IntegerField(blank=True, null=True)
    recommended_sales_strategy = models.CharField(max_length=20, choices=SalesStrategy.choices, blank=True)
    recommended_list_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    recommended_list_price_repaired = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Appraisal specifics
    property_rights_appraised = models.CharField(max_length=20, choices=PropertyRights.choices, blank=True)
    sales_comparison_approach = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    cost_approach = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    income_approach = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Market data
    financeable = models.CharField(max_length=50, blank=True)
    market_trend = models.CharField(max_length=20, choices=MarketTrend.choices, blank=True)
    neighborhood_trend = models.CharField(max_length=20, choices=MarketTrend.choices, blank=True)
    economic_trend = models.CharField(max_length=20, choices=MarketTrend.choices, blank=True)
    property_values_trend = models.CharField(max_length=50, blank=True)
    subject_appeal_compared_to_avg = models.CharField(max_length=20, choices=SubjectAppeal.choices, blank=True)
    subject_value_compared_to_avg = models.CharField(max_length=20, choices=SubjectAppeal.choices, blank=True)
    housing_supply = models.CharField(max_length=20, choices=Supply.choices, blank=True)
    crime_vandalism_risk = models.CharField(max_length=20, choices=RiskLevel.choices, blank=True)
    reo_driven_market = models.BooleanField(default=False)
    num_reo_ss_listings = models.IntegerField(blank=True, null=True)
    num_listings_in_area = models.IntegerField(blank=True, null=True)
    num_boarded_properties = models.IntegerField(blank=True, null=True)
    new_construction_in_area = models.BooleanField(default=False)
    seasonal_market = models.BooleanField(default=False)
    neighborhood_price_range_low = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    neighborhood_price_range_high = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    neighborhood_median_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    neighborhood_average_sales_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Marketability
    marketability_concerns = models.TextField(blank=True)

    # Comments
    property_comments = models.TextField(blank=True)
    neighborhood_comments = models.TextField(blank=True)
    general_comments = models.TextField(blank=True)

    # Repairs summary
    estimated_repair_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Total estimated repair costs")
    general_repair_comments = models.TextField(blank=True)

    # Professional info - consolidated to single "preparer" (agent or appraiser)
    preparer_name = models.CharField(max_length=255, blank=True, help_text="Name of BPO agent or appraiser who prepared the valuation")
    preparer_company = models.CharField(max_length=255, blank=True, help_text="Company of the preparer")
    preparer_email = models.EmailField(blank=True, help_text="Email of the preparer")
    preparer_phone = models.CharField(max_length=50, blank=True, help_text="Phone number of the preparer")
    preparer_comments = models.TextField(blank=True, help_text="Comments or notes from the preparer")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='valuations_created')

    class Meta:
        db_table = "etl_valuation"
        verbose_name = "Valuation ETL"
        verbose_name_plural = "Valuation ETL Records"
        ordering = ['-inspection_date', '-created_at']
        indexes = [
            models.Index(fields=['valuation_type', 'inspection_date']),
            models.Index(fields=['property_address', 'city', 'state']),
            models.Index(fields=['zip_code', 'inspection_date']),
            models.Index(fields=['loan_number']),
            models.Index(fields=['source']),
        ]

    def __str__(self):
        return f"{self.get_valuation_type_display()} - {self.property_address} ({self.inspection_date})"

    @property
    def price_per_sqft(self):
        if self.as_is_value and self.living_area:
            return round(float(self.as_is_value) / self.living_area, 2)
        return None


class ComparablesETL(models.Model):
    """Comparable properties for BPOs and Appraisals."""

    valuation = models.ForeignKey(ValuationETL, on_delete=models.CASCADE, related_name='comparables')
    comp_type = models.CharField(max_length=20, choices=CompType.choices, db_index=True)
    comp_number = models.IntegerField()
    agent_comp_ranking = models.IntegerField(blank=True, null=True, choices=CompRanking.choices)

    # Location
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    proximity_miles = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Distance from subject property in miles (straight line)")

    # Pricing
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateField(blank=True, null=True)
    price_per_sqft = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    original_list_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    original_list_date = models.DateField(blank=True, null=True)
    current_list_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    days_on_market = models.IntegerField(blank=True, null=True, help_text="Days on market")

    # Transaction details
    sales_type = models.CharField(max_length=20, choices=SalesType.choices, blank=True)
    seller_concessions = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    financing_type = models.CharField(max_length=20, choices=FinancingType.choices, blank=True)

    # Property characteristics
    living_area = models.IntegerField()
    total_rooms = models.IntegerField(blank=True, null=True)
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, help_text="Total bathrooms (e.g., 2.5)")
    year_built = models.IntegerField()
    foundation_type = models.CharField(max_length=30, choices=FoundationType.choices, blank=True)
    basement_square_feet = models.IntegerField(blank=True, null=True)
    lot_size_acres = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True, help_text="Lot size in acres")
    property_type = models.CharField(max_length=20, blank=True)
    style = models.CharField(max_length=20, blank=True)
    number_of_units = models.IntegerField(default=1)
    condition = models.CharField(max_length=20, blank=True)

    # Features (condensed - same as ValuationETL)
    has_pool = models.BooleanField(default=False)
    has_deck = models.BooleanField(default=False)
    has_fireplace = models.BooleanField(default=False)
    has_fencing = models.BooleanField(default=False)
    garage = models.CharField(max_length=20, blank=True)
    parking_spaces = models.IntegerField(blank=True, null=True)
    parking_type = models.CharField(max_length=50, blank=True)
    cooling_type = models.CharField(max_length=50, blank=True)
    heating_type = models.CharField(max_length=50, blank=True)
    water_type = models.CharField(max_length=20, blank=True)
    sewer_type = models.CharField(max_length=20, blank=True)
    hoa_fees_monthly = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    subdivision = models.CharField(max_length=255, blank=True)
    school_district = models.CharField(max_length=255, blank=True)

    # Data source
    data_source = models.CharField(max_length=50, blank=True)
    data_source_id = models.CharField(max_length=50, blank=True)

    # Adjustments (simplified - keep only totals)
    total_adjustments = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total $ adjustments made to comparable")
    adjusted_sale_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Sale price after adjustments")

    # Comments
    general_comments = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "etl_comparable"
        ordering = ['comp_type', 'comp_number']
        unique_together = ['valuation', 'comp_type', 'comp_number']
        indexes = [
            models.Index(fields=['valuation', 'comp_type']),
            models.Index(fields=['sale_date']),
        ]

    def __str__(self):
        return f"{self.get_comp_type_display()} #{self.comp_number} - {self.address}"

    def save(self, *args, **kwargs):
        # Calculate price per square foot
        if self.sale_price and self.living_area:
            self.price_per_sqft = round(float(self.sale_price) / self.living_area, 2)
        
        # Calculate adjusted sale price if total_adjustments provided
        if self.sale_price and self.adjusted_sale_price is None and self.total_adjustments != 0:
            self.adjusted_sale_price = self.sale_price + self.total_adjustments
        
        super().save(*args, **kwargs)


class RepairItem(models.Model):
    """Individual repair items for a valuation."""

    valuation = models.ForeignKey(ValuationETL, on_delete=models.CASCADE, related_name='repair_items')
    repair_type = models.CharField(max_length=10, choices=RepairType.choices)
    category = models.CharField(max_length=30, choices=RepairCategory.choices)
    description = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    repair_recommended = models.BooleanField(default=False, help_text="Whether this repair is recommended")

    class Meta:
        db_table = "etl_repair_item"
        ordering = ['repair_type', 'category']

    def __str__(self):
        return f"{self.get_category_display()} - ${self.estimated_cost}"


class ValuationPhoto(models.Model):
    """Photos associated with a valuation."""

    valuation = models.ForeignKey(ValuationETL, on_delete=models.CASCADE, related_name='photos')
    photo_type = models.CharField(max_length=30, choices=PhotoType.choices)
    image = models.ImageField(upload_to='valuation_photos/%Y/%m/%d/')
    caption = models.CharField(max_length=255, blank=True)
    taken_at = models.DateTimeField(blank=True, null=True)
    comparable = models.ForeignKey(ComparablesETL, on_delete=models.CASCADE, blank=True, null=True, related_name='photos')
    repair_item = models.ForeignKey(RepairItem, on_delete=models.CASCADE, blank=True, null=True, related_name='photos')
    display_order = models.IntegerField(default=0)

    class Meta:
        db_table = "etl_valuation_photo"
        ordering = ['photo_type', 'display_order']

    def __str__(self):
        return f"{self.get_photo_type_display()} - {self.valuation.property_address}"
