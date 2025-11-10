"""Admin configuration for ETL app models."""

from django.contrib import admin
from django.utils.html import format_html

from etl.models import (
    ValuationETL,
    ComparablesETL,
    RepairItem,
    ValuationPhoto,
    ValuationDocument,
    ExtractionFieldResult,
    ExtractionLogEntry,
)


# =============================================================================
# INLINE ADMIN CLASSES
# =============================================================================


class ComparablesETLInline(admin.TabularInline):
    """Inline admin for comparable properties within a valuation."""
    
    model = ComparablesETL
    extra = 0
    fields = (
        'comp_type', 'comp_number', 'address', 'city', 'state', 
        'sale_price', 'sale_date', 'living_area', 'bedrooms', 'bathrooms'
    )
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True


class RepairItemInline(admin.TabularInline):
    """Inline admin for repair items within a valuation."""
    
    model = RepairItem
    extra = 0
    fields = ('repair_type', 'category', 'severity', 'description', 'estimated_cost', 'is_required', 'priority')
    show_change_link = True


class ValuationPhotoInline(admin.TabularInline):
    """Inline admin for photos within a valuation."""
    
    model = ValuationPhoto
    extra = 0
    fields = ('photo_type', 'image', 'caption', 'display_order', 'taken_at')
    readonly_fields = ('image',)
    show_change_link = True


class ExtractionFieldResultInline(admin.TabularInline):
    """Inline admin for extraction field results within a document."""
    
    model = ExtractionFieldResult
    extra = 0
    fields = ('target_model', 'target_field', 'value_text', 'confidence', 'extraction_method', 'requires_review')
    readonly_fields = ('created_at',)
    show_change_link = True


