"""
Awarded Assets Serializers

WHAT: Request/response serializers for awarded assets workflow
WHY: Validate input and structure API responses
HOW: DRF serializers with custom validation

Docs reviewed:
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
"""

from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    """
    WHAT: Serializer for file upload request
    WHY: Validate uploaded file and trade ID
    HOW: FileField for file, IntegerField for trade_id
    """
    # WHAT: The uploaded file
    # WHY: User uploads CSV/Excel/PDF with awarded IDs
    # HOW: FileField handles multipart/form-data
    file = serializers.FileField(
        required=True,
        help_text="CSV, Excel, PDF, or image file containing awarded asset IDs"
    )
    
    # WHAT: Trade to process
    # WHY: Scope operation to specific trade
    # HOW: IntegerField with validation
    trade_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="ID of the trade to process"
    )
    
    def validate_file(self, value):
        """
        WHAT: Validate uploaded file
        WHY: Ensure file is readable and reasonable size
        HOW: Check size and extension
        """
        # WHAT: Check file size (max 50MB)
        # WHY: Prevent memory issues
        # HOW: Compare to 50 * 1024 * 1024 bytes
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File too large. Maximum size is 50MB. Your file is {value.size / 1024 / 1024:.1f}MB"
            )
        
        # WHAT: Check file extension
        # WHY: Only accept supported formats
        # HOW: Check file name suffix
        allowed_extensions = [
            '.csv', '.xlsx', '.xls', '.pdf', 
            '.png', '.jpg', '.jpeg', '.gif', '.webp'
        ]
        
        filename = value.name.lower()
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return value


class ExtractionResponseSerializer(serializers.Serializer):
    """
    WHAT: Serializer for AI extraction response
    WHY: Structure the extraction results
    HOW: Nested fields for identifiers and metadata
    """
    identifiers = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of extracted asset IDs"
    )
    
    confidence = serializers.CharField(
        help_text="AI confidence level: high, medium, low, none"
    )
    
    detected_format = serializers.CharField(
        help_text="Description of detected file format"
    )
    
    count = serializers.IntegerField(
        help_text="Number of unique IDs extracted"
    )
    
    error = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Error message if extraction failed"
    )


class AssetSummarySerializer(serializers.Serializer):
    """
    WHAT: Serializer for individual asset in preview
    WHY: Show key asset details in preview
    HOW: Basic fields for display
    """
    id = serializers.IntegerField(help_text="Asset database ID")
    sellertape_id = serializers.CharField(help_text="Seller tape ID")
    street_address = serializers.CharField(help_text="Property address")
    city = serializers.CharField(help_text="City")
    state = serializers.CharField(help_text="State")
    current_balance = serializers.FloatField(help_text="Current loan balance")
    acquisition_status = serializers.CharField(help_text="Current status: KEEP or DROP")
    matched_on = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Which ID field matched (for kept assets)"
    )


class PreviewSummarySerializer(serializers.Serializer):
    """
    WHAT: Serializer for preview summary statistics
    WHY: Show counts before executing drop
    HOW: Integer fields for each category
    """
    total_in_trade = serializers.IntegerField(
        help_text="Total assets in trade before drop"
    )
    matched_from_file = serializers.IntegerField(
        help_text="Number of assets matched from uploaded file"
    )
    will_keep = serializers.IntegerField(
        help_text="Number of assets that will be kept"
    )
    will_drop = serializers.IntegerField(
        help_text="Number of assets that will be dropped"
    )
    unmatched_from_file = serializers.IntegerField(
        help_text="Number of IDs from file not found in database"
    )


class PreviewResponseSerializer(serializers.Serializer):
    """
    WHAT: Serializer for drop preview response
    WHY: Structure the preview data for frontend
    HOW: Nested serializers for assets and summary
    """
    matched_assets = AssetSummarySerializer(
        many=True,
        help_text="Assets that will be KEPT (matched awarded IDs)"
    )
    
    will_be_dropped = AssetSummarySerializer(
        many=True,
        help_text="Assets that will be DROPPED (not in awarded list)"
    )
    
    unmatched_ids = serializers.ListField(
        child=serializers.CharField(),
        help_text="IDs from file that were not found in database"
    )
    
    summary = PreviewSummarySerializer(
        help_text="Summary statistics"
    )
    
    trade_name = serializers.CharField(
        help_text="Name of the trade being processed"
    )
    
    trade_id = serializers.IntegerField(
        help_text="ID of the trade being processed"
    )


class ConfirmDropSerializer(serializers.Serializer):
    """
    WHAT: Serializer for drop confirmation request
    WHY: Validate the list of IDs to keep before executing
    HOW: ListField of strings
    """
    trade_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="ID of the trade to process"
    )
    
    awarded_ids = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=False,
        help_text="List of asset IDs to KEEP (all others will be dropped)"
    )
    
    def validate_awarded_ids(self, value):
        """
        WHAT: Validate awarded IDs list
        WHY: Ensure we have valid data
        HOW: Check for empty strings, duplicates
        """
        # WHAT: Remove empty strings and whitespace
        # WHY: Clean user input
        # HOW: Strip and filter
        cleaned = [str(id_val).strip() for id_val in value if str(id_val).strip()]
        
        if not cleaned:
            raise serializers.ValidationError("awarded_ids cannot be empty")
        
        return cleaned


class ExecuteResponseSerializer(serializers.Serializer):
    """
    WHAT: Serializer for drop execution response
    WHY: Structure the result of drop operation
    HOW: Success flag and counts
    """
    success = serializers.BooleanField(
        help_text="Whether operation succeeded"
    )
    
    kept_count = serializers.IntegerField(
        help_text="Number of assets kept"
    )
    
    dropped_count = serializers.IntegerField(
        help_text="Number of assets dropped"
    )
    
    dropped_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Database IDs of dropped assets"
    )
    
    message = serializers.CharField(
        help_text="Success message"
    )


class UndoDropSerializer(serializers.Serializer):
    """
    WHAT: Serializer for undo drop request
    WHY: Validate undo operation parameters
    HOW: Optional list of asset IDs to restore
    """
    trade_id = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="ID of the trade"
    )
    
    asset_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True,
        help_text="Specific asset IDs to restore (optional - if not provided, restores all dropped assets)"
    )


class UndoResponseSerializer(serializers.Serializer):
    """
    WHAT: Serializer for undo response
    WHY: Structure the undo result
    HOW: Success flag and count
    """
    success = serializers.BooleanField(
        help_text="Whether operation succeeded"
    )
    
    restored_count = serializers.IntegerField(
        help_text="Number of assets restored to KEEP status"
    )
    
    message = serializers.CharField(
        help_text="Success message"
    )


class DropHistorySerializer(serializers.Serializer):
    """
    WHAT: Serializer for drop history response
    WHY: Show current state of dropped assets
    HOW: List of dropped assets with counts
    """
    dropped_assets = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of currently dropped assets"
    )
    
    dropped_count = serializers.IntegerField(
        help_text="Number of dropped assets"
    )
    
    kept_count = serializers.IntegerField(
        help_text="Number of kept assets"
    )
    
    trade_name = serializers.CharField(
        help_text="Name of the trade"
    )
