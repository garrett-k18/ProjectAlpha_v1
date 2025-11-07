"""
Serializers for assumptions models (StateReference, FCTimelines, etc.)

What this does:
- Converts Django model instances to/from JSON for API responses
- Handles validation of incoming data from frontend
- Maps backend field names to frontend-friendly names

Location: projectalphav1/core/serializers/assumptions.py
"""
from rest_framework import serializers
from core.models import StateReference, FCTimelines, FCStatus, CommercialUnits, Servicer


"""
Serializers for assumptions models (StateReference, FCTimelines, etc.)

What this does:
- Converts Django model instances to/from JSON for API responses
- Handles validation of incoming data from frontend
- Maps backend field names to frontend-friendly names

Location: projectalphav1/core/serializers/assumptions.py
"""
from rest_framework import serializers
from core.models import StateReference, FCTimelines, FCStatus, CommercialUnits, Servicer


class StateReferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for StateReference model

    What this does:
    - Serializes all StateReference fields for frontend consumption
    - Validates user edits before saving to database
    - Maps snake_case backend fields to camelCase frontend fields
    """
    # Map backend field names to frontend camelCase
    code = serializers.CharField(source='state_code', read_only=True)
    name = serializers.CharField(source='state_name', read_only=True)
    isJudicial = serializers.BooleanField(source='judicialvsnonjudicial', read_only=True)
    fcStateMonths = serializers.IntegerField(source='fc_state_months')
    evictionDuration = serializers.IntegerField(source='eviction_duration')
    rehabDuration = serializers.IntegerField(source='rehab_duration')
    reoMarketingDuration = serializers.IntegerField(source='reo_marketing_duration')
    reoLocalMarketExtDuration = serializers.IntegerField(source='reo_local_market_ext_duration')
    dilDurationAvg = serializers.IntegerField(source='dil_duration_avg')
    propertyTaxRate = serializers.DecimalField(source='property_tax_rate', max_digits=6, decimal_places=4)
    transferTaxRate = serializers.DecimalField(source='transfer_tax_rate', max_digits=6, decimal_places=4)
    insuranceRateAvg = serializers.DecimalField(source='insurance_rate_avg', max_digits=6, decimal_places=4)
    fcLegalFeesAvg = serializers.DecimalField(source='fc_legal_fees_avg', max_digits=10, decimal_places=2)
    dilCostAvg = serializers.DecimalField(source='dil_cost_avg', max_digits=10, decimal_places=2)
    cfkCostAvg = serializers.DecimalField(source='cfk_cost_avg', max_digits=10, decimal_places=2)
    valueAdjustmentAnnual = serializers.DecimalField(source='value_adjustment_annual', max_digits=6, decimal_places=4)
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = StateReference
        fields = [
            'code', 'name', 'isJudicial',
            'fcStateMonths', 'evictionDuration', 'rehabDuration',
            'reoMarketingDuration', 'reoLocalMarketExtDuration', 'dilDurationAvg',
            'propertyTaxRate', 'transferTaxRate', 'insuranceRateAvg',
            'fcLegalFeesAvg', 'dilCostAvg', 'cfkCostAvg',
            'valueAdjustmentAnnual', 'notes'
        ]
        # state_code is the primary key, so it's read-only
        read_only_fields = ['code', 'name', 'isJudicial']


class FCStatusSerializer(serializers.ModelSerializer):
    """Serializer for FCStatus model"""
    
    class Meta:
        model = FCStatus
        fields = ['id', 'status', 'order', 'notes']


class FCTimelinesSerializer(serializers.ModelSerializer):
    """Serializer for FCTimelines model"""
    stateCode = serializers.CharField(source='state.state_code', read_only=True)
    stateName = serializers.CharField(source='state.state_name', read_only=True)
    statusName = serializers.CharField(source='fc_status.get_status_display', read_only=True)
    durationDays = serializers.IntegerField(source='duration_days', allow_null=True)
    costAvg = serializers.DecimalField(source='cost_avg', max_digits=10, decimal_places=2, allow_null=True)
    
    class Meta:
        model = FCTimelines
        fields = ['id', 'stateCode', 'stateName', 'statusName', 'durationDays', 'costAvg', 'notes']


class CommercialUnitsSerializer(serializers.ModelSerializer):
    """Serializer for CommercialUnits model"""
    fcCostScale = serializers.DecimalField(source='fc_cost_scale', max_digits=5, decimal_places=2)
    rehabCostScale = serializers.DecimalField(source='rehab_cost_scale', max_digits=5, decimal_places=2)
    rehabDurationScale = serializers.DecimalField(source='rehab_duration_scale', max_digits=5, decimal_places=2)
    
    class Meta:
        model = CommercialUnits
        fields = ['id', 'units', 'fcCostScale', 'rehabCostScale', 'rehabDurationScale']


class ServicerSerializer(serializers.ModelSerializer):
    """Serializer for Servicer model"""
    servicerName = serializers.CharField(source='servicer_name')
    contactName = serializers.CharField(source='contact_name', required=False, allow_null=True, allow_blank=True)
    contactEmail = serializers.EmailField(source='contact_email', required=False, allow_null=True, allow_blank=True)
    contactPhone = serializers.CharField(source='contact_phone', required=False, allow_null=True, allow_blank=True)
    servicingTransferDuration = serializers.IntegerField(source='servicing_transfer_duration', required=False, allow_null=True)
    boardFee = serializers.DecimalField(source='board_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    currentFee = serializers.DecimalField(source='current_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    thirtdayFee = serializers.DecimalField(source='thirtday_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    sixtydayFee = serializers.DecimalField(source='sixtyday_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    ninetydayFee = serializers.DecimalField(source='ninetyday_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    onetwentydayFee = serializers.DecimalField(source='onetwentyday_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    fcFee = serializers.DecimalField(source='fc_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    bkFee = serializers.DecimalField(source='bk_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    modFee = serializers.DecimalField(source='mod_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    dilFee = serializers.DecimalField(source='dil_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    thirdpartyFee = serializers.DecimalField(source='thirdparty_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    reoFee = serializers.DecimalField(source='reo_fee', max_digits=10, decimal_places=2, required=False, allow_null=True)
    reoDays = serializers.IntegerField(source='reo_days', required=False, allow_null=True)
    # WHAT: Allow 2 decimal places for percentage input (e.g., 1.50 for 1.50%)
    # WHY: User enters percentage with 2 decimals, backend converts to 4 decimal storage (0.0150)
    liqfeePct = serializers.DecimalField(source='liqfee_pct', max_digits=10, decimal_places=4, required=False, allow_null=True, coerce_to_string=False)
    liqfeeFlat = serializers.DecimalField(source='liqfee_flat', max_digits=10, decimal_places=2, required=False, allow_null=True)
    
    class Meta:
        model = Servicer
        fields = [
            'id', 'servicerName', 'contactName', 'contactEmail', 'contactPhone',
            'servicingTransferDuration', 'boardFee', 'currentFee', 'thirtdayFee',
            'sixtydayFee', 'ninetydayFee', 'onetwentydayFee', 'fcFee', 'bkFee',
            'modFee', 'dilFee', 'thirdpartyFee', 'reoFee', 'reoDays',
            'liqfeePct', 'liqfeeFlat'
        ]
    
    def validate_liqfee_pct(self, value):
        """
        WHAT: Convert percentage input to decimal for storage
        WHY: Frontend enters as percentage (1.5 for 1.5%), backend stores as decimal (0.015)
        HOW: Divide by 100 to convert percentage to decimal
        
        Example: User enters 1.5 (meaning 1.5%) -> stored as 0.015 in database
        """
        if value is not None:
            from decimal import Decimal
            # WHAT: Convert percentage to decimal by dividing by 100
            # WHY: Database stores as decimal (0.015), frontend displays as percent (1.5)
            return Decimal(str(value)) / Decimal('100')
        return value
    
    def to_representation(self, instance):
        """
        WHAT: Convert decimal back to percentage for display
        WHY: Database stores 0.0150, frontend wants to show 1.50
        HOW: Multiply by 100 when sending to frontend, preserve 2 decimal places
        """
        data = super().to_representation(instance)
        # WHAT: Convert liqfee_pct from decimal to percentage for frontend display
        # WHY: Keep 2 decimal places (e.g., 0.0150 → 1.50, not 1.5)
        if data.get('liqfeePct') is not None:
            from decimal import Decimal
            # WHAT: Multiply by 100 and quantize to 2 decimal places
            percentage_value = Decimal(str(data['liqfeePct'])) * Decimal('100')
            data['liqfeePct'] = float(percentage_value.quantize(Decimal('0.01')))
        return data