class ExtractionLogEntryInline(admin.TabularInline):
    """Inline admin for extraction log entries within a document."""
    
    model = ExtractionLogEntry
    extra = 0
    fields = ('level', 'message', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False


# =============================================================================
# MAIN MODEL ADMIN CLASSES
# =============================================================================


@admin.register(ValuationETL)
class ValuationETLAdmin(admin.ModelAdmin):
    """Admin interface for ValuationETL staging records."""
    
    # List view configuration
    list_display = (
        'id',
        'property_address',
        'city',
        'state',
        'valuation_type',
        'source',
        'inspection_date',
        'as_is_value',
        'as_repaired_value',
        'created_at',
    )
    
    list_filter = (
        'valuation_type',
        'bpo_type',
        'source',
        'state',
        'occupancy_status',
        'condition',
        'inspection_date',
        'created_at',
    )
    
    search_fields = (
        'property_address',
        'city',
        'zip_code',
        'loan_number',
        'deal_name',
        'parcel_number',
        'owner_name',
    )
    
    # Detail view configuration
    readonly_fields = ('created_at', 'updated_at', 'price_per_sqft')
    
    fieldsets = (
        ('Core Information', {
            'fields': (
                'asset_hub',
                'source',
                'valuation_type',
                'bpo_type',
            )
        }),
        ('Property Identification', {
            'fields': (
                'property_address',
                'city',
                'state',
                'zip_code',
                'parcel_number',
            )
        }),
        ('Order Information', {
            'fields': (
                'loan_number',
                'deal_name',
                'owner_name',
            )
        }),
        ('Dates', {
            'fields': (
                'inspection_date',
                'effective_date',
                'report_date',
            )
        }),
        ('Property Status', {
            'fields': (
                'occupancy_status',
                'property_appears_secure',
            )
        }),
        ('Financials', {
            'fields': (
                'yearly_taxes',
                'estimated_monthly_rent',
                'estimated_monthly_rent_repaired',
            )
        }),
        ('Sale/Listing History', {
            'fields': (
                'sold_in_last_12_months',
                'prior_sale_price',
                'prior_sale_date',
                'currently_listed',
                'listing_broker',
                'listing_broker_contact',
                'listing_agent_email',
                'listing_agent_firm',
                'initial_list_price',
                'initial_list_date',
                'current_list_price',
                'days_on_market',
                'cumulative_days_on_market',
                'listing_currently_pending',
                'pending_contract_date',
            )
        }),
        ('Property Characteristics', {
            'fields': (
                'living_area',
                'total_rooms',
                'bedrooms',
                'bathrooms',
                'full_bathrooms',
                'half_bathrooms',
                'year_built',
                'effective_age',
                'foundation_type',
                'basement_square_feet',
                'basement_percent_finished',
                'basement_rooms',
                'lot_size_acres',
                'lot_size_square_feet',
                'property_type',
                'style',
                'quality_rating',
                'number_of_units',
                'condition',
            )
        }),
        ('Features', {
            'fields': (
                'has_pool',
                'has_spa',
                'pool_type',
                'view',
                'has_porch',
                'has_patio',
                'has_deck',
                'patio_deck_description',
                'has_fireplace',
                'number_of_fireplaces',
                'has_fencing',
                'fencing_type',
                'garage',
                'garage_spaces',
                'parking_spaces',
                'parking_type',
                'cooling_type',
                'heating_type',
                'water_type',
                'sewer_type',
                'other_features',
                'hoa_fees_monthly',
                'hoa_fees_annual',
                'hoa_name',
                'hoa_phone',
                'subdivision',
                'school_district',
                'proximity_to_amenities',
            ),
            'classes': ('collapse',),
        }),
        ('Data Source', {
            'fields': (
                'data_source',
                'data_source_id',
            )
        }),
        ('Valuation Estimates', {
            'fields': (
                'as_is_value',
                'as_repaired_value',
                'quick_sale_value',
                'quick_sale_value_repaired',
                'land_value',
                'estimated_marketing_time',
                'typical_marketing_time_days',
                'recommended_sales_strategy',
                'recommended_list_price',
                'recommended_list_price_repaired',
                'price_per_sqft',
            )
        }),
        ('Appraisal Details', {
            'fields': (
                'appraisal_purpose',
                'property_rights_appraised',
                'sales_comparison_approach',
                'cost_approach',
                'income_approach',
            ),
            'classes': ('collapse',),
        }),
        ('Market Data', {
            'fields': (
                'financeable',
                'location_type',
                'location_view',
                'market_trend',
                'neighborhood_trend',
                'economic_trend',
                'property_values_trend',
                'subject_appeal_compared_to_avg',
                'subject_value_compared_to_avg',
                'housing_supply',
                'crime_vandalism_risk',
                'reo_driven_market',
                'num_reo_ss_listings',
                'num_listings_in_area',
                'num_boarded_properties',
                'avg_neighborhood_age',
                'neighborhood_pride_of_ownership',
                'predominant_ownership',
                'percentage_owner_occupancy',
                'new_construction_in_area',
                'seasonal_market',
                'neighborhood_price_range_low',
                'neighborhood_price_range_high',
                'neighborhood_median_price',
                'neighborhood_predominate_value',
                'neighborhood_average_sales_price',
            ),
            'classes': ('collapse',),
        }),
        ('Marketability', {
            'fields': (
                'most_likely_buyer_type',
                'financing_issues',
                'marketability_concerns',
            ),
            'classes': ('collapse',),
        }),
        ('Comments', {
            'fields': (
                'property_comments',
                'neighborhood_comments',
                'general_comments',
            ),
            'classes': ('collapse',),
        }),
        ('Repairs Summary', {
            'fields': (
                'estimated_repair_cost',
                'repairs_to_bring_to_market',
                'deferred_maintenance_cost',
                'general_repair_comments',
            )
        }),
        ('Professional Information', {
            'fields': (
                'agent_name',
                'agent_license',
                'agent_company',
                'agent_email',
                'agent_phone',
                'agent_tax_id',
                'agent_signature',
                'appraiser_name',
                'appraiser_license',
                'appraiser_company',
                'appraiser_signature',
                'reviewer_name',
                'reviewer_license',
                'partner_comments',
                'vendor_comments',
                'internal_notes',
            ),
            'classes': ('collapse',),
        }),
        ('File Attachments', {
            'fields': (
                'original_document',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
                'created_by',
            )
        }),
    )
    
    # Inline models
    inlines = [ComparablesETLInline, RepairItemInline, ValuationPhotoInline]
    
    # Pagination
    list_per_page = 50
    
    # Date hierarchy for easy filtering
    date_hierarchy = 'inspection_date'


@admin.register(ComparablesETL)
class ComparablesETLAdmin(admin.ModelAdmin):
    """Admin interface for ComparablesETL records."""
    
    # List view configuration
    list_display = (
        'id',
        'valuation',
        'comp_type',
        'comp_number',
        'address',
        'city',
        'state',
        'sale_price',
        'sale_date',
        'living_area',
        'bedrooms',
        'bathrooms',
    )
    
    list_filter = (
        'comp_type',
        'sales_type',
        'financing_type',
        'state',
        'property_type',
        'condition',
        'sale_date',
    )
    
    search_fields = (
        'address',
        'city',
        'zip_code',
        'subdivision',
        'valuation__property_address',
        'valuation__loan_number',
    )
    
    # Detail view configuration
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Relationship', {
            'fields': (
                'valuation',
                'comp_type',
                'comp_number',
                'agent_comp_ranking',
            )
        }),
        ('Location', {
            'fields': (
                'address',
                'city',
                'state',
                'zip_code',
                'proximity_miles',
                'proximity_direction',
                'proximity_to_subject',
                'calculated_distance_miles',
            )
        }),
        ('Pricing', {
            'fields': (
                'sale_price',
                'sale_date',
                'price_per_sqft',
                'original_list_price',
                'original_list_date',
                'current_list_price',
                'list_price_at_sale',
                'active_days_on_market',
                'total_days_on_market',
                'days_on_market',
                'cumulative_days_on_market',
            )
        }),
        ('Transaction Details', {
            'fields': (
                'sales_type',
                'seller_concessions',
                'financing_type',
            )
        }),
        ('Property Characteristics', {
            'fields': (
                'living_area',
                'total_rooms',
                'bedrooms',
                'bathrooms',
                'full_bathrooms',
                'half_bathrooms',
                'year_built',
                'effective_age',
                'foundation_type',
                'basement_square_feet',
                'basement_percent_finished',
                'basement_rooms',
                'lot_size_acres',
                'lot_size_square_feet',
                'property_type',
                'style',
                'quality_rating',
                'number_of_units',
                'condition',
            ),
            'classes': ('collapse',),
        }),
        ('Features', {
            'fields': (
                'has_pool',
                'has_spa',
                'pool_type',
                'view',
                'has_porch',
                'has_patio',
                'has_deck',
                'has_fireplace',
                'number_of_fireplaces',
                'has_fencing',
                'fencing_type',
                'garage',
                'garage_spaces',
                'parking_spaces',
                'parking_type',
                'cooling_type',
                'heating_type',
                'water_type',
                'sewer_type',
                'other_features',
                'hoa_fees_monthly',
                'hoa_name',
                'hoa_phone',
                'subdivision',
                'school_district',
                'proximity_to_amenities',
            ),
            'classes': ('collapse',),
        }),
        ('Data Source', {
            'fields': (
                'data_source',
                'data_source_id',
            )
        }),
        ('Adjustments', {
            'fields': (
                'agent_adjustments',
                'adjustment_location',
                'adjustment_site_view',
                'adjustment_design_appeal',
                'adjustment_quality',
                'adjustment_age',
                'adjustment_condition',
                'adjustment_above_grade_rooms',
                'adjustment_gross_living_area',
                'adjustment_basement',
                'adjustment_functional_utility',
                'adjustment_heating_cooling',
                'adjustment_garage_carport',
                'adjustment_porch_patio_deck',
                'adjustment_other',
                'total_adjustments',
                'adjusted_sale_price',
            ),
            'classes': ('collapse',),
        }),
        ('Comments', {
            'fields': (
                'general_comments',
                'adjustments_description',
            ),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )
    
    # Pagination
    list_per_page = 50
    
    # Date hierarchy
    date_hierarchy = 'sale_date'


@admin.register(RepairItem)
class RepairItemAdmin(admin.ModelAdmin):
    """Admin interface for RepairItem records."""
    
    # List view configuration
    list_display = (
        'id',
        'valuation',
        'repair_type',
        'category',
        'severity',
        'estimated_cost',
        'is_required',
        'priority',
    )
    
    list_filter = (
        'repair_type',
        'category',
        'severity',
        'is_required',
        'priority',
    )
    
    search_fields = (
        'description',
        'valuation__property_address',
        'valuation__loan_number',
    )
    
    # Detail view configuration
    fieldsets = (
        ('Relationship', {
            'fields': (
                'valuation',
            )
        }),
        ('Repair Details', {
            'fields': (
                'repair_type',
                'category',
                'severity',
                'repair_number',
                'description',
                'estimated_cost',
                'is_required',
                'priority',
            )
        }),
    )
    
    # Pagination
    list_per_page = 100


@admin.register(ValuationDocument)
class ValuationDocumentAdmin(admin.ModelAdmin):
    """Admin interface for ValuationDocument extraction metadata."""
    
    # List view configuration
    list_display = (
        'id',
        'file_name',
        'status',
        'uploaded_at',
        'processed_at',
        'created_by',
        'file_size_display',
    )
    
    list_filter = (
        'status',
        'file_mime_type',
        'uploaded_at',
        'processed_at',
    )
    
    search_fields = (
        'file_name',
        'file_path',
        'status_message',
    )
    
    # Detail view configuration
    readonly_fields = ('uploaded_at', 'processed_at', 'file_size_display')
    
    fieldsets = (
        ('File Information', {
            'fields': (
                'file_name',
                'file_path',
                'file_mime_type',
                'file_size_bytes',
                'file_size_display',
            )
        }),
        ('Processing Status', {
            'fields': (
                'status',
                'status_message',
                'uploaded_at',
                'processed_at',
            )
        }),
        ('User Information', {
            'fields': (
                'created_by',
            )
        }),
    )
    
    # Inline models
    inlines = [ExtractionFieldResultInline, ExtractionLogEntryInline]
    
    # Pagination
    list_per_page = 50
    
    # Date hierarchy
    date_hierarchy = 'uploaded_at'
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        if obj.file_size_bytes:
            size = obj.file_size_bytes
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.2f} {unit}"
                size /= 1024.0
            return f"{size:.2f} TB"
        return "N/A"
    
    file_size_display.short_description = "File Size"


