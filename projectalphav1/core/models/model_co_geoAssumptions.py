from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class StateReference(models.Model):
    """Model to store state-specific data and regulations"""
    state_code = models.CharField(max_length=2, primary_key=True)
    state_name = models.CharField(max_length=50)
    judicialvsnonjudicial = models.BooleanField(default=False, help_text="Is this a judicial foreclosure state")   
    
    fc_state_months = models.IntegerField(help_text="Average months to complete foreclosure")
    eviction_duration = models.IntegerField(help_text="Average months to complete eviction")
    rehab_duration = models.IntegerField(help_text="Average months to complete rehab")
    reo_marketing_duration = models.IntegerField(help_text="Average months to complete reo marketing")
    reo_local_market_ext_duration = models.IntegerField(help_text="Average months to complete reo local market extension")
    dil_duration_avg = models.IntegerField(help_text="Average months to complete dilution")
    

    # Tax data (stored as decimals with 4 decimal places: 0.0063 = 0.63%)
    # Validation: 0.0000 (0%) to 1.0000 (100%)
    property_tax_rate = models.DecimalField(
        max_digits=6, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000')), MaxValueValidator(Decimal('1.0000'))],
        help_text="Average property tax rate (as decimal: 0.0063 = 0.63%, range: 0-100%)"
    )
    transfer_tax_rate = models.DecimalField(
        max_digits=6, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000')), MaxValueValidator(Decimal('1.0000'))],
        help_text="Tax rate for property transfers (as decimal: 0.0033 = 0.33%, range: 0-100%)"
    )
    insurance_rate_avg = models.DecimalField(
        max_digits=6, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000')), MaxValueValidator(Decimal('1.0000'))],
        help_text="Average insurance rate (as decimal: 0.0040 = 0.40%, range: 0-100%)"
    )
    broker_closing_cost_fees_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average broker closing cost fees")
    other_closing_cost_fees_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average other closing cost fees")
    # Legal fees
    fc_legal_fees_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average legal fees for foreclosure")
    dil_cost_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average dilution cost")
    cfk_cost_avg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Average CFK cost")
    
    # Value adjustment can be negative (depreciation) or positive (appreciation)
    # Validation: -1.0000 (-100%) to 1.0000 (100%)
    value_adjustment_annual = models.DecimalField(
        max_digits=6, 
        decimal_places=4,
        validators=[MinValueValidator(Decimal('-1.0000')), MaxValueValidator(Decimal('1.0000'))],
        help_text="Average value adjustment (as decimal: 0.0028 = 0.28%, range: -100% to +100%)"
    )
    
    # State-specific utility costs (monthly averages in dollars)
    utility_electric_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly electric utility cost in dollars"
    )
    utility_gas_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly gas utility cost in dollars"
    )
    utility_water_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly water utility cost in dollars"
    )
    utility_sewer_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly sewer utility cost in dollars"
    )
    utility_trash_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly trash utility cost in dollars"
    )
    utility_other_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly other utility costs in dollars"
    )
    
    # State-specific property management costs (monthly averages in dollars)
    property_management_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly property management cost in dollars"
    )
    repairs_maintenance_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly repairs and maintenance cost in dollars"
    )
    marketing_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly marketing cost in dollars"
    )
    security_cost_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly security cost in dollars"
    )
    landscaping_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly landscaping cost in dollars"
    )
    pool_maintenance_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average monthly pool maintenance cost in dollars"
    )
    
    # State-specific one-time costs (averages in dollars)
    trashout_cost_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average one-time trashout cost in dollars"
    )
    renovation_cost_avg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Average one-time renovation cost in dollars"
    )


    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "State Reference"
        verbose_name_plural = "State References"
        ordering = ['state_name']
        indexes = [
            models.Index(fields=['state_code']),
        ]
        db_table = 'state_reference'
    
    def __str__(self):
        return self.state_name.rstrip('.')

