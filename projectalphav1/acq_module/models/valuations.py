from django.db import models
from .seller import SellerRawData
import os
from datetime import datetime

# Function to determine the upload path for broker photos
def get_broker_photo_path(instance, filename):
    """Generate a file path for storing broker photos
    
    Args:
        instance: The BrokerPhoto instance being saved
        filename: Original filename of the uploaded photo
        
    Returns:
        str: Path where the file will be stored
    """
    # Get the broker valuation ID and related seller raw data ID
    broker_id = instance.broker_valuation.id
    seller_id = instance.broker_valuation.seller_raw_data.id
    
    # Format the filename with timestamp to avoid collisions
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"
    
    # Return the path: broker_photos/seller_id/broker_id/filename
    return os.path.join('broker_photos', str(seller_id), str(broker_id), new_filename)


class InternalValuation(models.Model):
    """Model to store internal and third-party valuations linked to a specific SellerRawData instance"""
    # One-to-one relationship with SellerRawData
    seller_raw_data = models.OneToOneField(
        SellerRawData,
        on_delete=models.CASCADE,
        related_name='internal_valuation'
    )
    
    # Internal underwriting values
    internal_uw_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    internal_uw_arv_value = models.DecimalField(max_digits=15, decimal_places=2)
    internal_uw_value_date = models.DateField()

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
        indexes = [
            models.Index(fields=['seller_raw_data']),
        ]
        db_table = 'acq_internal_valuation'
    
    def __str__(self):
        return f"Internal Valuation for {self.seller_raw_data.id}"


class BrokerValues(models.Model):
    """Model to store broker valuations linked to a specific SellerRawData instance"""
    # One-to-one relationship with SellerRawData
    seller_raw_data = models.OneToOneField(
        SellerRawData,
        on_delete=models.CASCADE,
        related_name='broker_valuation'
    )
    
    # Broker values
    broker_asis_value = models.DecimalField(max_digits=15, decimal_places=2)
    broker_arv_value = models.DecimalField(max_digits=15, decimal_places=2)
    broker_value_date = models.DateField()
    broker_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Broker Values"
        verbose_name_plural = "Broker Values"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller_raw_data']),
        ]
        db_table = 'acq_broker_values'
    
    def __str__(self):
        return f"Broker Valuation for {self.seller_raw_data.id}"


class BrokerPhoto(models.Model):
    """Model to store broker photos with many-to-one relationship to BrokerValues"""
    # Many-to-one relationship with BrokerValues
    broker_valuation = models.ForeignKey(
        BrokerValues, 
        on_delete=models.CASCADE, 
        related_name='photos'
    )
    
    # Photo fields
    photo = models.ImageField(upload_to=get_broker_photo_path)
    
    # Timestamps
    upload_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Broker Photo"
        verbose_name_plural = "Broker Photos"
        ordering = ['upload_date']
        indexes = [
            models.Index(fields=['broker_valuation']),
        ]
        db_table = 'acq_broker_photo'
    
    def __str__(self):
        return f"{self.photo} photo for {self.broker_valuation.seller_raw_data.id}"


def get_broker_photo_path(instance, filename):
    """Generates file path for broker photos
    
    Creates path structure: broker_photos/[seller_id]/[trade_id]/[filename]
    """
    # For BrokerPhotos model
    if hasattr(instance, 'broker_valuation'):
        seller_id = instance.broker_valuation.seller_raw_data.seller.id
        trade_id = instance.broker_valuation.seller_raw_data.trade.id
    # For direct photos on BrokerValues model if we add them later
    else:
        seller_id = instance.seller_raw_data.seller.id
        trade_id = instance.seller_raw_data.trade.id
        
    return f'broker_photos/{seller_id}/{trade_id}/{filename}'


# -----------------------------------------------------------------------------------
# Public (Scraped) Photos
# -----------------------------------------------------------------------------------
# We store photos scraped from public sources (Google, Zillow, Realtor, Redfin, etc.)
# directly against the SellerRawData record. This allows us to always have a set of
# images regardless of whether broker photos are available. The upload path mirrors
# the broker scheme but under a different base folder (public_photos/) and includes
# a timestamp to avoid filename collisions.

def get_public_photo_path(instance, filename):
    """Generate a file path for storing public/scraped photos
    
    The structure used is: public_photos/{seller_id}/{trade_id}/{timestamped_filename}

    Args:
        instance: The PublicPhoto instance being saved
        filename: The original filename of the photo being uploaded

    Returns:
        str: The path within the MEDIA_ROOT where the image should be stored
    """
    # Extract identifiers from the related SellerRawData for stable folder grouping
    seller_id = instance.seller_raw_data.seller.id  # Seller id (parent entity)
    trade_id = instance.seller_raw_data.trade.id    # Trade id (seller's trade)

    # Append a timestamp to the base filename to avoid overwriting files with the same name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"

    # Build a hierarchical path: public_photos/seller_id/trade_id/filename
    return os.path.join('public_photos', str(seller_id), str(trade_id), new_filename)


