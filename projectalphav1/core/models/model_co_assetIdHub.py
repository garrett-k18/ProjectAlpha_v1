from django.db import models

class AssetIdHub(models.Model):
    """Central hub that provides a stable, human-friendly integer ID for an asset.

    This ID is used across acquisitions (SellerRawData), asset management (SellerBoardedData),
    valuations, photos, and other domain models as the canonical join key.

    Snapshots store useful source identifiers for traceability and backfill logic.
    """

    # Optional source snapshot for backfill/traceability (indexed)
    # - sellertape_id -> acq_module.models.seller.SellerRawData.sellertape_id (external tape key)
    #   Kept to assist ETL joins and admin lookups. Authoritative relations live on spoke tables via 1:1/1:n FKs.
    sellertape_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)  # This is the id that comes with seller tape so that we can cross ref internal vs external IDs
    
    # Servicer reference for cross-app joins and admin lookups
    servicer_id = models.CharField(max_length=64, null=True, blank=True, db_index=True, help_text='External servicer ID for cross-referencing servicer loan data')

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
        details = getattr(self, 'details', None)
        if details is None:
            return False
        # Prefer explicit boolean tag stored on AssetDetails
        if details.is_commercial is not None:
            return bool(details.is_commercial)
        # Fall back to inference on AssetDetails
        return details._infer_is_commercial()


class AssetDetails(models.Model):
    """Minimal asset details linking AssetIdHub to a fund/legal entity."""

    class AssetStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'  # WHAT: Flag assets currently in portfolio workflows (default state)
        LIQUIDATED = 'LIQUIDATED', 'Liquidated'  # WHAT: Represents assets sold/resolved and no longer actively managed

    asset = models.OneToOneField(
        AssetIdHub,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='details',
        help_text="Asset this detail row belongs to"
    )

    fund_legal_entity = models.ForeignKey(
        'core.FundLegalEntity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_assignments',
        help_text="Fund/Entity associated with this asset"
    )
    trade = models.ForeignKey(
        'acq_module.Trade',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_details',
        help_text="Trade associated with this asset detail"
    )

    servicer_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        help_text="Servicer ID snapshot copied from AssetIdHub.servicer_id for admin/SQL use."
    )

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "asset_details"
        verbose_name = "Asset Detail"
        verbose_name_plural = "Asset Details"

    def __str__(self):
        label = self.fund_legal_entity or "Unassigned"
        return f"{label} → Asset {self.asset_id}"

    def save(self, *args, **kwargs):
        """Override save to auto-infer category when not explicitly set.

        What: Ensures hub has a reasonable default category based on loaded data.
        Why: Frontend can rely on a single source of truth without duplicating inference.
        How: Checks SellerRawData first; if absent/unspecified, falls back to data presence.
        """
        hub = getattr(self, 'asset', None)
        if hub is not None and hub.servicer_id and self.servicer_id != hub.servicer_id:
            self.servicer_id = hub.servicer_id
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

        hub = getattr(self, 'asset', None)

        # 1) SRD standardized tags
        try:
            SellerRawData = apps.get_model('acq_module', 'SellerRawData')
        except Exception:
            SellerRawData = None
        srd = getattr(hub, 'acq_raw', None) if hub is not None else None
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
            if hub is not None and ComparableProperty.objects.filter(asset_hub=hub, units__gte=5).exists():
                return True
        except Exception:
            pass

        # 3) Presence of UnitMix or RentRoll
        try:
            UnitMix = apps.get_model('core', 'UnitMix')
            if hub is not None and UnitMix.objects.filter(asset_hub_id=hub.pk).exists():
                return True
        except Exception:
            pass
        try:
            RentRoll = apps.get_model('core', 'RentRoll')
            if hub is not None and RentRoll.objects.filter(asset_hub_id=hub.pk).exists():
                return True
        except Exception:
            pass

        return False

