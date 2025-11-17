from __future__ import annotations

from django.db import models


class LlDataEnrichment(models.Model):
    """
    Loan-level Data Enrichment

    Stores supplemental/derived analysis for a single `SellerRawData` record.
    This model is intentionally flexible so we can attach various enrichment
    artifacts without altering the core raw data schema.
    """


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
    geocode_msa = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Human-friendly MSA name returned by Geocodio census append.",
    )
    geocode_msa_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="MSA/CBSA code returned by Geocodio census append.",
    )
    
    # Additional Geocodio census fields
    geocode_state_fips = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        help_text="State FIPS code from Geocodio census data.",
    )
    geocode_county_fips = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        help_text="County FIPS code from Geocodio census data.",
    )
    geocode_tract_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Census tract code from Geocodio census data.",
    )
    geocode_full_fips = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="Full FIPS code from Geocodio census data.",
    )
    geocode_msa_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="MSA type (metropolitan/micropolitan) from Geocodio census data.",
    )
    geocode_csa_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Combined Statistical Area name from Geocodio census data.",
    )
    geocode_csa_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Combined Statistical Area code from Geocodio census data.",
    )
    geocode_county_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="County name from Geocodio census data.",
    )
    geocode_school_district = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="School district name from Geocodio school field.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Loan Level Data Enrichment"
        verbose_name_plural = "Loan Level Data Enrichments"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['geocode_lat', 'geocode_lng']),
        ]
        db_table = 'acq_ll_data_enrichment'

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Enrichment for {self.asset_hub_id}"
