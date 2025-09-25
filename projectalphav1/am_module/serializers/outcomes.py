from __future__ import annotations

# Django REST Framework docs reviewed:
# - ModelSerializer: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
# - Validation: https://www.django-rest-framework.org/api-guide/serializers/#validation
# - Writable nested representations (avoided here for simplicity):
#   https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers

from typing import Any, Dict

from rest_framework import serializers

from am_module.models.am_data import (
    REOData, REOtask,
    FCSale, FCTask,
    DIL, DILTask,
    ShortSale, ShortSaleTask,
    Modification, ModificationTask,
)
from core.models import AssetIdHub
from core.models.crm import MasterCRM  # string refs used in models but serializer type hints are fine


# -----------------------------
# Outcome Serializers (1:1 hub)
# -----------------------------

class _AssetHubPKField(serializers.PrimaryKeyRelatedField):
    """Reusable helper for write-only asset_hub_id -> asset_hub mapping.

    We accept `asset_hub_id` in requests and map it to the FK `asset_hub` field.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('source', 'asset_hub')
        kwargs.setdefault('queryset', AssetIdHub.objects.all())
        kwargs.setdefault('write_only', True)
        super().__init__(**kwargs)


class REODataSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = REOData
        fields = [
            'asset_hub', 'asset_hub_id',
            'broker_crm',
            'list_price', 'list_date', 'under_contract_flag', 'under_contract_date',
            'contract_price', 'estimated_close_date', 'actual_close_date',
            'seller_credit_amt', 'purchase_type', 'gross_purchase_price',
        ]
        read_only_fields = ['asset_hub']

    def create(self, validated_data: Dict[str, Any]):
        # Idempotent: ensure 1:1 by asset_hub
        asset_hub = validated_data.get('asset_hub')
        obj, _ = REOData.objects.get_or_create(asset_hub=asset_hub, defaults=validated_data)
        if _ is False:
            # Update provided fields when already exists
            for k, v in validated_data.items():
                setattr(obj, k, v)
            obj.save()
        return obj


class FCSaleSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = FCSale
        fields = [
            'asset_hub', 'asset_hub_id',
            'legal_crm', 'fc_sale_sched_date', 'fc_sale_actual_date',
            'fc_bid_price', 'fc_sale_price',
        ]
        read_only_fields = ['asset_hub']

    def create(self, validated_data: Dict[str, Any]):
        asset_hub = validated_data.get('asset_hub')
        obj, _ = FCSale.objects.get_or_create(asset_hub=asset_hub, defaults=validated_data)
        if _ is False:
            for k, v in validated_data.items():
                setattr(obj, k, v)
            obj.save()
        return obj


class DILSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = DIL
        fields = [
            'asset_hub', 'asset_hub_id',
            'legal_crm', 'dil_completion_date', 'dil_cost', 'cfk_cost',
        ]
        read_only_fields = ['asset_hub']

    def create(self, validated_data: Dict[str, Any]):
        asset_hub = validated_data.get('asset_hub')
        obj, _ = DIL.objects.get_or_create(asset_hub=asset_hub, defaults=validated_data)
        if _ is False:
            for k, v in validated_data.items():
                setattr(obj, k, v)
            obj.save()
        return obj


class ShortSaleSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = ShortSale
        fields = [
            'asset_hub', 'asset_hub_id',
            'broker_crm', 'acceptable_min_offer', 'short_sale_date',
        ]
        read_only_fields = ['asset_hub']

    def create(self, validated_data: Dict[str, Any]):
        asset_hub = validated_data.get('asset_hub')
        obj, _ = ShortSale.objects.get_or_create(asset_hub=asset_hub, defaults=validated_data)
        if _ is False:
            for k, v in validated_data.items():
                setattr(obj, k, v)
            obj.save()
        return obj


class ModificationSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = Modification
        fields = [
            'asset_hub', 'asset_hub_id',
            'broker_crm', 'modification_date', 'modification_cost', 'modification_upb',
            'modification_term', 'modification_rate', 'modification_maturity_date',
            'modification_pi', 'modification_down_payment',
        ]
        read_only_fields = ['asset_hub']

    def create(self, validated_data: Dict[str, Any]):
        asset_hub = validated_data.get('asset_hub')
        obj, _ = Modification.objects.get_or_create(asset_hub=asset_hub, defaults=validated_data)
        if _ is False:
            for k, v in validated_data.items():
                setattr(obj, k, v)
            obj.save()
        return obj


# -----------------------
# Task Serializers (many)
# -----------------------

class REOTaskSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = REOtask
        fields = ['id', 'asset_hub', 'asset_hub_id', 'reo_outcome', 'task_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure the reo_outcome belongs to same hub (safety)
        reo = attrs.get('reo_outcome')
        hub = attrs.get('asset_hub')
        if reo and hub and reo.asset_hub_id != hub.id:
            raise serializers.ValidationError('REO outcome and asset_hub mismatch.')
        return attrs


class FCTaskSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = FCTask
        fields = ['id', 'asset_hub', 'asset_hub_id', 'fc_sale', 'task_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        fc_sale = attrs.get('fc_sale')
        hub = attrs.get('asset_hub')
        if fc_sale and hub and fc_sale.asset_hub_id != hub.id:
            raise serializers.ValidationError('FCSale outcome and asset_hub mismatch.')
        return attrs


class DILTaskSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = DILTask
        fields = ['id', 'asset_hub', 'asset_hub_id', 'dil', 'task_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        dil = attrs.get('dil')
        hub = attrs.get('asset_hub')
        if dil and hub and dil.asset_hub_id != hub.id:
            raise serializers.ValidationError('DIL outcome and asset_hub mismatch.')
        return attrs


class ShortSaleTaskSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = ShortSaleTask
        fields = ['id', 'asset_hub', 'asset_hub_id', 'short_sale', 'task_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        ss = attrs.get('short_sale')
        hub = attrs.get('asset_hub')
        if ss and hub and ss.asset_hub_id != hub.id:
            raise serializers.ValidationError('ShortSale outcome and asset_hub mismatch.')
        return attrs


class ModificationTaskSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = ModificationTask
        fields = ['id', 'asset_hub', 'asset_hub_id', 'modification', 'task_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        m = attrs.get('modification')
        hub = attrs.get('asset_hub')
        if m and hub and m.asset_hub_id != hub.id:
            raise serializers.ValidationError('Modification outcome and asset_hub mismatch.')
        return attrs
