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

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_assetidhub'
        verbose_name = 'Asset ID Hub'
        verbose_name_plural = 'Asset ID Hub'
        indexes = [
            models.Index(fields=['sellertape_id']),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        label = self.sellertape_id or 'hub'
        return f"AssetIdHub({self.pk}:{label})"