class CountyReference(models.Model):
    """
    WHAT: Model to store county-level reference data
    WHY: Counties are key geographic units for regulations, taxes, and legal processes
    HOW: Populated from Census Bureau API with FIPS codes
    
    Use Cases:
    - Property tax calculations (county-specific rates)
    - Legal jurisdiction for foreclosures
    - Recording fees and transfer taxes
    - Market analysis at county level
    
    Geographic Hierarchy:
    - State → County → ZIP codes
    - County may overlap with multiple MSAs
    
    Data Sources:
    - Census Bureau Geographic Reference Files
    - FIPS county codes (5 digits: 2 state + 3 county)
    """
    
    # WHAT: 5-digit FIPS county code (primary key)
    # WHY: Standard federal code for counties
    # HOW: First 2 digits = state FIPS, last 3 = county code
    county_fips = models.CharField(
        max_length=5,
        primary_key=True,
        help_text="5-digit FIPS code (2-digit state + 3-digit county)"
    )
    
    # WHAT: County name
    # WHY: Human-readable identifier
    county_name = models.CharField(
        max_length=100,
        help_text="Official county name (e.g., 'Los Angeles County', 'Cook County')"
    )
    
    # WHAT: Foreign key to StateReference
    # WHY: Every county belongs to a state
    # HOW: Required field for geographic hierarchy
    state = models.ForeignKey(
        StateReference,
        on_delete=models.PROTECT,  # Don't allow deleting states with counties
        related_name='counties',
        help_text="State this county belongs to"
    )
    
    # WHAT: Optional population data
    # WHY: Useful for market sizing and analysis
    # HOW: Can be updated from Census API periodically
    population = models.IntegerField(
        null=True,
        blank=True,
        help_text="County population (from latest Census estimate)"
    )
    
    # WHAT: County seat (main city)
    # WHY: Identifies where county government/courthouse is located
    county_seat = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="County seat (main city where courthouse is located)"
    )
    
    class Meta:
        verbose_name = "County Reference"
        verbose_name_plural = "County References"
        ordering = ['state', 'county_name']
        indexes = [
            models.Index(fields=['county_fips']),
            models.Index(fields=['state']),
            models.Index(fields=['county_name']),
            models.Index(fields=['state', 'county_name']),  # Composite for state queries
        ]
        db_table = 'county_reference'
    
    def __str__(self):
        return f"{self.county_name}, {self.state.state_code if self.state else '??'}"
    
    def get_full_name(self) -> str:
        """
        WHAT: Get full county name with state
        WHY: Unambiguous identification (many states have same county names)
        RETURNS: "Los Angeles County, CA"
        """
        county_display = self.county_name
        if not county_display.lower().endswith('county'):
            county_display += ' County'
        return f"{county_display}, {self.state.state_code if self.state else '??'}"


class MSAReference(models.Model):
    """
    WHAT: Model to store MSA (Metropolitan Statistical Area) reference data
    WHY: Provides geographic market data for broker assignments and market analysis
    HOW: Populated from Census Bureau API with CBSA codes and names
    """
    msa_code = models.CharField(
        max_length=5, 
        primary_key=True,
        help_text="5-digit CBSA code from Census Bureau"
    )
    msa_name = models.CharField(
        max_length=255,
        help_text="Full MSA name from Census Bureau (e.g., 'New York-Newark-Jersey City, NY-NJ-PA')"
    )
    
    # WHAT: Foreign key to StateReference for primary state
    # WHY: Link MSA to its primary state for filtering and referential integrity
    # HOW: Parsed from MSA name or assigned during import
    state = models.ForeignKey(
        StateReference,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='msas',
        help_text="Primary state for this MSA"
    )
    
    class Meta:
        verbose_name = "MSA Reference"
        verbose_name_plural = "MSA References"
        ordering = ['msa_name']
        indexes = [
            models.Index(fields=['msa_code']),
            models.Index(fields=['state']),
            models.Index(fields=['msa_name']),
        ]
        db_table = 'msa_reference'
    
    def __str__(self):
        return f"{self.msa_name} ({self.msa_code})"


