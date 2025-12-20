"""
Import Mapping Serializers

WHAT: Serializers for ImportMapping model CRUD operations
WHY: Provide API interface for managing column mappings
HOW: Thin wrappers around ImportMapping model with validation

USAGE:
    # List mappings
    serializer = ImportMappingListSerializer(mappings, many=True)
    
    # Create/update mapping
    serializer = ImportMappingSerializer(data=request.data)
    if serializer.is_valid():
        mapping = serializer.save()

Docs reviewed:
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF Relations: https://www.django-rest-framework.org/api-guide/relations/
"""

from rest_framework import serializers
from etl.models.model_etl_import_mapping import ImportMapping
from acq_module.models.model_acq_seller import Seller, Trade


class ImportMappingListSerializer(serializers.ModelSerializer):
    """
    WHAT: Lightweight serializer for listing mappings
    WHY: Provide essential fields for mapping selection UI
    HOW: Excludes heavy fields like full column_mapping for performance
    """
    
    # WHAT: Include seller name for display
    # WHY: Users need to see which seller mapping belongs to
    # HOW: Read-only field from related model
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    
    # WHAT: Include trade name for context
    # WHY: Show which trade mapping was created from
    # HOW: Read-only field from related model
    trade_name = serializers.CharField(source='trade.trade_name', read_only=True, allow_null=True)
    
    # WHAT: Include creator username
    # WHY: Show who created the mapping
    # HOW: Read-only field from User model
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    
    # WHAT: Include modifier username
    # WHY: Show who last edited the mapping
    # HOW: Read-only field from User model
    modified_by_username = serializers.CharField(source='modified_by.username', read_only=True, allow_null=True)
    
    # WHAT: Count of mapped fields
    # WHY: Quick metric for mapping completeness
    # HOW: Calculate length of column_mapping dict
    mapped_field_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ImportMapping
        fields = [
            'id',
            'mapping_name',
            'seller',
            'seller_name',
            'trade',
            'trade_name',
            'mapping_method',
            'is_default',
            'is_active',
            'original_filename',
            'created_by',
            'created_by_username',
            'modified_by',
            'modified_by_username',
            'created_at',
            'updated_at',
            'last_used_at',
            'usage_count',
            'mapped_field_count',
        ]
        read_only_fields = ['created_at', 'updated_at', 'usage_count', 'last_used_at']
    
    def get_mapped_field_count(self, obj):
        """
        WHAT: Return count of mapped fields
        WHY: Show how many fields are mapped
        HOW: Calculate length of column_mapping dict
        """
        return len(obj.column_mapping) if obj.column_mapping else 0


