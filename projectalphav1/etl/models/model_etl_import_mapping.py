"""
Import Mapping Model

WHAT: Stores column mappings for data imports to enable review and reuse
WHY: Users need to review, edit, and reuse successful column mappings
HOW: Stores JSON mapping configurations linked to sellers/trades

USAGE:
    # Create mapping after successful import
    mapping = ImportMapping.objects.create(
        seller=seller,
        trade=trade,
        mapping_name="ABC Seller - Standard Format",
        column_mapping={"Loan Number": "sellertape_id", ...}
    )
    
    # Retrieve mapping for reuse
    mapping = ImportMapping.objects.filter(seller=seller).first()
    column_mapping = mapping.column_mapping

Docs reviewed:
- Django JSONField: https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield
- Django model best practices: https://docs.djangoproject.com/en/stable/topics/db/models/
"""

from django.db import models
from django.utils import timezone
from acq_module.models.model_acq_seller import Seller, Trade


class ImportMapping(models.Model):
    """
    WHAT: Stores column mapping configurations for data imports
    WHY: Enable users to review, edit, and reuse successful mappings
    HOW: JSON field stores source-to-target column mappings
    """
    
    # WHAT: Link mapping to seller for organization and filtering
    # WHY: Different sellers typically have different file formats
    # HOW: Nullable FK so mapping can exist even if seller is deleted
    seller = models.ForeignKey(
        Seller,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='import_mappings',
        help_text='Seller this mapping is associated with'
    )
    
    # WHAT: Link mapping to specific trade for context
    # WHY: Track which trade this mapping was used for
    # HOW: Nullable FK so mapping persists if trade is deleted
    trade = models.ForeignKey(
        Trade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='import_mappings',
        help_text='Trade this mapping was created from (optional)'
    )
    
    # WHAT: Human-readable name for the mapping configuration
    # WHY: Users need to identify and select mappings easily
    # HOW: Auto-generated or user-provided descriptive name
    mapping_name = models.CharField(
        max_length=255,
        help_text='Descriptive name for this mapping (e.g., "ABC Seller - Standard Format")'
    )
    
    # WHAT: JSON field storing the actual column mappings
    # WHY: Flexible storage for source-to-target field mappings
    # HOW: Dict format: {"Source Column Name": "target_model_field"}
    column_mapping = models.JSONField(
        help_text='JSON mapping of source columns to model fields'
    )
    
    # WHAT: Store source file columns for reference and validation
    # WHY: Users need to see what columns were in the original file
    # HOW: List of column names from the source file
    source_columns = models.JSONField(
        default=list,
        blank=True,
        help_text='List of column names from the source file'
    )
    
    # WHAT: Track how mapping was created (AI vs manual vs exact)
    # WHY: Helps users understand mapping quality and source
    # HOW: Enum field with predefined creation methods
    class MappingMethod(models.TextChoices):
        AI = 'AI', 'AI-Generated'
        MANUAL = 'MANUAL', 'Manual'
        EXACT = 'EXACT', 'Exact Match'
        HYBRID = 'HYBRID', 'AI + Manual Edits'
    
    mapping_method = models.CharField(
        max_length=20,
        choices=MappingMethod.choices,
        default=MappingMethod.AI,
        help_text='How this mapping was created'
    )
    
    # WHAT: Track if mapping is marked as default for this seller
    # WHY: Users can set preferred mapping for automatic reuse
    # HOW: Boolean flag, only one default per seller
    is_default = models.BooleanField(
        default=False,
        help_text='Use this mapping as default for this seller'
    )
    
    # WHAT: Track if mapping is active or archived
    # WHY: Users may want to deprecate old mappings without deleting
    # HOW: Boolean flag for filtering active mappings
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this mapping is active'
    )
    
    # WHAT: Store original file name for reference
    # WHY: Helps users identify which file format this mapping is for
    # HOW: Optional text field
    original_filename = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Original file name this mapping was created from'
    )
    
    # WHAT: Store import statistics for reference
    # WHY: Track success rate and data quality metrics
    # HOW: JSON field with flexible stats structure
    import_stats = models.JSONField(
        default=dict,
        blank=True,
        help_text='Statistics from import (records imported, errors, etc.)'
    )
    
    # WHAT: Notes field for user comments
    # WHY: Users may want to document mapping quirks or special cases
    # HOW: Text field for free-form notes
    notes = models.TextField(
        blank=True,
        help_text='User notes about this mapping'
    )
    
    # WHAT: Track who created the mapping
    # WHY: Audit trail for mapping creation and modifications
    # HOW: Nullable FK to User model
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_mappings',
        help_text='User who created this mapping'
    )
    
    # WHAT: Track who last modified the mapping
    # WHY: Audit trail for mapping edits
    # HOW: Nullable FK to User model
    modified_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='modified_mappings',
        help_text='User who last modified this mapping'
    )
    
    # WHAT: Automatic timestamp tracking
    # WHY: Track when mappings are created and updated
    # HOW: Django auto_now_add and auto_now
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # WHAT: Track last time mapping was used
    # WHY: Identify frequently used vs stale mappings
    # HOW: Manual update when mapping is applied
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time this mapping was used for an import'
    )
    
    # WHAT: Count how many times mapping has been used
    # WHY: Identify popular/reliable mappings
    # HOW: Increment counter on each use
    usage_count = models.IntegerField(
        default=0,
        help_text='Number of times this mapping has been used'
    )
    
    class Meta:
        verbose_name = "Import Mapping"
        verbose_name_plural = "Import Mappings"
        ordering = ['-created_at']
        indexes = [
            # WHAT: Index for filtering by seller
            # WHY: Common query pattern - get all mappings for a seller
            models.Index(fields=['seller']),
            # WHAT: Index for filtering by trade
            # WHY: Track mappings used for specific trades
            models.Index(fields=['trade']),
            # WHAT: Index for finding default mappings
            # WHY: Quick lookup of default mapping for a seller
            models.Index(fields=['seller', 'is_default', 'is_active']),
            # WHAT: Index for active mappings
            # WHY: Filter out archived mappings efficiently
            models.Index(fields=['is_active']),
        ]
        constraints = [
            # WHAT: Ensure only one default mapping per seller
            # WHY: Prevent ambiguity in automatic mapping selection
            # HOW: Unique constraint on seller + is_default when both are set
            models.UniqueConstraint(
                fields=['seller', 'is_default'],
                condition=models.Q(is_default=True),
                name='unique_default_per_seller'
            ),
        ]
    
    def __str__(self):
        """Return human-readable representation of mapping"""
        seller_name = self.seller.name if self.seller else "No Seller"
        return f"{self.mapping_name} ({seller_name})"
    
    def save(self, *args, **kwargs):
        """
        WHAT: Override save to handle default mapping logic
        WHY: Ensure only one default mapping per seller
        HOW: Clear other defaults when this is set as default
        """
        # WHAT: If this mapping is being set as default, clear other defaults
        # WHY: Only one default mapping per seller
        # HOW: Update other mappings for same seller
        if self.is_default and self.seller:
            ImportMapping.objects.filter(
                seller=self.seller,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def mark_as_used(self):
        """
        WHAT: Update usage statistics when mapping is used
        WHY: Track mapping popularity and recency
        HOW: Increment counter and update timestamp
        """
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])
    
    def get_mapped_fields(self):
        """
        WHAT: Get list of target fields that are mapped
        WHY: Useful for validation and UI display
        HOW: Extract values from column_mapping dict
        
        Returns:
            List of target field names
        """
        return list(self.column_mapping.values())
    
    def get_unmapped_columns(self):
        """
        WHAT: Get list of source columns that aren't mapped
        WHY: Identify potential data loss or missing mappings
        HOW: Compare source_columns to column_mapping keys
        
        Returns:
            List of unmapped source column names
        """
        mapped_sources = set(self.column_mapping.keys())
        all_sources = set(self.source_columns)
        return list(all_sources - mapped_sources)
    
    def validate_mapping(self):
        """
        WHAT: Validate that mapped fields exist in ETL registry
        WHY: Prevent errors from invalid field names
        HOW: Check each target field against model fields
        
        Returns:
            Dict with validation results: {valid: bool, errors: list}
        """
        from etl.services.services_sellerTapeImport.etl_field_registry import get_import_field_specs
        
        # WHAT: Get valid field names from registry
        # WHY: Need reference list for validation
        # HOW: Use registry spec keys
        valid_fields = set(get_import_field_specs().keys())
        
        errors = []
        # WHAT: Check each mapped field
        # WHY: Identify invalid field names
        # HOW: Compare against valid_fields set
        for source_col, target_field in self.column_mapping.items():
            if target_field not in valid_fields:
                errors.append(f"Invalid field: {target_field} (from {source_col})")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'mapped_count': len(self.column_mapping),
            'valid_fields_count': len(valid_fields)
        }
