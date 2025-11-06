"""
core.serializers.crm_serializers

Purpose
-------
Serializers for MasterCRM model to support CRM API endpoints (Brokers, Trading Partners, Investors, etc.)

Docs Reviewed
-------------
- Django REST Framework ModelSerializer: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
- Field validation: https://www.django-rest-framework.org/api-guide/serializers/#validation
"""

from rest_framework import serializers
from core.models.crm import MasterCRM
from core.models.model_co_assumptions import StateReference


class MasterCRMSerializer(serializers.ModelSerializer):
    """
    Serializer for MasterCRM model.
    
    What: Converts MasterCRM model instances to/from JSON for API responses
    Why: Provides a clean API interface for CRM data with validation
    Where: Used by CRM API views (brokers, trading partners, investors, etc.)
    How: Maps all MasterCRM fields, validates tag choices using ContactTag enum
    """
    
    # Display the human-readable label for the tag field in responses
    tag_display = serializers.CharField(source='get_tag_display', read_only=True)
    # Many-to-many states as list of state codes (e.g., ["CA","AZ"]) for clean frontend binding
    states = serializers.SlugRelatedField(
        many=True,
        slug_field='state_code',
        queryset=StateReference.objects.all(),
        required=False,
    )
    
    class Meta:
        model = MasterCRM
        fields = [
            'id',
            'firm',
            'contact_name',
            'states',
            'city',
            'email',
            'phone',
            'tag',
            'tag_display',
            'alt_contact_name',
            'alt_contact_email',
            'alt_contact_phone',
            'nda_flag',
            'nda_signed',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'tag_display']
    
    def validate_tag(self, value):
        """
        Validate that the tag is one of the allowed ContactTag enum values.
        
        What: Ensures tag field contains valid enum value
        Why: Prevents invalid tag values from being saved
        How: Checks against MasterCRM.ContactTag.values list
        """
        if value and value not in MasterCRM.ContactTag.values:
            raise serializers.ValidationError(
                f"Invalid tag. Must be one of: {', '.join(MasterCRM.ContactTag.values)}"
            )
        return value
    
    def create(self, validated_data):
        """
        WHAT: Create MasterCRM instance with proper many-to-many handling
        WHY: States is a M2M field that must be set after instance creation
        WHERE: Called by DRF when POSTing to CRM endpoints
        HOW: Pop states from validated_data, create instance, then set states
        """
        # WHAT: Extract states M2M field before creating instance
        # WHY: M2M fields must be set after instance exists in DB
        states = validated_data.pop('states', [])
        
        # WHAT: Create the MasterCRM instance with all other fields
        # WHY: Instance must exist before M2M relationships can be set
        instance = MasterCRM.objects.create(**validated_data)
        
        # WHAT: Set the many-to-many states relationship
        # WHY: M2M requires instance to exist first
        if states:
            instance.states.set(states)
        
        return instance


class InvestorSerializer(MasterCRMSerializer):
    """
    Specialized serializer for Investor CRM entries.
    
    What: Extends MasterCRMSerializer with investor-specific defaults
    Why: Automatically sets tag='investor' for investor endpoints
    Where: Used by /api/core/crm/investors/ endpoint
    How: Overrides create() to force tag to INVESTOR
    """
    
    def create(self, validated_data):
        """
        Create a new MasterCRM entry with tag='investor'.
        
        What: Creates new investor CRM record
        Why: Ensures all records created via investor endpoint have correct tag
        How: Forces tag field to ContactTag.INVESTOR before saving
        """
        # Always set tag to investor for this endpoint
        validated_data['tag'] = MasterCRM.ContactTag.INVESTOR
        return super().create(validated_data)


class BrokerSerializer(MasterCRMSerializer):
    """
    Specialized serializer for Broker CRM entries.
    
    What: Extends MasterCRMSerializer with broker-specific defaults
    Why: Automatically sets tag='broker' for broker endpoints
    Where: Used by /api/core/crm/brokers/ endpoint
    How: Overrides create() to force tag to BROKER
    """
    
    def create(self, validated_data):
        """
        Create a new MasterCRM entry with tag='broker'.
        
        What: Creates new broker CRM record
        Why: Ensures all records created via broker endpoint have correct tag
        How: Forces tag field to ContactTag.BROKER before saving
        """
        # Always set tag to broker for this endpoint
        validated_data['tag'] = MasterCRM.ContactTag.BROKER
        return super().create(validated_data)


class TradingPartnerSerializer(MasterCRMSerializer):
    """
    Specialized serializer for Trading Partner CRM entries.
    
    What: Extends MasterCRMSerializer with trading partner-specific defaults
    Why: Automatically sets tag='trading_partner' for trading partner endpoints
    Where: Used by /api/core/crm/trading-partners/ endpoint
    How: Overrides create() to force tag to TRADING_PARTNER
    """
    
    def create(self, validated_data):
        """
        Create a new MasterCRM entry with tag='trading_partner'.
        
        What: Creates new trading partner CRM record
        Why: Ensures all records created via trading partner endpoint have correct tag
        How: Forces tag field to ContactTag.TRADING_PARTNER before saving
        """
        # Always set tag to trading_partner for this endpoint
        validated_data['tag'] = MasterCRM.ContactTag.TRADING_PARTNER
        return super().create(validated_data)


class LegalSerializer(MasterCRMSerializer):
    """
    Specialized serializer for Legal CRM entries.
    
    What: Extends MasterCRMSerializer with legal-specific defaults
    Why: Automatically sets tag='legal' for legal endpoints
    Where: Used by /api/core/crm/legal/ endpoint
    How: Overrides create() to force tag to LEGAL
    """
    
    def create(self, validated_data):
        """
        Create a new MasterCRM entry with tag='legal'.
        
        What: Creates new legal CRM record
        Why: Ensures all records created via legal endpoint have correct tag
        How: Forces tag field to ContactTag.LEGAL before saving
        """
        # Always set tag to legal for this endpoint
        validated_data['tag'] = MasterCRM.ContactTag.LEGAL
        return super().create(validated_data)


class ServicerSerializer(MasterCRMSerializer):
    """
    Specialized serializer for Servicer CRM entries.
    
    What: Extends MasterCRMSerializer with servicer-specific defaults
    Why: Automatically sets tag='servicer' for servicer endpoints
    Where: Used by /api/core/crm/servicers/ endpoint
    How: Overrides create() to force tag to SERVICER
    """
    
    def create(self, validated_data):
        """
        Create a new MasterCRM entry with tag='servicer'.
        
        What: Creates new servicer CRM record
        Why: Ensures all records created via servicer endpoint have correct tag
        How: Forces tag field to ContactTag.SERVICER before saving
        """
        # Always set tag to servicer for this endpoint
        validated_data['tag'] = MasterCRM.ContactTag.SERVICER
        return super().create(validated_data)
