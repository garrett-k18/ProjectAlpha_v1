"""
Broker-specific CRM serializer.

What: Simple, focused serializer for broker CRM data
Why: Clean separation from complex unified CRM serializer
Where: Used by broker-only API endpoints
How: Minimal fields, MSA support, no complex relationships
"""

from rest_framework import serializers
from core.models.model_co_crm import MasterCRM, BrokerMSAAssignment
from core.models.model_co_geoAssumptions import StateReference, MSAReference


class BrokerCRMSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for broker CRM data with performance focus.
    
    What: Handles broker CRUD with minimal database queries
    Why: Fast loading of 200+ brokers with relationships
    How: Efficient field access, lazy MSA loading, optimized firm handling
    """
    
    # Frontend compatibility - map contact_name to name
    name = serializers.CharField(source='contact_name', allow_blank=True, allow_null=True, required=False)
    
    # Firm name from FK relationship (already prefetched)
    firm = serializers.CharField(source='firm_ref.name', allow_blank=True, allow_null=True, required=False, read_only=True)
    
    # States as list of state codes (already prefetched)
    states = serializers.SlugRelatedField(
        many=True,
        slug_field='state_code',
        queryset=StateReference.objects.all(),
        required=False,
    )
    
    # MSAs as list of MSA names - write-only field for updates
    msas = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        write_only=True,  # Only for writing, reading handled in to_representation
        help_text="List of MSA names for this broker"
    )
    
    # Add firm_id for efficient updates
    firm_id = serializers.IntegerField(source='firm_ref.id', read_only=True, allow_null=True)
    
    class Meta:
        model = MasterCRM
        fields = [
            'id',
            'name',           # Maps to contact_name
            'contact_name',   # Direct field
            'firm',           # From firm_ref.name (read-only)
            'firm_id',        # For efficient updates
            'email',
            'phone', 
            'city',
            'states',         # State codes array
            'msas',           # MSA names array (write-only, read via to_representation)
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'firm', 'firm_id']
    
    def to_representation(self, instance):
        """Custom representation to populate MSAs from database."""
        data = super().to_representation(instance)
        
        # Apply title case formatting to names
        if data.get('contact_name'):
            data['contact_name'] = data['contact_name'].title()
        if data.get('name'):
            data['name'] = data['name'].title()
        if data.get('firm'):
            data['firm'] = data['firm'].title()
        
        # Always add MSAs field - handle brokers with or without existing assignments
        try:
            if hasattr(instance, '_prefetched_objects_cache') and 'msa_assignments' in instance._prefetched_objects_cache:
                data['msas'] = [
                    assignment.msa.msa_name 
                    for assignment in instance.msa_assignments.all() 
                    if assignment.is_active and assignment.msa
                ]
            else:
                # Fallback for non-prefetched objects
                data['msas'] = list(
                    instance.msa_assignments.filter(
                        is_active=True,
                        msa__isnull=False
                    ).values_list('msa__msa_name', flat=True)
                )
        except Exception:
            # If there's any issue accessing MSA assignments, default to empty list
            data['msas'] = []
        
        return data
    
    def create(self, validated_data):
        """Create broker with optimized relationship handling."""
        # Extract fields that need special handling
        states = validated_data.pop('states', [])
        msas = validated_data.pop('msas', [])
        
        # Force broker tag
        validated_data['tag'] = MasterCRM.ContactTag.BROKER
        
        # Create broker
        broker = MasterCRM.objects.create(**validated_data)
        
        # Set states efficiently
        if states:
            broker.states.set(states)
        
        # Set MSAs via junction table (only if provided)
        if msas:
            self._update_msa_assignments(broker, msas)
        
        return broker
    
    def update(self, instance, validated_data):
        """Update broker with optimized relationship handling."""
        # Extract special fields
        states = validated_data.pop('states', None)
        msas = validated_data.pop('msas', None)
        
        # Update basic fields efficiently
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=list(validated_data.keys()))  # Only update changed fields
        
        # Update states efficiently
        if states is not None:
            instance.states.set(states)
        
        # Update MSAs only if provided
        if msas is not None:
            self._update_msa_assignments(instance, msas)
        
        return instance
    
    def _update_msa_assignments(self, broker, msa_names):
        """Update MSA assignments efficiently via bulk operations."""
        from core.models.model_co_geoAssumptions import MSAReference
        
        # Clear existing assignments efficiently
        BrokerMSAAssignment.objects.filter(broker=broker).delete()
        
        if not msa_names:
            return
        
        # Get MSAs in bulk
        msa_lookup = {msa.msa_name: msa for msa in MSAReference.objects.filter(msa_name__in=msa_names)}
        
        # Create assignments in bulk
        assignments = []
        for i, msa_name in enumerate(msa_names):
            if msa_name in msa_lookup:
                assignments.append(BrokerMSAAssignment(
                    broker=broker,
                    msa=msa_lookup[msa_name],
                    priority=i + 1,
                    is_active=True
                ))
        
        if assignments:
            BrokerMSAAssignment.objects.bulk_create(assignments)
