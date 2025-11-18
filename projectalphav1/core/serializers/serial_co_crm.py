"""
core.serializers.serial_co_crm

Purpose
-------
Serializers for MasterCRM model to support CRM API endpoints (Brokers, Trading Partners, Investors, etc.)

Docs Reviewed
-------------
- Django REST Framework ModelSerializer: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
- Field validation: https://www.django-rest-framework.org/api-guide/serializers/#validation
"""

from rest_framework import serializers
from core.models.model_co_crm import MasterCRM
from core.models.model_co_geoAssumptions import StateReference


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
    # Firm name is exposed as a simple string but backed by the firm_ref FK via
    # the MasterCRM.firm property, so API stays stable while data is normalized.
    firm = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        help_text="Firm/company name (mapped from firm_ref.name)"
    )
    # Expose firm_ref details for frontend
    firm_ref = serializers.SerializerMethodField(read_only=True)
    # MSA assignments for brokers (read-only, populated from BrokerMSAAssignment)
    msas = serializers.SerializerMethodField(read_only=True)
    msa_assignments = serializers.SerializerMethodField(read_only=True)
    # Map contact_name to name for frontend compatibility
    name = serializers.CharField(source='contact_name', allow_blank=True, allow_null=True, required=False)
    
    class Meta:
        model = MasterCRM
        fields = [
            'id',
            'name',                      # Maps to contact_name for frontend compatibility
            'firm',
            'firm_ref',                  # Expose firm FK details
            'contact_name',
            'states',
            'city',
            'msas',                      # MSA names array
            'msa_assignments',           # Full MSA assignment details
            'email',
            'phone',
            'tag',
            'tag_display',
            'preferred',
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
    
    def get_msas(self, obj):
        """
        Get MSA assignments for this broker.
        
        What: Returns list of MSA names assigned to this broker
        Why: Frontend needs to display MSA coverage information
        How: Queries BrokerMSAAssignment for active assignments and returns MSA names
        """
        if obj.tag != MasterCRM.ContactTag.BROKER:
            return []
        
        return list(
            obj.msa_assignments.filter(
                is_active=True,
                msa__isnull=False
            ).select_related('msa').values_list('msa__msa_name', flat=True)
        )
    
    def get_firm_ref(self, obj):
        """
        Get firm reference details.
        
        What: Returns firm FK details including ID, name, and states
        Why: Frontend needs access to firm relationship data
        How: Serializes the firm_ref FK if it exists
        """
        if not obj.firm_ref:
            return None
        
        return {
            'id': obj.firm_ref.id,
            'name': obj.firm_ref.name,
            'phone': obj.firm_ref.phone,
            'email': obj.firm_ref.email,
            'states': list(obj.firm_ref.states.values_list('state_code', flat=True)),
        }
    
    def get_msa_assignments(self, obj):
        """
        Get detailed MSA assignment information.
        
        What: Returns full MSA assignment details with priority and status
        Why: Frontend may need detailed assignment info for editing/management
        How: Serializes BrokerMSAAssignment records with MSA details
        """
        if obj.tag != MasterCRM.ContactTag.BROKER:
            return []
        
        assignments = obj.msa_assignments.select_related('msa').filter(msa__isnull=False)
        return [
            {
                'id': assignment.id,
                'msa_id': assignment.msa.id,
                'msa_name': assignment.msa.msa_name,
                'msa_code': assignment.msa.msa_code,
                'priority': assignment.priority,
                'is_active': assignment.is_active,
                'notes': assignment.notes,
            }
            for assignment in assignments
        ]
    
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
        # WHAT: Extract MSAs (handled via junction table)
        msas = validated_data.pop('msas', [])
        # WHAT: Extract firm name which is backed by firm_ref via property
        firm_value = validated_data.pop('firm', None)

        # WHAT: Create the MasterCRM instance with all other fields
        # WHY: Instance must exist before M2M relationships can be set
        instance = MasterCRM.objects.create(**validated_data)

        # WHAT: Apply firm name via property so it creates/links FirmCRM
        if firm_value is not None:
            instance.firm = firm_value
            instance.save(update_fields=['firm_ref'])

        # WHAT: Set the many-to-many states relationship
        # WHY: M2M requires instance to exist first
        if states:
            instance.states.set(states)

        # WHAT: Handle MSA assignments for brokers via junction table
        if msas and instance.tag == MasterCRM.ContactTag.BROKER:
            self._update_msa_assignments(instance, msas)

        return instance

    def update(self, instance, validated_data):
        """
        Update MasterCRM instance with proper relationship handling.
        """
        # Extract relationship fields
        states = validated_data.pop('states', None)
        msas = validated_data.pop('msas', None)
        firm_value = validated_data.pop('firm', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle firm update
        if firm_value is not None:
            instance.firm = firm_value

        instance.save()

        # Update states M2M
        if states is not None:
            instance.states.set(states)

        # Update MSA assignments for brokers
        if msas is not None and instance.tag == MasterCRM.ContactTag.BROKER:
            self._update_msa_assignments(instance, msas)

        return instance

    def _update_msa_assignments(self, broker_instance, msa_names):
        """
        Update MSA assignments via BrokerMSAAssignment junction table.
        
        What: Manages broker-to-MSA assignments through junction table
        Why: MSAs are not direct M2M but go through BrokerMSAAssignment
        How: Clear existing assignments and create new ones with priority=1
        """
        from core.models.model_co_geoAssumptions import MSAReference
        from core.models.model_co_crm import BrokerMSAAssignment

        # Clear existing assignments
        BrokerMSAAssignment.objects.filter(broker=broker_instance).delete()

        # Create new assignments
        for i, msa_name in enumerate(msa_names):
            try:
                msa = MSAReference.objects.get(msa_name=msa_name)
                BrokerMSAAssignment.objects.create(
                    broker=broker_instance,
                    msa=msa,
                    priority=i + 1,  # Set priority based on order
                    is_active=True
                )
            except MSAReference.DoesNotExist:
                # Skip unknown MSAs (could log warning here)
                continue


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


class MSAReferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for MSAReference model with state information for broker assignments.
    
    What: Converts MSAReference model instances to JSON for frontend broker MSA dropdowns
    Why: Frontend needs MSA options filtered by state for broker assignments
    How: Includes state code for filtering MSAs by broker's states
    """
    
    # Include state information for filtering
    state_code = serializers.CharField(source='state.state_code', read_only=True)
    state_name = serializers.CharField(source='state.state_name', read_only=True)
    
    class Meta:
        from core.models.model_co_geoAssumptions import MSAReference
        model = MSAReference
        fields = [
            'msa_code',  # Primary key field
            'msa_name',
            'state_code',
            'state_name',
        ]
        
    def to_representation(self, instance):
        """Add state_codes array for easier frontend filtering."""
        data = super().to_representation(instance)
        # Add state_codes as array for frontend compatibility
        if data.get('state_code'):
            data['state_codes'] = [data['state_code']]
        return data
