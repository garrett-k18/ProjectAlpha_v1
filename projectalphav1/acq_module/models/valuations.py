from django.db import models
from .seller import SellerRawData
import os
from datetime import datetime

"""
Migration compatibility re-exports for legacy upload helpers
- Old migrations import these by path: acq_module.models.valuations.get_*_photo_path
- Implementations reside in acq_module.archive.legacy_upload_paths; we import here so the
  same dotted path remains valid for historical migrations.
Docs: https://docs.djangoproject.com/en/stable/topics/migrations/#serializing-values
"""
from acq_module.archive.legacy_upload_paths import (
    get_broker_photo_path,
    get_public_photo_path,
    get_document_photo_path,
)


# -----------------------------------------------------------------------------------
# Internal and Third-Party Valuations
# -----------------------------------------------------------------------------------
class InternalValuation(models.Model):
    """Model to store internal and third-party valuations linked 1:1 to the AssetIdHub."""
    # Hub is the owner key (strict 1:1). Create hub first, then attach the valuation.
    # Staged migration step 1: temporarily nullable and not primary_key
    # After migration apply, we'll promote this to primary_key=True and null=False
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='internal_valuation',
        help_text='TEMP: nullable during staged migration; will be PK in next migration.',
    )
    
    # Internal underwriting values and Rehab estimates
    internal_uw_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    internal_uw_arv_value = models.DecimalField(max_digits=15, decimal_places=2)
    internal_uw_value_date = models.DateField()
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
    
    class Meta:
        verbose_name = "Internal Valuation"
        verbose_name_plural = "Internal Valuations"
        ordering = ['-created_at']
        db_table = 'acq_internal_valuation'
    
    def __str__(self):
        return f"Internal Valuation for hub {self.asset_hub_id}"


# -----------------------------------------------------------------------------------
# Broker: Valuations & Uploads (all broker-related models and helpers)
# -----------------------------------------------------------------------------------
# Broker Valuations (values captured from brokers)
class BrokerValues(models.Model):
    """Model to store broker valuations linked 1:1 to the AssetIdHub."""
    # Hub is the owner key (strict 1:1). Create hub first, then attach the broker values row.
    # Staged migration step 1: temporarily nullable and not primary_key
    # After migration apply, we'll promote this to primary_key=True and null=False
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
    
    class Meta:
        verbose_name = "Broker Values"
        verbose_name_plural = "Broker Values"
        ordering = ['-created_at']
        db_table = 'acq_broker_values'
    
    def __str__(self):
        return f"Broker Valuation for hub {self.asset_hub_id}"


# -----------------------------------------------------------------------------------
# Unified Photos
# -----------------------------------------------------------------------------------
def get_photo_path(instance, filename):
    """Generate a unified file path for all photos.

    Structure: photos/{seller_id}/{trade_id}/{timestamped_filename}

    We keep a single storage layout since all photos are keyed to SellerRawData.
    """
    seller_id = instance.seller_raw_data.seller.id
    trade_id = instance.seller_raw_data.trade.id

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"

    return os.path.join('photos', str(seller_id), str(trade_id), new_filename)


class Photo(models.Model):
    """Unified photo model for all sources (broker, document, public, internal).

    Photos are stored against SellerRawData. Use `source_tag` to indicate origin.
    """

    # Owning asset
    seller_raw_data = models.ForeignKey(
        SellerRawData,
        on_delete=models.CASCADE,
        related_name='photos',
        help_text='SellerRawData record this photo belongs to.'
    )
    # Stable hub link (optional) and snapshot of source raw PK for durability
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_photos',
        help_text='Stable hub ID for this photo (from seller_raw_data.asset_hub).',
    )
    source_raw_id = models.IntegerField(null=True, blank=True, db_index=True, help_text='Snapshot of SellerRawData.id')

    # The actual image file
    image = models.ImageField(
        upload_to=get_photo_path,
        help_text='Uploaded image file.'
    )

    # Source tagging
    SOURCE_TAG_CHOICES = [
        ('broker', 'Broker'),
        ('document', 'Document'),
        ('public', 'Public'),
        ('internal', 'Internal'),
    ]
    source_tag = models.CharField(
        max_length=20,
        choices=SOURCE_TAG_CHOICES,
        help_text='Origin tag for the photo.'
    )

    # Optional display fields
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    # Optional document-related metadata (nullable; used when source_tag == 'document')
    source_document_name = models.CharField(max_length=255, blank=True, null=True)
    source_document_type = models.CharField(max_length=20, blank=True, null=True)
    page_number = models.IntegerField(blank=True, null=True)
    bbox = models.JSONField(blank=True, null=True)
    extraction_confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    source_tool = models.CharField(max_length=100, blank=True, null=True)

    # Optional public scraping metadata
    source_url = models.URLField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller_raw_data']),
            models.Index(fields=['source_tag']),
        ]
        db_table = 'acq_photo'

    def __str__(self):
        return f"Photo[{self.source_tag}] for SellerRawData {self.seller_raw_data.id}"



# -----------------------------------------------------------------------------------
# Broker Uploads: Document path helper
# -----------------------------------------------------------------------------------
def get_broker_document_path(instance, filename):
    """Generate a file path for storing broker-uploaded documents (any file type).
    
    Structure: broker_documents/{seller_id}/{broker_values_id}/{timestamped_filename}
    
    Docs reviewed:
    - Django File uploads: https://docs.djangoproject.com/en/5.0/topics/files/
    - FileField: https://docs.djangoproject.com/en/5.0/ref/models/fields/#filefield
    """
    # Identify owning records for stable folder grouping
    broker_values_id = instance.broker_valuation.pk
    # Resolve SellerRawData via hub 1:1: hub -> acq_raw
    raw = getattr(getattr(instance.broker_valuation, 'asset_hub', None), 'acq_raw', None)
    seller_id = getattr(getattr(raw, 'seller', None), 'id', 'unknown')

    # Timestamp filename to reduce collisions
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"

    return os.path.join('broker_documents', str(seller_id), str(broker_values_id), new_filename)


# -----------------------------------------------------------------------------------
# Broker Uploads: Documents model
# -----------------------------------------------------------------------------------
class BrokerDocument(models.Model):
    """Model to store broker documents (PDFs, DOCX, XLSX, etc.) with many-to-one
    relationship to BrokerValues.

    This is distinct from `DocumentPhoto` which contains images extracted from
    documents by future automation. `BrokerDocument` stores the original files
    that brokers upload in the portal.
    """

    # Many-to-one with BrokerValues (same parent as BrokerPhoto)
    broker_valuation = models.ForeignKey(
        BrokerValues,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    # Stable hub link (optional) and snapshot of source raw PK for durability
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='broker_documents',
        help_text='Stable hub ID (from broker_valuation.seller_raw_data.asset_hub).',
    )
    source_raw_id = models.IntegerField(null=True, blank=True, db_index=True, help_text='Snapshot of SellerRawData.id')

    # Generic file (allows any file type)
    file = models.FileField(upload_to=get_broker_document_path)
    original_name = models.CharField(max_length=255, blank=True, null=True)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Broker Document'
        verbose_name_plural = 'Broker Documents'
        ordering = ['uploaded_at']
        indexes = [
            models.Index(fields=['broker_valuation']),
        ]
        db_table = 'acq_broker_document'

    def __str__(self):
        hub_id = getattr(self.broker_valuation, 'asset_hub_id', None)
        return f"{self.file} document for hub {hub_id}"

"""
Note: PublicPhoto, DocumentPhoto, and BrokerPhoto have been consolidated into the
unified `Photo` model above. Any new reads/writes should go through `Photo`.
"""