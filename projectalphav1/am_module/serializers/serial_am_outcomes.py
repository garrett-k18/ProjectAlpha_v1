from __future__ import annotations

# Django REST Framework docs reviewed:
# - ModelSerializer: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
# - Validation: https://www.django-rest-framework.org/api-guide/serializers/#validation
# - Writable nested representations (avoided here for simplicity):
#   https://www.django-rest-framework.org/api-guide/relations/#writable-nested-serializers

from typing import Any, Dict

from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from am_module.models.am_data import (
    REOData, REOtask,
    FCSale, FCTask,
    DIL, DILTask,
    ShortSale, ShortSaleTask,
    Modification, ModificationTask,
    REOScope,
)
from core.models import AssetIdHub
from core.models.crm import MasterCRM  # string refs used in models but serializer type hints are fine
from core.serializers.crm_serializers import MasterCRMSerializer


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
    # CRM contacts now accessed via: asset_hub.crm_contacts.filter(role='legal')
    crm_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FCSale
        fields = [
            'asset_hub', 'asset_hub_id',
            'crm_details', 'fc_sale_sched_date', 'fc_sale_actual_date',
            'fc_bid_price', 'fc_sale_price', 'nod_noi_sent_date', 'nod_noi_expire_date',
        ]
        read_only_fields = ['asset_hub', 'crm_details']
    
    def get_crm_details(self, obj):
        """Get legal contact for this asset via AssetCRMContact junction."""
        try:
            contact_link = obj.asset_hub.crm_contacts.filter(role='legal').first()
            if contact_link:
                return MasterCRMSerializer(contact_link.crm).data
        except Exception:
            pass
        return None

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
            'dil_completion_date', 'dil_cost', 'cfk_cost',
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
            'acceptable_min_offer', 'short_sale_date',
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
            'modification_date', 'modification_cost', 'modification_upb',
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
        fields = ['id', 'asset_hub', 'asset_hub_id', 'reo_outcome', 'task_type', 'task_started', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure the reo_outcome belongs to same hub (safety)
        reo = attrs.get('reo_outcome')
        hub = attrs.get('asset_hub')
        if reo and hub and reo.asset_hub_id != hub.id:
            raise serializers.ValidationError('REO outcome and asset_hub mismatch.')
        task_type = attrs.get('task_type') or getattr(self.instance, 'task_type', None)
        if hub and task_type:
            qs = REOtask.objects.filter(asset_hub=hub, task_type=task_type)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('A task with this type already exists for this asset.')
        return attrs


# -----------------------------
# REO Scope/Bid Serializer
# -----------------------------

class REOScopeSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = REOScope
        fields = [
            'id',
            'asset_hub', 'asset_hub_id',
            'scope_kind', 'reo_task',
            'scope_date', 'total_cost', 'expected_completion', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # Mirror model.clean() basic checks at serializer level for clearer API errors
        hub = attrs.get('asset_hub')
        reo_task = attrs.get('reo_task')
        if reo_task and hub and reo_task.asset_hub_id != hub.id:
            raise serializers.ValidationError('Linked REO task must reference the same AssetIdHub.')
        if reo_task and reo_task.task_type not in ('trashout', 'renovation'):
            raise serializers.ValidationError('Linked REO task must be type Trashout or Renovation.')
        if scope_kind and reo_task and scope_kind != reo_task.task_type:
            raise serializers.ValidationError('Scope kind must match the linked REO task type.')
        return attrs

    def create(self, validated_data: Dict[str, Any]):
        """Create REOScope while converting Django ValidationError to DRF ValidationError.

        Model.save() calls full_clean(), which raises DjangoValidationError. DRF only formats
        serializers.ValidationError nicely, so we translate here to produce a 400 with details
        instead of a 500.
        """
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            detail = getattr(e, 'message_dict', None) or getattr(e, 'messages', None) or str(e)
            raise serializers.ValidationError(detail)

    def update(self, instance, validated_data: Dict[str, Any]):
        """Update REOScope with the same error translation for consistency."""
        try:
            return super().update(instance, validated_data)
        except DjangoValidationError as e:
            detail = getattr(e, 'message_dict', None) or getattr(e, 'messages', None) or str(e)
            raise serializers.ValidationError(detail)


class FCTaskSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = FCTask
        fields = ['id', 'asset_hub', 'asset_hub_id', 'fc_sale', 'task_type', 'task_started', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        fc_sale = attrs.get('fc_sale')
        hub = attrs.get('asset_hub')
        if fc_sale and hub and fc_sale.asset_hub_id != hub.id:
            raise serializers.ValidationError('FCSale outcome and asset_hub mismatch.')
        task_type = attrs.get('task_type') or getattr(self.instance, 'task_type', None)
        if hub and task_type:
            qs = FCTask.objects.filter(asset_hub=hub, task_type=task_type)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('A task with this type already exists for this asset.')
        return attrs


class DILTaskSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = DILTask
        fields = ['id', 'asset_hub', 'asset_hub_id', 'dil', 'task_type', 'task_started', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        dil = attrs.get('dil')
        hub = attrs.get('asset_hub')
        if dil and hub and dil.asset_hub_id != hub.id:
            raise serializers.ValidationError('DIL outcome and asset_hub mismatch.')
        task_type = attrs.get('task_type') or getattr(self.instance, 'task_type', None)
        if hub and task_type:
            qs = DILTask.objects.filter(asset_hub=hub, task_type=task_type)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('A task with this type already exists for this asset.')
        return attrs


class ShortSaleTaskSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = ShortSaleTask
        fields = ['id', 'asset_hub', 'asset_hub_id', 'short_sale', 'task_type', 'task_started', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        ss = attrs.get('short_sale')
        hub = attrs.get('asset_hub')
        if ss and hub and ss.asset_hub_id != hub.id:
            raise serializers.ValidationError('ShortSale outcome and asset_hub mismatch.')
        task_type = attrs.get('task_type') or getattr(self.instance, 'task_type', None)
        if hub and task_type:
            qs = ShortSaleTask.objects.filter(asset_hub=hub, task_type=task_type)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('A task with this type already exists for this asset.')
        return attrs


class ModificationTaskSerializer(serializers.ModelSerializer):
    asset_hub_id = _AssetHubPKField()

    class Meta:
        model = ModificationTask
        fields = ['id', 'asset_hub', 'asset_hub_id', 'modification', 'task_type', 'task_started', 'created_at', 'updated_at']
        read_only_fields = ['id', 'asset_hub', 'created_at', 'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        m = attrs.get('modification')
        hub = attrs.get('asset_hub')
        if m and hub and m.asset_hub_id != hub.id:
            raise serializers.ValidationError('Modification outcome and asset_hub mismatch.')
        task_type = attrs.get('task_type') or getattr(self.instance, 'task_type', None)
        if hub and task_type:
            qs = ModificationTask.objects.filter(asset_hub=hub, task_type=task_type)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('A task with this type already exists for this asset.')
        return attrs
