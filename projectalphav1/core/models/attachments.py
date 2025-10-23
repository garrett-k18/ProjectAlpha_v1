from __future__ import annotations

from django.db import models
from django.conf import settings
import os
from datetime import datetime

# -----------------------------------------------------------------------------------
# Photos and Documents (hub-first attachments)
# -----------------------------------------------------------------------------------

def get_photo_path(instance, filename):
    """Generate a unified file path for all photos.

    Hub-first structure: photos/{asset_hub_id}/{timestamped_filename}
    This avoids coupling to Seller/Trade tables and supports photos throughout asset life.
    """
    hub_id = getattr(instance, 'asset_hub_id', None) or 'unknown'

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"

    return os.path.join('photos', str(hub_id), new_filename)


class Photo(models.Model):
    """Unified photo model for all sources (broker, document, public, internal).
DEPRECATE
    Hub-first: photos belong to `AssetIdHub` and are not tied to `SellerRawData` directly.
    """

    # Owning asset hub (many photos per hub)
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_photos',
        help_text='Stable hub ID for this photo.',
    )

    # Optional reference back to the raw row at the time of ingestion for traceability
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

    # Optional document-related metadata
    source_document_name = models.CharField(max_length=255, blank=True, null=True)
    source_document_type = models.CharField(max_length=20, blank=True, null=True)
    page_number = models.IntegerField(blank=True, null=True)
    bbox = models.JSONField(blank=True, null=True)
    extraction_confidence = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    source_tool = models.CharField(max_length=100, blank=True, null=True)

    # Optional public scraping metadata
    source_url = models.URLField(blank=True, null=True)
    
    # Valuation relationship
    valuation = models.ForeignKey(
        'core.Valuation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='photos',
        help_text='Valuation this photo is associated with.'
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_photos',
        help_text='User who created this photo.'
    )

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset_hub']),
            models.Index(fields=['source_tag']),
        ]
        db_table = 'acq_photo'

    def __str__(self):
        return f"Photo[{self.source_tag}] for hub {self.asset_hub_id}"


# Documents ------------------------------------------------------------------------

def get_document_path(instance, filename):
    """Generate a file path for storing uploaded documents.

    Hub-first structure: documents/{asset_hub_id}/{timestamped_filename}
    """
    hub_id = getattr(instance, 'asset_hub_id', None) or 'unknown'

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"

    return os.path.join('documents', str(hub_id), new_filename)


class Document(models.Model):
    """Generic document model (PDFs, DOCX, XLSX, etc.) linked to an AssetIdHub.
DEPRECATE
    Hub-first: many documents per asset hub.
    """

    # Owning asset hub
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        help_text='Stable hub ID this document belongs to.',
    )
    # Optional reference back to source raw row for lineage
    source_raw_id = models.IntegerField(null=True, blank=True, db_index=True, help_text='Snapshot of SellerRawData.id')
    
    # Valuation relationship
    valuation = models.ForeignKey(
        'core.Valuation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        help_text='Valuation this document is associated with.'
    )

    # Generic file (allows any file type)
    file = models.FileField(upload_to=get_document_path)
    original_name = models.CharField(max_length=255, blank=True, null=True)

    # Audit
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_documents',
        help_text='User who uploaded this document.'
    )

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['uploaded_at']
        indexes = [
            models.Index(fields=['asset_hub']),
        ]
        db_table = 'acq_broker_document'

    def __str__(self):
        return f"{self.file} for hub {self.asset_hub_id}"