@admin.register(ExtractionFieldResult)
class ExtractionFieldResultAdmin(admin.ModelAdmin):
    """Admin interface for ExtractionFieldResult records."""
    
    # List view configuration
    list_display = (
        'id',
        'document',
        'target_model',
        'target_field',
        'confidence',
        'extraction_method',
        'requires_review',
        'created_at',
    )
    
    list_filter = (
        'extraction_method',
        'requires_review',
        'target_model',
        'created_at',
    )
    
    search_fields = (
        'target_model',
        'target_field',
        'value_text',
        'document__file_name',
    )
    
    # Detail view configuration
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Relationship', {
            'fields': (
                'document',
            )
        }),
        ('Target Information', {
            'fields': (
                'target_model',
                'target_field',
            )
        }),
        ('Extracted Value', {
            'fields': (
                'value_text',
                'value_json',
            )
        }),
        ('Extraction Metadata', {
            'fields': (
                'confidence',
                'extraction_method',
                'requires_review',
                'created_at',
            )
        }),
    )
    
    # Pagination
    list_per_page = 100


@admin.register(ExtractionLogEntry)
class ExtractionLogEntryAdmin(admin.ModelAdmin):
    """Admin interface for ExtractionLogEntry records."""
    
    # List view configuration
    list_display = (
        'id',
        'document',
        'level',
        'message_preview',
        'created_at',
    )
    
    list_filter = (
        'level',
        'created_at',
    )
    
    search_fields = (
        'message',
        'document__file_name',
    )
    
    # Detail view configuration
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Relationship', {
            'fields': (
                'document',
            )
        }),
        ('Log Entry', {
            'fields': (
                'level',
                'message',
                'created_at',
            )
        }),
    )
    
    # Pagination
    list_per_page = 100
    
    # Date hierarchy
    date_hierarchy = 'created_at'
    
    def message_preview(self, obj):
        """Display truncated message preview in list view."""
        if len(obj.message) > 100:
            return f"{obj.message[:100]}..."
        return obj.message
    
    message_preview.short_description = "Message"