class ImportMappingSerializer(serializers.ModelSerializer):
    """
    WHAT: Full serializer for creating/updating mappings
    WHY: Handle all mapping fields including column_mapping JSON
    HOW: Validates mapping and handles user tracking
    """
    
    # WHAT: Include seller name for display
    # WHY: Show seller context in responses
    # HOW: Read-only field from related model
    seller_name = serializers.CharField(source='seller.name', read_only=True)
    
    # WHAT: Include trade name for display
    # WHY: Show trade context in responses
    # HOW: Read-only field from related model
    trade_name = serializers.CharField(source='trade.trade_name', read_only=True, allow_null=True)
    
    # WHAT: Validation results
    # WHY: Return validation status with full details
    # HOW: Call model's validate_mapping method
    validation_results = serializers.SerializerMethodField(read_only=True)
    
    # WHAT: Unmapped columns
    # WHY: Show which source columns aren't mapped
    # HOW: Call model's get_unmapped_columns method
    unmapped_columns = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ImportMapping
        fields = [
            'id',
            'seller',
            'seller_name',
            'trade',
            'trade_name',
            'mapping_name',
            'column_mapping',
            'source_columns',
            'mapping_method',
            'is_default',
            'is_active',
            'original_filename',
            'import_stats',
            'notes',
            'created_by',
            'modified_by',
            'created_at',
            'updated_at',
            'last_used_at',
            'usage_count',
            'validation_results',
            'unmapped_columns',
        ]
        read_only_fields = ['created_at', 'updated_at', 'usage_count', 'last_used_at']
    
    def get_validation_results(self, obj):
        """Return full validation results"""
        return obj.validate_mapping()
    
    def get_unmapped_columns(self, obj):
        """Return list of unmapped source columns"""
        return obj.get_unmapped_columns()
    
    def validate_column_mapping(self, value):
        """
        WHAT: Validate column_mapping JSON structure
        WHY: Ensure mapping is a valid dict before saving
        HOW: Check type and basic structure
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("column_mapping must be a dictionary")
        
        # WHAT: Validate all keys and values are strings
        # WHY: Prevent invalid data types in mapping
        # HOW: Check each key-value pair
        for source_col, target_field in value.items():
            if not isinstance(source_col, str) or not isinstance(target_field, str):
                raise serializers.ValidationError(
                    "All column_mapping keys and values must be strings"
                )
        
        return value
    
    def validate_source_columns(self, value):
        """
        WHAT: Validate source_columns is a list
        WHY: Ensure proper data structure
        HOW: Check type
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("source_columns must be a list")
        return value
    
    def create(self, validated_data):
        """
        WHAT: Create new mapping with user tracking
        WHY: Track who created the mapping
        HOW: Set created_by from request user
        """
        # WHAT: Get current user from request context
        # WHY: Track mapping creator
        # HOW: Access request.user from serializer context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['modified_by'] = request.user
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        WHAT: Update mapping with user tracking
        WHY: Track who modified the mapping
        HOW: Set modified_by from request user
        """
        # WHAT: Get current user from request context
        # WHY: Track mapping editor
        # HOW: Access request.user from serializer context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['modified_by'] = request.user
        
        # WHAT: If mapping was edited, update method to HYBRID
        # WHY: Track that mapping has been manually modified
        # HOW: Check if column_mapping changed and original was AI
        if 'column_mapping' in validated_data:
            if instance.mapping_method == ImportMapping.MappingMethod.AI:
                validated_data['mapping_method'] = ImportMapping.MappingMethod.HYBRID
        
        return super().update(instance, validated_data)


class ImportMappingDetailSerializer(ImportMappingSerializer):
    """
    WHAT: Extended serializer with additional computed fields
    WHY: Provide comprehensive mapping details for edit view
    HOW: Adds field definitions and validation details
    """
    
    # WHAT: Available target fields from SellerRawData model
    # WHY: Show users what fields they can map to
    # HOW: Get field list from model metadata
    available_target_fields = serializers.SerializerMethodField(read_only=True)
    
    class Meta(ImportMappingSerializer.Meta):
        fields = ImportMappingSerializer.Meta.fields + ['available_target_fields']
    
    def get_available_target_fields(self, obj):
        """
        WHAT: Get list of available target fields from SellerRawData
        WHY: Provide field options for mapping editor
        HOW: Extract field names and types from model
        """
        from acq_module.models.model_acq_seller import SellerRawData
        
        fields = []
        # WHAT: Get all mappable fields from model
        # WHY: Users need to know what fields they can map to
        # HOW: Filter out auto-created and FK fields
        for field in SellerRawData._meta.get_fields():
            if field.auto_created or field.name in ['asset_hub', 'seller', 'trade']:
                continue
            
            fields.append({
                'name': field.name,
                'type': field.get_internal_type(),
                'required': not field.null and not field.blank,
                'help_text': getattr(field, 'help_text', ''),
            })
        
        return fields


class ImportMappingApplySerializer(serializers.Serializer):
    """
    WHAT: Serializer for applying a saved mapping to a new import
    WHY: Handle mapping reuse workflow
    HOW: Validates mapping ID and optional overrides
    """
    
    # WHAT: ID of mapping to apply
    # WHY: Identify which mapping to use
    # HOW: FK to ImportMapping
    mapping_id = serializers.IntegerField(required=True)
    
    # WHAT: Optional column mapping overrides
    # WHY: Allow users to adjust mapping for specific file
    # HOW: Dict of source -> target overrides
    overrides = serializers.JSONField(required=False, default=dict)
    
    # WHAT: Whether to save overrides as new mapping
    # WHY: Users may want to save adjusted mapping
    # HOW: Boolean flag
    save_as_new = serializers.BooleanField(required=False, default=False)
    
    # WHAT: Name for new mapping if save_as_new is True
    # WHY: Users need to name the new mapping
    # HOW: String field
    new_mapping_name = serializers.CharField(required=False, allow_blank=True)
    
    def validate_mapping_id(self, value):
        """
        WHAT: Validate mapping exists and is active
        WHY: Prevent using invalid or archived mappings
        HOW: Check database for mapping
        """
        try:
            mapping = ImportMapping.objects.get(pk=value, is_active=True)
        except ImportMapping.DoesNotExist:
            raise serializers.ValidationError(f"Active mapping with ID {value} not found")
        return value
    
    def validate(self, data):
        """
        WHAT: Cross-field validation
        WHY: Ensure save_as_new has required fields
        HOW: Check new_mapping_name when save_as_new is True
        """
        if data.get('save_as_new') and not data.get('new_mapping_name'):
            raise serializers.ValidationError({
                'new_mapping_name': 'Required when save_as_new is True'
            })
        return data
