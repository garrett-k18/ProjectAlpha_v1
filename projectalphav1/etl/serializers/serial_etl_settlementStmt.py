"""Serializers for trade-level settlement statement ETL models."""

from rest_framework import serializers

from etl.models import (
    TradeSettlementStatementDocument,
    TradeSettlementStatementETL,
    TradeSettlementStatementLineItem,
)


class TradeSettlementStatementDocumentSerializer(serializers.ModelSerializer):
    """Thin serializer wrapper for settlement statement documents."""

    class Meta:
        model = TradeSettlementStatementDocument
        fields = [
            "id",
            "file_name",
            "file_path",
            "file_mime_type",
            "file_size_bytes",
            "uploaded_at",
            "processed_at",
            "status",
            "status_message",
            "created_by",
            "created_at",
            "updated_at",
        ]


class TradeSettlementStatementETLSerializer(serializers.ModelSerializer):
    """Thin serializer wrapper for trade settlement statement ETL data."""

    # WHAT: Nested line items for the statement.
    # WHY: Expose raw line items alongside statement summary fields.
    line_items = serializers.SerializerMethodField()

    def get_line_items(self, obj):  # pragma: no cover - simple mapping
        # WHAT: Serialize line items using the dedicated serializer.
        # WHY: Keep line item field definitions centralized.
        return TradeSettlementStatementLineItemSerializer(obj.line_items.all(), many=True).data

    class Meta:
        model = TradeSettlementStatementETL
        fields = [
            "id",
            "document",
            "trade",
            "statement_date",
            "settlement_date",
            "trade_name",
            "seller_name",
            "buyer_name",
            "accepted_bid_amount",
            "deposit_amount",
            "pool_name",
            "currency_code",
            "total_upb",
            "total_purchase_price",
            "total_adjustments",
            "net_purchase_price",
            "line_items",
            "notes",
            "extracted_at",
            "created_at",
            "updated_at",
            "created_by",
        ]


class TradeSettlementStatementLineItemSerializer(serializers.ModelSerializer):
    """Thin serializer wrapper for trade settlement statement line items."""

    class Meta:
        model = TradeSettlementStatementLineItem
        fields = [
            "id",
            "statement",
            "line_number",
            "description",
            "amount",
            "category",
            "notes",
            "created_at",
            "updated_at",
        ]