@admin.register(ValuationPhoto)
class ValuationPhotoAdmin(admin.ModelAdmin):
    """Admin interface for ValuationPhoto records."""
    
    # List view configuration
    list_display = (
        'id',
        'valuation',
        'photo_type',
        'caption',
        'display_order',
        'taken_at',
        'thumbnail_preview',
    )
    
    list_filter = (
        'photo_type',
        'taken_at',
    )
    
    search_fields = (
        'caption',
        'valuation__property_address',
        'valuation__loan_number',
    )
    
    # Detail view configuration
    readonly_fields = ('image_preview',)
    
    fieldsets = (
        ('Relationship', {
            'fields': (
                'valuation',
                'comparable',
                'repair_item',
            )
        }),
        ('Photo Details', {
            'fields': (
                'photo_type',
                'image',
                'image_preview',
                'caption',
                'taken_at',
                'display_order',
            )
        }),
    )
    
    # Pagination
    list_per_page = 50
    
    def thumbnail_preview(self, obj):
        """Display thumbnail in list view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    
    thumbnail_preview.short_description = "Preview"
    
    def image_preview(self, obj):
        """Display larger image in detail view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 600px; max-height: 600px;" />',
                obj.image.url
            )
        return "No image"
    
    image_preview.short_description = "Image Preview"
