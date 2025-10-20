from django.db import models

class AssetIdHub(models.Model):
    """Central hub that provides a stable, human-friendly integer ID for an asset.

    This ID is used across acquisitions (SellerRawData), asset management (SellerBoardedData),
    valuations, photos, and other domain models as the canonical join key.

    Snapshots store useful source identifiers for traceability and backfill logic.
    """

    class AssetStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'  # WHAT: Flag assets currently in portfolio workflows (default state)
        LIQUIDATED = 'LIQUIDATED', 'Liquidated'  # WHAT: Represents assets sold/resolved and no longer actively managed

    # Optional source snapshot for backfill/traceability (indexed)
    # - sellertape_id -> acq_module.models.seller.SellerRawData.sellertape_id (external tape key)
    #   Kept to assist ETL joins and admin lookups. Authoritative relations live on spoke tables via 1:1/1:n FKs.
    sellertape_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)  # This is the id that comes with seller tape so that we can cross ref internal vs external IDs
    
    # Servicer reference for cross-app joins and admin lookups
    servicer_id = models.CharField(max_length=64, null=True, blank=True, db_index=True, help_text='External servicer ID for cross-referencing servicer loan data')

    # Simple yes/no commercial tag for UI toggles
    is_commercial = models.BooleanField(
        null=True,
        blank=True,
        help_text="Simple tag: True for commercial assets, False for residential. If blank, inferred at save time."
    )

    asset_status = models.CharField(
        max_length=32,  # WHAT: Provides headroom for future lifecycle labels beyond the current Active/Liquidated pair
        choices=AssetStatus.choices,  # WHAT: Restricts persisted values to the canonical AssetStatus enumeration
        default=AssetStatus.ACTIVE,  # WHY: Maintain backward compatibility by treating existing hubs as Active unless explicitly updated
        db_index=True,  # WHY: Enable fast filtering/grouping by lifecycle status across dashboards and reports
        help_text='Canonical lifecycle status for this asset hub (drives UI dropdown and module coordination).',  # WHAT: Document downstream usage for administrators
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_assetidhub'
        verbose_name = 'Asset ID Hub'
        verbose_name_plural = 'Asset ID Hub'
        indexes = [
            models.Index(fields=['sellertape_id']),
            models.Index(fields=['servicer_id']),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        label = self.sellertape_id or 'hub'
        return f"AssetIdHub({self.pk}:{label})"

    @property
    def is_commercial_flag(self) -> bool:
        """Convenience boolean for UI logic.

        Returns the explicit boolean when set; otherwise falls back to inference.
        """
        # Prefer explicit boolean tag
        if self.is_commercial is not None:
            return bool(self.is_commercial)
        # Fall back to inference
        return self._infer_is_commercial()

    def save(self, *args, **kwargs):
        """Override save to auto-infer category when not explicitly set.

        What: Ensures hub has a reasonable default category based on loaded data.
        Why: Frontend can rely on a single source of truth without duplicating inference.
        How: Checks SellerRawData first; if absent/unspecified, falls back to data presence.
        """
        if self.is_commercial is None:
            # Only set boolean if not explicitly provided; follow requested order
            self.is_commercial = self._infer_is_commercial()
        super().save(*args, **kwargs)

    def _infer_is_commercial(self) -> bool:
        """Infer a simple boolean commercial flag.

        Order requested:
        1) Use standardized SRD tags first (Multifamily 5+, Industrial, Mixed Use OR product_type=Commercial)
        2) If none: any ComparableProperty with units >= 5
        3) If none: presence of UnitMix or RentRoll for this hub
        """
        from django.apps import apps

        # 1) SRD standardized tags
        try:
            srd = getattr(self, 'acq_raw', None)
            SellerRawData = apps.get_model('acq_module', 'SellerRawData')
        except Exception:
            srd = None
            SellerRawData = None
        if srd is not None:
            pt = getattr(srd, 'property_type', None)
            prod = getattr(srd, 'product_type', None)
            commercial_pts = {
                getattr(SellerRawData.PropertyType, 'MULTIFAMILY', 'Multifamily 5+'),
                getattr(SellerRawData.PropertyType, 'INDUSTRIAL', 'Industrial'),
                getattr(SellerRawData.PropertyType, 'MIXED_USE', 'Mixed Use'),
            } if SellerRawData else {'Multifamily 5+', 'Industrial', 'Mixed Use'}
            if pt in commercial_pts or prod == (getattr(SellerRawData.ProductType, 'COMMERCIAL', 'Commercial') if SellerRawData else 'Commercial'):
                return True

        # 2) Unit counts from ComparableProperty (comps) >=5
        try:
            ComparableProperty = apps.get_model('core', 'ComparableProperty')
            if ComparableProperty.objects.filter(asset_hub=self, units__gte=5).exists():
                return True
        except Exception:
            pass

        # 3) Presence of UnitMix or RentRoll
        try:
            UnitMix = apps.get_model('core', 'UnitMix')
            if UnitMix.objects.filter(asset_hub_id=self).exists():
                return True
        except Exception:
            pass
        try:
            RentRoll = apps.get_model('core', 'RentRoll')
            if RentRoll.objects.filter(asset_hub_id=self).exists():
                return True
        except Exception:
            pass

        return False
