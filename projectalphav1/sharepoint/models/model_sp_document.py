"""
SharePoint Document Model
=========================
Tracks files stored in SharePoint with backend database records.
Links documents to trades/assets and maintains sync between platform and SharePoint.

File Naming Convention: model_sp_document.py
Module: SharePoint (sp)
Purpose: Track SharePoint documents in Django database
"""

from django.conf import settings
from django.db import models


class DocumentCategory(models.TextChoices):
    """
    Valid document categories matching SharePoint folder structure.
    Ensures files are always in categorized folders, never at root level.
    """
    # Trade-level categories
    TRADE_BID = 'trade_bid', 'Trade - Bid'
    TRADE_LEGAL = 'trade_legal', 'Trade - Legal'
    TRADE_POST_CLOSE = 'trade_post_close', 'Trade - Post Close'
    
    # Asset-level categories
    ASSET_VALUATION = 'asset_valuation', 'Asset - Valuation'
    ASSET_COLLATERAL = 'asset_collateral', 'Asset - Collateral'
    ASSET_LEGAL = 'asset_legal', 'Asset - Legal'
    ASSET_TAX = 'asset_tax', 'Asset - Tax'
    ASSET_TITLE = 'asset_title', 'Asset - Title'
    ASSET_PHOTOS = 'asset_photos', 'Asset - Photos'


class SharePointDocument(models.Model):
    """
    Tracks documents stored in SharePoint.
    Maintains relationship between Django entities (trades/assets) and SharePoint files.
    
    Design: Platform is source of truth. SharePoint is storage layer.
    Users upload via platform only (SharePoint is read-only for users).
    """
    
    # Foreign key relationships to your entities
    # NOTE: You'll need to import your Trade/Asset models from acq_module
    # For now, using CharField for IDs to avoid circular imports
    trade_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text="Trade ID (e.g., TRD-2024-001)",
    )
    
    asset_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text="Asset ID within trade",
    )
    
    # Document categorization
    category = models.CharField(
        max_length=50,
        choices=DocumentCategory.choices,
        help_text="Document category - determines SharePoint folder location",
    )
    
    # File metadata
    file_name = models.CharField(
        max_length=256,
        help_text="Original uploaded file name",
    )
    
    file_type = models.CharField(
        max_length=50,
        help_text="File extension (pdf, xlsx, jpg, etc.)",
    )
    
    file_size_bytes = models.BigIntegerField(
        help_text="File size in bytes",
    )
    
    # SharePoint-specific fields
    sharepoint_path = models.CharField(
        max_length=1024,
        help_text="Full path in SharePoint (e.g., /Trades/TRD-2024-001/Legal/contract.pdf)",
    )
    
    sharepoint_item_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="SharePoint item ID from Microsoft Graph API",
    )
    
    sharepoint_drive_id = models.CharField(
        max_length=255,
        help_text="SharePoint drive ID from Microsoft Graph API",
    )
    
    sharepoint_web_url = models.URLField(
        max_length=1024,
        help_text="Direct URL to view file in SharePoint",
    )
    
    # Validation tracking
    is_validated = models.BooleanField(
        default=False,
        help_text="Whether file passed naming/content validation",
    )
    
    validation_errors = models.JSONField(
        default=dict,
        blank=True,
        help_text="Validation errors if any",
    )
    
    # Audit fields
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_sharepoint_documents',
        help_text="User who uploaded the file",
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When file was uploaded to SharePoint",
    )
    
    last_modified_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification timestamp",
    )
    
    # Soft delete for audit trail
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag - file archived in SharePoint",
    )
    
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When file was deleted/archived",
    )
    
    class Meta:
        db_table = 'sharepoint_document'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['trade_id', 'asset_id']),
            models.Index(fields=['sharepoint_item_id']),
            models.Index(fields=['category']),
            models.Index(fields=['is_deleted']),
        ]
        verbose_name = 'SharePoint Document'
        verbose_name_plural = 'SharePoint Documents'
    
    def __str__(self):
        """Human-readable representation"""
        location = self.trade_id or 'Unknown'
        if self.asset_id:
            location = f"{location}/{self.asset_id}"
        return f"{self.file_name} ({location})"
    
    def get_display_path(self):
        """Get user-friendly display path"""
        parts = self.sharepoint_path.split('/')
        return ' > '.join(p for p in parts if p)

