from __future__ import annotations

from django.db import models
from django.conf import settings

class InternalValuation(models.Model):
    """[DEPRECATED] Use `Valuation` instead.

    Model to store internal and third-party valuations linked 1:1 to the AssetIdHub.

    Moved from acq_module.models.valuations to core.models.valuations to align with
    hub-first ownership. db_table is preserved for continuity.
    """
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='internal_valuations',
        help_text='Link to hub; many valuations over asset life are supported.',
    )

    # Internal underwriting values and Rehab estimates
    internal_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    internal_arv_value = models.DecimalField(max_digits=15, decimal_places=2)
    internal_value_date = models.DateField()
    internal_rehab_est_total = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    roof_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    kitchen_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    bath_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    flooring_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    windows_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    appliances_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    plumbing_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    electrical_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    landscaping_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Third-party values
    thirdparty_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    thirdparty_arv_value = models.DecimalField(max_digits=15, decimal_places=2)
    thirdparty_value_date = models.DateField()

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # User tracking (who created/last updated this valuation)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_internal_valuations',
        help_text='User who created this valuation record.'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_internal_valuations',
        help_text='User who last updated this valuation record.'
    )

    class Meta:
        verbose_name = "Internal Valuation"
        verbose_name_plural = "Internal Valuations"
        ordering = ['-created_at']
        db_table = 'acq_internal_valuation'

    def __str__(self):
        return f"Internal Valuation for hub {self.asset_hub_id}"


class BrokerValues(models.Model):
    """[DEPRECATED] Use `Valuation` instead.

    Model to store broker valuations linked 1:1 to the AssetIdHub.

    Moved from acq_module.models.valuations to core.models.valuations. db_table preserved.
    """
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='broker_values',
        help_text='TEMP: nullable during staged migration; will be PK in next migration.',
    )

    # Broker values
    broker_asis_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    broker_arv_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    broker_value_date = models.DateField(null=True, blank=True)
    broker_rehab_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    broker_notes = models.TextField(blank=True, null=True)
    broker_links = models.URLField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # User tracking (who created/last updated this broker valuation)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_broker_valuations',
        help_text='User who created this broker valuation record.'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_broker_valuations',
        help_text='User who last updated this broker valuation record.'
    )

    class Meta:
        verbose_name = "Broker Values"
        verbose_name_plural = "Broker Values"
        ordering = ['-created_at']
        db_table = 'acq_broker_values'

    def __str__(self):
        return f"Broker Valuation for hub {self.asset_hub_id}"

class Valuation(models.Model):
    """
    Unified valuation model that combines InternalValuation and BrokerValues.
    
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
    
    # Source tracking
    SOURCE_CHOICES = [
        ('internalInitialUW', 'Internal Initial UW Valuation'),
        ('internal', 'Internal Valuation'),
        ('broker', 'Broker Valuation'),
        ('desktop', 'Desktop Valuation'),
        ('BPOI', 'BPOI'),
        ('BPOE', 'BPOE'),
        ('seller', 'Seller Provided'),
        ('appraisal', 'Professional Appraisal'),
    ]
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
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
    
    # Detailed rehab estimates (from InternalValuation)
    roof_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    kitchen_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    bath_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    flooring_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    windows_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    appliances_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    plumbing_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    electrical_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    landscaping_est = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
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