"""
am_module.serializers.asset_crm_serializer

Purpose
-------
Serializer for AssetCRMContact junction model to manage asset-to-CRM relationships.

What: Handles CRUD for asset-CRM contact links with role categorization
Why: Provides API for managing multiple contacts per asset (attorney, servicer, broker, etc.)
Where: Used by /api/am/asset-crm-contacts/ endpoint
How: Validates and serializes AssetCRMContact model with nested CRM details
"""

from rest_framework import serializers
from am_module.models.model_am_amData import AssetCRMContact
from core.models import AssetIdHub, MasterCRM
from core.serializers.serial_co_crm import MasterCRMSerializer


class AssetCRMContactSerializer(serializers.ModelSerializer):
    """
    Serializer for AssetCRMContact junction model.
    
    What: Manages asset-to-CRM contact relationships with roles
    Why: Allows assigning multiple contacts (legal, servicer, broker) to assets
    Where: Used by AssetCRMContactViewSet
    How: Accepts asset_hub_id and crm_id, returns nested CRM details
    """
    
    # Write-only fields for creating relationships
    asset_hub_id = serializers.PrimaryKeyRelatedField(
        source='asset_hub',
        queryset=AssetIdHub.objects.all(),
        write_only=True,
        help_text="Asset hub ID to link contact to"
    )
    
    crm_id = serializers.PrimaryKeyRelatedField(
        source='crm',
        queryset=MasterCRM.objects.all(),
        write_only=True,
        help_text="CRM contact ID to link"
    )
    
    # Read-only nested CRM details
    crm_details = MasterCRMSerializer(source='crm', read_only=True)
    
    class Meta:
        model = AssetCRMContact
        fields = [
            'id',
            'asset_hub', 'asset_hub_id',
            'crm', 'crm_id', 'crm_details',
            'role', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'asset_hub', 'crm', 'crm_details', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        """
        WHAT: Check for existing asset-CRM-role combination
        WHY: Provide better error message than generic unique constraint violation
        WHERE: Called before create() during POST
        HOW: Query for existing record, allow if found (idempotent)
        """
        # This validation is informational only - create() handles idempotency
        return attrs
    
    def create(self, validated_data):
        """
        Create or update AssetCRMContact link.
        
        What: Creates new asset-CRM link or updates existing one
        Why: Idempotent assignment - prevents duplicate role assignments
        How: Uses get_or_create with unique constraint on [asset_hub, crm, role]
        """
        asset_hub = validated_data.get('asset_hub')
        crm = validated_data.get('crm')
        role = validated_data.get('role')
        
        # Get or create to handle idempotent assignment
        obj, created = AssetCRMContact.objects.get_or_create(
            asset_hub=asset_hub,
            crm=crm,
            role=role,
            defaults={'notes': validated_data.get('notes', '')}
        )
        
        # Update notes if already exists
        if not created and 'notes' in validated_data:
            obj.notes = validated_data['notes']
            obj.save()
        
        return obj
