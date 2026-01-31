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
    sellertape_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    # Servicer reference for cross-app joins and admin lookups
    servicer_id = models.CharField(max_length=64, null=True, blank=True, db_index=True, help_text='External servicer ID for cross-referencing servicer loan data')

    # Audit
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

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
        servicer = self.servicer_id or 'servicer?'
        return f"AssetIdHub({self.pk}:{label}|Servicer:{servicer})"

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

    class AssetClass(models.TextChoices):
        NPL = 'NPL', 'NPL'
        REO = 'REO', 'REO'
        PERFORMING = 'PERFORMING', 'Performing'

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

    asset_class = models.CharField(
        max_length=32,
        choices=AssetClass.choices,
        null=True,
        blank=True,
        db_index=True,
        help_text='High-level asset classification (NPL, REO, Performing).'
    )

    legacy_flag = models.BooleanField(
        null=True,  # WHAT: Allow NULL values in the database
        blank=True,  # WHAT: Allow blank values in forms/admin
        db_index=True,  # WHY: Enable fast filtering/grouping by legacy status across dashboards and reports
        help_text='Flag indicating if this asset is a legacy asset',  # WHAT: Document the purpose of this flag
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "asset_details"
        verbose_name = "Asset Detail"
        verbose_name_plural = "Asset Details"

    def __str__(self):
        # WHAT: Safely get fund_legal_entity label, handling deletion edge cases
        # WHY: During FundLegalEntity deletion, accessing the relationship can cause errors
        # HOW: Use try/except to safely get the string representation
        try:
            label = str(self.fund_legal_entity) if self.fund_legal_entity else "Unassigned"
        except Exception:
            # WHAT: Fallback if fund_legal_entity is being deleted or inaccessible
            label = "Unassigned"
        return f"{label} → Asset {self.pk}"

    def save(self, *args, **kwargs):
        """Override save to skip auto-inference of commercial flag.
        
        What: Saves the record without automatically inferring is_commercial.
        Why: Allow manual control over commercial flag without automatic validation.
        How: Skips inference - is_commercial can be set manually or left as None.
        """
        # WHAT: Skip auto-inference of is_commercial
        # WHY: Allow manual control without automatic validation
        # NOTE: Removed auto-inference logic - set is_commercial manually if needed
        if not self.asset_class:
            acq_asset = getattr(self.asset, 'acq_asset', None)
            raw_status = getattr(acq_asset, 'asset_status', None)
            if raw_status == 'NPL':
                self.asset_class = self.AssetClass.NPL
            elif raw_status == 'REO':
                self.asset_class = self.AssetClass.REO
            elif raw_status in {'PERF', 'RPL'}:
                self.asset_class = self.AssetClass.PERFORMING
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
            AcqAsset = apps.get_model('acq_module', 'AcqAsset')
        except Exception:
            AcqAsset = None
        acq_asset = getattr(hub, 'acq_asset', None) if hub is not None else None
        if acq_asset is not None:
            pt = None
            prod = None
            if getattr(acq_asset, 'property', None):
                pt = getattr(acq_asset.property, 'property_type_merged', None)
            if getattr(acq_asset, 'loan', None):
                prod = getattr(acq_asset.loan, 'product_type', None)
            # WHAT: Define commercial property types as string values (subclass codes)
            # WHY: Subclass is the single property type source of truth
            # HOW: Compare against stored subclass values
            commercial_pts = {
                'Industrial',
                'Mixed Use',
                'Storage',
                'Healthcare',
                'Office',
                'Retail',
                'Hospitality',
            }
            # WHAT: Treat multifamily and commercial asset classes as commercial
            # WHY: Multifamily 5+ and Commercial are handled as commercial assets
            # HOW: Check asset_class or property_type/subclass + product type
            if acq_asset.asset_class in {
                getattr(AcqAsset.AssetClass, 'MULTIFAMILY_5_PLUS', None),
                getattr(AcqAsset.AssetClass, 'COMMERCIAL', None),
            }:
                return True
            if pt in commercial_pts or prod == 'Commercial':
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