class ZIPReference(models.Model):
    """
    WHAT: Model to store ZIP code reference data with MSA and state linkage
    WHY: Enable geocoding of assets by ZIP → MSA → Broker assignments
    HOW: Populated from Census Bureau Geocoding API or HUD USPS ZIP Crosswalk
    
    Use Cases:
    - Geocode asset by ZIP code to determine MSA
    - Assign brokers to assets based on ZIP → MSA mapping
    - Filter assets by geographic market (ZIP/MSA/State hierarchy)
    - Validate and standardize address data
    
    Data Sources:
    - Census Bureau Geocoding API
    - HUD USPS ZIP-to-MSA Crosswalk (quarterly updates)
    - USPS ZIP Code Database
    NOTE (Deprecated):
    - HUDZIPCBSACrosswalk now provides authoritative ZIP→CBSA data.
    - This model is kept only for legacy joins; new code should use the crosswalk table.
    - Safe to delete once all legacy dependencies are migrated.
    """
    
    # WHAT: 5-digit ZIP code (primary key)
    # WHY: Standard USPS ZIP code format
    zip_code = models.CharField(
        max_length=5,
        primary_key=True,
        help_text="5-digit ZIP code (USPS format)"
    )
    
    # WHAT: Foreign key to MSAReference
    # WHY: Link ZIP to its MSA for market-based assignments
    # HOW: Populated from Census/HUD crosswalk data
    # NOTE: Nullable because rural ZIPs may not be in any MSA
    msa = models.ForeignKey(
        MSAReference,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='zip_codes',
        help_text="MSA this ZIP code belongs to (null for rural areas)"
    )
    
    # WHAT: Foreign key to StateReference
    # WHY: Every ZIP belongs to a state
    # HOW: Required field for data integrity
    state = models.ForeignKey(
        StateReference,
        on_delete=models.PROTECT,  # Don't allow deleting states with ZIPs
        related_name='zip_codes',
        help_text="State this ZIP code belongs to"
    )
    
    # WHAT: Foreign key to CountyReference
    # WHY: Most ZIPs belong to a county (important for legal/tax jurisdiction)
    # HOW: Populated from Census crosswalk data
    # NOTE: Some ZIPs may span multiple counties (use primary county)
    county = models.ForeignKey(
        'CountyReference',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='zip_codes',
        help_text="Primary county this ZIP code belongs to"
    )
    
    # WHAT: Primary city name for this ZIP
    # WHY: Display purposes and additional filtering
    # HOW: From USPS or Census data
    city_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Primary city name for this ZIP code"
    )
    
    # WHAT: All county FIPS codes for ZIPs spanning multiple counties
    # WHY: Some ZIPs span multiple counties - track them all
    # HOW: Pipe-separated list (e.g., "06037|06059")
    county_fips_all = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="All county FIPS codes for this ZIP (pipe-separated for multi-county ZIPs)"
    )
    
    # WHAT: County distribution weights as JSON
    # WHY: Track percentage of ZIP in each county
    # HOW: Store as text JSON (e.g., '{"06037": 75.5, "06059": 24.5}')
    county_weights = models.TextField(
        blank=True,
        null=True,
        help_text="JSON of county FIPS to percentage weight for multi-county ZIPs"
    )
    
    # WHAT: ZIP type classification
    # WHY: Different ZIP types have different characteristics
    # HOW: Standard, PO Box, Unique (single building), Military
    class ZIPType(models.TextChoices):
        STANDARD = 'STANDARD', 'Standard'
        PO_BOX = 'PO_BOX', 'PO Box'
        UNIQUE = 'UNIQUE', 'Unique (Single Building)'
        MILITARY = 'MILITARY', 'Military'
    
    zip_type = models.CharField(
        max_length=20,
        choices=ZIPType.choices,
        default=ZIPType.STANDARD,
        help_text="ZIP code type classification"
    )
    
    class Meta:
        verbose_name = "ZIP Code Reference"
        verbose_name_plural = "ZIP Code References"
        ordering = ['zip_code']
        indexes = [
            models.Index(fields=['zip_code']),
            models.Index(fields=['state']),
            models.Index(fields=['county']),
            models.Index(fields=['msa']),
            models.Index(fields=['city_name']),
            models.Index(fields=['state', 'msa']),  # Composite for geographic queries
            models.Index(fields=['state', 'county']),  # Composite for county queries
        ]
        db_table = 'zip_reference'
    
    def __str__(self):
        if self.city_name:
            return f"{self.zip_code} - {self.city_name}, {self.state.state_code if self.state else '??'}"
        return f"{self.zip_code}"
    
    def get_full_location(self) -> str:
        """
        WHAT: Get full location string for display
        WHY: Useful for dropdowns and reports
        RETURNS: "90210 - Beverly Hills, CA (Los Angeles County, Los Angeles MSA)"
        """
        parts = [self.zip_code]
        if self.city_name:
            parts.append(f"{self.city_name}, {self.state.state_code if self.state else '??'}")
        
        # Add county and/or MSA info
        geo_info = []
        if self.county:
            geo_info.append(self.county.county_name)
        if self.msa:
            geo_info.append(self.msa.msa_name)
        
        if geo_info:
            parts.append(f"({', '.join(geo_info)})")
        
        return " - ".join(parts)


