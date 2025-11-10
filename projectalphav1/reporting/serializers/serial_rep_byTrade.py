"""
Serializer: By Trade Report

WHAT: Field definitions for By Trade report (chart and grid data)
WHY: Single source of truth for API response structure
WHERE: Imported by view_rep_trade.py
HOW: Define all fields that can be displayed in AG Grid

FILE NAMING: serial_rep_byTrade.py
- serial_ = Serializers folder
- _rep_ = Reporting module
- byTrade = Specific report type

ARCHITECTURE:
Service returns raw dicts → Serializer defines fields → View returns Response

Docs reviewed:
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF Fields: https://www.django-rest-framework.org/api-guide/fields/
"""

from rest_framework import serializers


class TradeChartSerializer(serializers.Serializer):
    """
    WHAT: Field definitions for By Trade chart data (Chart.js format)
    WHY: Chart needs minimal fields (x, y, meta)
    WHERE: Used by by_trade_chart endpoint
    
    FIELDS:
    - x: Trade name (chart label/x-axis)
    - y: Total UPB (chart value/y-axis)
    - meta: Additional data for tooltips and drill-down
    """
    # WHAT: Chart X-axis label (trade name)
    # WHY: Display trade name on chart
    x = serializers.CharField()
    
    # WHAT: Chart Y-axis value (total UPB)
    # WHY: Display dollar amount on chart
    y = serializers.FloatField()
    
    # WHAT: Metadata for tooltips and drill-down
    # WHY: Show extra info on hover and enable click-through
    meta = serializers.DictField()


class TradeGridSerializer(serializers.Serializer):
    """
    WHAT: Field definitions for By Trade AG Grid
    WHY: Define ALL possible columns users can show/hide in AG Grid
    WHERE: Used by by_trade_grid endpoint
    
    FIELDS: All metrics available for By Trade reporting
    
    HOW TO ADD FIELDS:
    1. Add annotation in serv_rep_queryBuilder.py (if from related model)
    2. Add to .annotate() in serv_rep_aggregations.py (if aggregating)
    3. Add to results dict in serv_rep_aggregations.py (include in return)
    4. Add field definition HERE ✅
    5. Add column def in frontend AG Grid
    """
    # ========================================================================
    # 🆔 IDENTIFIER FIELDS
    # ========================================================================
    # WHAT: Unique identifier for row
    # WHY: AG Grid needs unique ID for row selection and operations
    id = serializers.IntegerField()
    
    # WHAT: Trade ID (same as id for trade-level grouping)
    # WHY: Reference back to Trade model
    trade_id = serializers.IntegerField()
    
    # WHAT: Servicer ID from AssetIdHub
    # WHY: External identifier used by asset managers
    # NOTE: This would require annotation at asset level, not trade level
    # servicer_id = serializers.CharField(required=False, allow_null=True)
    
    # ========================================================================
    # 📝 CORE DESCRIPTIVE FIELDS
    # ========================================================================
    # WHAT: Trade name
    # WHY: Primary display name for trade
    trade_name = serializers.CharField()
    
    # WHAT: Seller name
    # WHY: Who sold this portfolio
    seller_name = serializers.CharField(required=False, allow_blank=True)
    
    # WHAT: Trade status
    # WHY: Current lifecycle status (DD, AWARDED, PASS, BOARD)
    status = serializers.CharField()
    
    # WHAT: Bid date (when trade was bid on)
    # WHY: Temporal tracking
    bid_date = serializers.DateTimeField(required=False, allow_null=True)
    
    # ========================================================================
    # 📊 COUNT METRICS
    # ========================================================================
    # WHAT: Number of assets in this trade
    # WHY: Portfolio size metric
    asset_count = serializers.IntegerField()
    
    # WHAT: Number of unique states in this trade
    # WHY: Geographic diversification metric
    state_count = serializers.IntegerField(required=False)
    
    # ========================================================================
    # 💰 BALANCE FIELDS (from SellerRawData)
    # ========================================================================
    # WHAT: Sum of current balances across all assets
    # WHY: Total unpaid principal balance for trade
    total_upb = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # WHAT: Average current balance per asset
    # WHY: Average loan size in trade
    avg_upb = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    
    # WHAT: Sum of total debt (includes fees, advances, etc.)
    # WHY: Total exposure for trade
    total_debt = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    
    # ========================================================================
    # 💰 SERVICER BALANCE FIELDS (from ServicerLoanData)
    # ========================================================================
    # WHAT: Sum of servicer current balances
    # WHY: Most up-to-date balance from servicing platform
    servicer_total_upb = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        required=False,
        allow_null=True
    )
    
    # WHAT: Average servicer balance per asset
    # WHY: Average loan size from servicer data
    servicer_avg_balance = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        required=False,
        allow_null=True
    )
    
    # WHAT: Sum of servicer total debt
    # WHY: Total debt from servicing platform
    servicer_total_debt_sum = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        required=False,
        allow_null=True
    )
    
    # ========================================================================
    # 📈 CALCULATED METRICS
    # ========================================================================
    # WHAT: Average LTV (Loan-to-Value) ratio
    # WHY: Risk metric - higher LTV = higher risk
    avg_ltv = serializers.FloatField(required=False)
    
    # WHAT: Delinquency rate (percentage of delinquent assets)
    # WHY: Portfolio quality metric
    delinquency_rate = serializers.FloatField(required=False)
    
    # ========================================================================
    # 📅 TIMESTAMP FIELDS
    # ========================================================================
    # WHAT: Last time this data was updated
    # WHY: Data freshness indicator
    last_updated = serializers.DateTimeField(required=False, allow_null=True)
    
    # ========================================================================
    # 🎯 ADD YOUR OWN FIELDS HERE - Copy patterns above!
    # ========================================================================
    # 
    # FIELD TYPES:
    # - CharField() - Text fields
    # - IntegerField() - Whole numbers
    # - FloatField() - Decimals (simple)
    # - DecimalField(max_digits=15, decimal_places=2) - Money (precise)
    # - DateField() - Dates only (YYYY-MM-DD)
    # - DateTimeField() - Dates with time
    # - BooleanField() - True/False
    # - SerializerMethodField() - Computed fields (needs get_field_name method)
    #
    # PARAMETERS:
    # - required=False - Field can be missing
    # - allow_null=True - Field can be null
    # - allow_blank=True - Text field can be empty string
    # - source='other_name' - Map to different dict key
    #
    # EXAMPLES:
    # property_type = serializers.CharField(required=False, allow_blank=True)
    # avg_interest_rate = serializers.FloatField(required=False, allow_null=True)
    # fc_count = serializers.IntegerField(required=False)
    # has_foreclosure = serializers.BooleanField(required=False)
    # ========================================================================


class TradeReportSerializer(serializers.Serializer):
    """
    WHAT: Combined serializer with both chart and grid data
    WHY: Single endpoint can return both chart and table data
    WHERE: Used if you want to return everything in one response
    """
    chart = TradeChartSerializer(many=True)
    grid = TradeGridSerializer(many=True)

