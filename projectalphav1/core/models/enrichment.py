from __future__ import annotations

from django.db import models


class LlDataEnrichment(models.Model):
    """
    Loan-level Data Enrichment

    Stores supplemental/derived analysis for a single `SellerRawData` record.
    This model is intentionally flexible so we can attach various enrichment
    artifacts without altering the core raw data schema.
    """

    # One-to-one link to the core loan row (string ref to avoid cross-app import)
    seller_raw_data = models.OneToOneField(
        'acq_module.SellerRawData',
        on_delete=models.CASCADE,
        related_name='enrichment',
    )
    # Stable hub link (optional for backfill; will be promoted to PK later if desired)
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrichment',
        help_text='1:1 hub link for this enrichment (mirror of seller_raw_data.asset_hub).',
    )

    # Geocoding persistence (store once, reuse many times)
    geocode_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geocode_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    geocode_used_address = models.CharField(max_length=255, null=True, blank=True)
    geocode_full_address = models.CharField(max_length=255, null=True, blank=True)
    geocode_display_address = models.CharField(max_length=255, null=True, blank=True)
    geocoded_at = models.DateTimeField(null=True, blank=True)
    geocode_county = models.CharField(max_length=255, null=True, blank=True)
    geocode_msa = models.CharField(max_length=255, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Loan Level Data Enrichment"
        verbose_name_plural = "Loan Level Data Enrichments"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller_raw_data']),
            models.Index(fields=['geocode_lat', 'geocode_lng']),
        ]
        db_table = 'acq_ll_data_enrichment'

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Enrichment for {self.seller_raw_data_id}"