class HUDZIPCBSACrosswalk(models.Model):
    """
    WHAT: Raw HUD ZIP-to-CBSA crosswalk data (quarterly snapshot)
    WHY: Provides ZIP → MSA mapping without complex FK constraints
    HOW: Bulk imported directly from HUD USPS ZIP_CBSA CSV file
    
    Use Cases:
    - Join seller tape ZIPs to CBSA/MSA codes for broker assignments
    - Reference table for geographic market analysis
    - Preserves HUD's original ratio data for split ZIPs
    
    Data Source:
    - HUD USPS ZIP Code Crosswalk Files (quarterly)
    - https://www.huduser.gov/portal/datasets/usps_crosswalk.html
    
    Import Strategy:
    - Truncate and reload quarterly when HUD releases new data
    - Keep ALL rows including micro areas (filter in queries as needed)
    - No FK constraints = fast bulk import without validation overhead
    """
    
    # WHAT: 5-digit ZIP code
    # WHY: Primary geographic identifier from seller tapes
    # HOW: Direct from HUD CSV 'ZIP' column
    zip_code = models.CharField(
        max_length=5,
        db_index=True,
        help_text="5-digit ZIP code from HUD crosswalk"
    )
    
    # WHAT: 5-digit CBSA (MSA/Micro) code
    # WHY: Links ZIP to its Metropolitan/Micropolitan Statistical Area
    # HOW: Direct from HUD CSV 'CBSA' column (can be blank for rural ZIPs)
    cbsa_code = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        db_index=True,
        help_text="5-digit CBSA code (blank for rural ZIPs)"
    )
    
    # WHAT: Preferred city name for this ZIP
    # WHY: Display and filtering purposes
    # HOW: Direct from HUD CSV 'USPS_ZIP_PREF_CITY' column
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="USPS preferred city name"
    )
    
    # WHAT: Two-letter state postal abbreviation
    # WHY: Every ZIP belongs to a state
    # HOW: Direct from HUD CSV 'USPS_ZIP_PREF_STATE' column
    state_code = models.CharField(
        max_length=2,
        db_index=True,
        help_text="Two-letter state code"
    )
    
    # WHAT: Residential address ratio
    # WHY: Percentage of residential addresses in this ZIP within this CBSA
    # HOW: Direct from HUD CSV 'RES_RATIO' column (0.0 to 1.0)
    res_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=9,
        default=Decimal('0.0'),
        help_text="Residential address ratio (0.0 to 1.0)"
    )
    
    # WHAT: Business address ratio
    # WHY: Percentage of business addresses in this ZIP within this CBSA
    # HOW: Direct from HUD CSV 'BUS_RATIO' column (0.0 to 1.0)
    bus_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=9,
        default=Decimal('0.0'),
        help_text="Business address ratio (0.0 to 1.0)"
    )
    
    # WHAT: Other address ratio
    # WHY: Percentage of other delivery points in this ZIP within this CBSA
    # HOW: Direct from HUD CSV 'OTH_RATIO' column (0.0 to 1.0)
    oth_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=9,
        default=Decimal('0.0'),
        help_text="Other address ratio (0.0 to 1.0)"
    )
    
    # WHAT: Total address ratio (weighted average)
    # WHY: Overall percentage of addresses in this ZIP within this CBSA
    # HOW: Direct from HUD CSV 'TOT_RATIO' column (0.0 to 1.0)
    # NOTE: Use this field to pick dominant CBSA when a ZIP spans multiple markets
    tot_ratio = models.DecimalField(
        max_digits=12,
        decimal_places=9,
        default=Decimal('0.0'),
        db_index=True,
        help_text="Total address ratio (0.0 to 1.0) - use for dominant CBSA selection"
    )
    
    # WHAT: Import timestamp
    # WHY: Track when this data was loaded (HUD releases quarterly)
    # HOW: Auto-set on record creation
    imported_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was imported"
    )
    
    class Meta:
        verbose_name = "HUD ZIP-CBSA Crosswalk"
        verbose_name_plural = "HUD ZIP-CBSA Crosswalks"
        ordering = ['zip_code', '-tot_ratio']  # Order by ZIP, then dominant CBSA first
        indexes = [
            models.Index(fields=['zip_code']),
            models.Index(fields=['cbsa_code']),
            models.Index(fields=['state_code']),
            models.Index(fields=['zip_code', 'cbsa_code']),  # Composite for join queries
            models.Index(fields=['zip_code', '-tot_ratio']),  # For finding dominant CBSA
        ]
        db_table = 'hud_zip_cbsa_crosswalk'
    
    def __str__(self):
        if self.cbsa_code:
            return f"{self.zip_code} → CBSA {self.cbsa_code} ({self.tot_ratio:.1%})"
        return f"{self.zip_code} (no CBSA)"
    
    def is_dominant(self) -> bool:
        """
        WHAT: Check if this is the dominant CBSA for this ZIP
        WHY: ZIPs can span multiple CBSAs; we often want just the primary one
        RETURNS: True if tot_ratio > 0.5 (majority of addresses in this CBSA)
        """
        return self.tot_ratio > Decimal('0.5')