from __future__ import annotations

from django.db import models

# Local import to link one-to-one with the core loan row
from .seller import SellerRawData


class LlDataEnrichment(models.Model):
    """
    Loan-level Data Enrichment

    Stores supplemental/derived analysis for a single `SellerRawData` record.
    This model is intentionally flexible so we can attach various enrichment
    artifacts without altering the core raw data schema.
    """

    # One-to-one link to the core loan row
    seller_raw_data = models.OneToOneField(
        SellerRawData,
        on_delete=models.CASCADE,
        related_name='enrichment',
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