class PublicPhoto(models.Model):
    """Public (scraped) photos tied directly to a SellerRawData record.

    This model is intended for photos gathered from public sources such as Google
    Street View, Zillow, Realtor, Redfin, etc. Keeping these separate from
    `BrokerPhoto` allows us to track provenance and metadata independently.
    """

    # Foreign key to the specific raw-data row this image represents
    seller_raw_data = models.ForeignKey(
        SellerRawData,
        on_delete=models.CASCADE,
        related_name='public_photos',  # Access via seller_raw_data.public_photos
        help_text='SellerRawData record this public photo belongs to.'
    )

    # The actual image file. Requires Pillow to be installed in the environment.
    photo = models.ImageField(
        upload_to=get_public_photo_path,
        help_text='Uploaded public/scraped image file.'
    )

    # Optional metadata about where the image was sourced from
    SOURCE_CHOICES = [
        ('google', 'Google'),
        ('zillow', 'Zillow'),
        ('realtor', 'Realtor'),
        ('redfin', 'Redfin'),
        ('other', 'Other'),
    ]
    source = models.CharField(
        max_length=50,
        choices=SOURCE_CHOICES,
        default='other',
        help_text='Origin/source of the public image.'
    )

    # Where the image was fetched from (if applicable)
    source_url = models.URLField(
        blank=True,
        null=True,
        help_text='Original URL of the public image, if available.'
    )

    # Optional caption/alt text for accessibility and context
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Short caption or alt text describing the image.'
    )

    # Mark a preferred image for quick selection in UIs
    is_primary = models.BooleanField(
        default=False,
        help_text='Flag to indicate this is the primary public image.'
    )

    # Timestamps
    scraped_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the image metadata/file was first recorded.'
    )

    class Meta:
        verbose_name = 'Public Photo'
        verbose_name_plural = 'Public Photos'
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['seller_raw_data']),
            models.Index(fields=['source']),
        ]
        db_table = 'acq_public_photo'

    def __str__(self):
        # Provide a readable representation including origin and owning record id
        base = f"PublicPhoto for SellerRawData {self.seller_raw_data.id}"
        return f"{base} ({self.source})"


# -----------------------------------------------------------------------------------
# Document-Extracted Photos
# -----------------------------------------------------------------------------------
# These are images that will be extracted by a future document processing tool from
# PDFs, Word docs, or other sources. We store them against SellerRawData to keep a
# complete picture of each loan/asset. We include metadata such as page number and
# optional bounding box for where the image came from in the source document.

def get_document_photo_path(instance, filename):
    """Generate a file path for storing document-extracted photos.

    Structure: document_photos/{seller_id}/{trade_id}/{timestamped_filename}

    We append a timestamp (and optionally page number if present) to reduce
    filename collisions. The MEDIA_ROOT is defined in settings and Django will
    handle storage relative to that directory.
    """
    # Extract identifiers from the related SellerRawData for stable folder grouping
    seller_id = instance.seller_raw_data.seller.id  # Seller id (parent entity)
    trade_id = instance.seller_raw_data.trade.id    # Trade id (seller's trade)

    # Build a safe, timestamped filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    # Optionally include page number in filename for traceability
    page_suffix = f"_p{instance.page_number}" if getattr(instance, 'page_number', None) else ""
    new_filename = f"{name}_{timestamp}{page_suffix}{ext}"

    return os.path.join('document_photos', str(seller_id), str(trade_id), new_filename)


class DocumentPhoto(models.Model):
    """Images extracted from uploaded documents, tied to `SellerRawData`.

    Fields are designed to capture provenance (which doc, which page), optional
    location (bounding box), and extraction confidence for QA workflows.
    """

    # Foreign key to the specific raw-data row this image relates to
    seller_raw_data = models.ForeignKey(
        SellerRawData,
        on_delete=models.CASCADE,
        related_name='document_photos',  # Access via seller_raw_data.document_photos
        help_text='SellerRawData record this document-extracted photo belongs to.'
    )

    # The extracted image file (requires Pillow installed)
    photo = models.ImageField(
        upload_to=get_document_photo_path,
        help_text='Extracted image saved from a source document.'
    )

    # Basic provenance about the source document
    DOC_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word (DOCX)'),
        ('image', 'Image'),
        ('other', 'Other'),
    ]
    source_document_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Original filename or identifier of the source document.'
    )
    source_document_type = models.CharField(
        max_length=20,
        choices=DOC_TYPE_CHOICES,
        default='other',
        help_text='Type of document the image was extracted from.'
    )
    page_number = models.IntegerField(
        blank=True,
        null=True,
        help_text='Page number in the source document where the image was found.'
    )

    # Optional bounding box of the image region in the source (document-space units)
    # Stored as JSON to be flexible: {"x": ..., "y": ..., "width": ..., "height": ...}
    bbox = models.JSONField(
        blank=True,
        null=True,
        help_text='Optional bounding box JSON (x, y, width, height) within the source document.'
    )

    # Extraction metadata
    extraction_confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Confidence score (0-100) from the extraction tool, if provided.'
    )
    source_tool = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Name/version of the extraction tool, for auditability.'
    )

    # Optional caption and primary flag for UI usage
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Short caption or alt text describing the image.'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Flag to indicate this is a primary/representative image.'
    )

    # Timestamps
    extracted_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When the image was extracted and recorded.'
    )

    class Meta:
        verbose_name = 'Document Photo'
        verbose_name_plural = 'Document Photos'
        ordering = ['-extracted_at']
        indexes = [
            models.Index(fields=['seller_raw_data']),
            models.Index(fields=['source_document_type']),
            models.Index(fields=['page_number']),
        ]
        db_table = 'acq_document_photo'

    def __str__(self):
        # Readable representation including owning record id and page
        page = f", p{self.page_number}" if self.page_number is not None else ''
        return f"DocumentPhoto for SellerRawData {self.seller_raw_data.id}{page}"