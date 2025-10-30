"""
Unified Valuation API (backwards-compatible surface for existing internal endpoint).

This endpoint supports ALL valuation sources via a `source` query parameter
(defaults to 'internal'). It reads/writes the unified core.models.valuations.Valuation
model and preserves legacy field names for compatibility while also exposing
neutral field names.

Docs reviewed:
- DRF API Views: https://www.django-rest-framework.org/api-guide/views/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- Django get_object_or_404: https://docs.djangoproject.com/en/5.0/topics/http/shortcuts/
"""
from decimal import Decimal, InvalidOperation
from typing import Optional
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers

from ..models.seller import SellerRawData
from core.models.valuations import Valuation


class ValuationCompatSerializer(serializers.Serializer):
    """Back-compat serializer that supports both neutral and legacy alias fields.

    Write: accepts either neutral names (asis_value, arv_value, value_date, rehab_est_total)
    or legacy alias names (internal_uw_* or broker_*). If both are provided, neutral wins.

    Read: returns both neutral fields and legacy alias fields for the requested source.
    """
    # Context fields
    seller_raw_data = serializers.IntegerField(read_only=True)
    source = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Neutral fields (preferred)
    asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    value_date = serializers.DateField(required=False, allow_null=True)
    rehab_est_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    # Detailed rehab estimates
    roof_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    kitchen_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    bath_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    flooring_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    windows_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    appliances_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    plumbing_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    electrical_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    landscaping_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    links = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    # Legacy internal aliases
    internal_uw_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_uw_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_uw_value_date = serializers.DateField(required=False, allow_null=True)
    internal_rehab_est_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    # Legacy broker aliases
    broker_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_rehab_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_value_date = serializers.DateField(required=False, allow_null=True)
    broker_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_links = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    def to_representation(self, instance: Optional[Valuation]):
        if instance is None:
            return {}
        data = {
            "source": instance.source,
            "asis_value": instance.asis_value,
            "arv_value": instance.arv_value,
            "value_date": instance.value_date,
            "rehab_est_total": getattr(instance, 'rehab_est_total', None),
            # Detailed rehab estimates
            "roof_est": getattr(instance, 'roof_est', None),
            "kitchen_est": getattr(instance, 'kitchen_est', None),
            "bath_est": getattr(instance, 'bath_est', None),
            "flooring_est": getattr(instance, 'flooring_est', None),
            "windows_est": getattr(instance, 'windows_est', None),
            "appliances_est": getattr(instance, 'appliances_est', None),
            "plumbing_est": getattr(instance, 'plumbing_est', None),
            "electrical_est": getattr(instance, 'electrical_est', None),
            "landscaping_est": getattr(instance, 'landscaping_est', None),
            "notes": getattr(instance, 'notes', None),
            "links": getattr(instance, 'links', None),
        }
        # Add legacy aliases per source for UI compatibility
        if instance.source == 'internal':
            data.update({
                "internal_uw_asis_value": instance.asis_value,
                "internal_uw_arv_value": instance.arv_value,
                "internal_uw_value_date": instance.value_date,
                "internal_rehab_est_total": getattr(instance, 'rehab_est_total', None),
            })
        elif instance.source == 'broker':
            data.update({
                "broker_asis_value": instance.asis_value,
                "broker_arv_value": instance.arv_value,
                "broker_value_date": instance.value_date,
                "broker_rehab_est": getattr(instance, 'rehab_est_total', None),
                "broker_notes": getattr(instance, 'notes', None),
                "broker_links": getattr(instance, 'links', None),
            })
        return data

    def validated_neutral(self) -> dict:
        """Map incoming data (neutral or legacy aliases) to neutral field dict."""
        v = self.validated_data
        # Prefer neutral keys; fallback to aliases
        return {
            'asis_value': v.get('asis_value', v.get('internal_uw_asis_value', v.get('broker_asis_value'))),
            'arv_value': v.get('arv_value', v.get('internal_uw_arv_value', v.get('broker_arv_value'))),
            'value_date': v.get('value_date', v.get('internal_uw_value_date', v.get('broker_value_date'))),
            'rehab_est_total': v.get('rehab_est_total', v.get('internal_rehab_est_total', v.get('broker_rehab_est'))),
            # Detailed rehab estimates
            'roof_est': v.get('roof_est'),
            'kitchen_est': v.get('kitchen_est'),
            'bath_est': v.get('bath_est'),
            'flooring_est': v.get('flooring_est'),
            'windows_est': v.get('windows_est'),
            'appliances_est': v.get('appliances_est'),
            'plumbing_est': v.get('plumbing_est'),
            'electrical_est': v.get('electrical_est'),
            'landscaping_est': v.get('landscaping_est'),
            'notes': v.get('notes', v.get('broker_notes')),
            'links': v.get('links', v.get('broker_links')),
        }


@api_view(['GET', 'PATCH', 'PUT'])
@permission_classes([AllowAny])
def internal_valuation_view(request, seller_id: int | str):
    """Backwards-compatible endpoint for valuation by SellerRawData id.

    URL: /api/acq/valuations/internal/<seller_id>/?source=<internal|broker|third_party|seller|appraisal>
    Defaults to source=internal for backwards compatibility.
    """
    srd = get_object_or_404(SellerRawData, pk=seller_id)
    ser_cls = ValuationCompatSerializer
    # Pick source (default internal)
    source = (request.query_params.get('source') or 'internal').strip().lower()
    if source not in {s for s, _ in Valuation.Source.choices}:
        source = 'internal'

    if request.method == 'GET':
        # Find latest valuation for hub/source
        obj = (
            Valuation.objects.filter(asset_hub=srd.asset_hub, source=source)
            .order_by('-value_date', '-created_at')
            .first()
        )
        data = ser_cls().to_representation(obj) if obj else {}
        data.update({
            'seller_raw_data': srd.asset_hub_id,
            'source': source,
        })
        return Response(data, status=status.HTTP_200_OK)

    # Write path
    ser = ser_cls(data=request.data or {})
    ser.is_valid(raise_exception=True)
    incoming = ser.validated_neutral()

    # Map incoming -> unified Valuation neutral fields
    asis_value = incoming.get('asis_value')
    arv_value = incoming.get('arv_value')
    value_date = incoming.get('value_date')
    rehab_total = incoming.get('rehab_est_total')
    notes = incoming.get('notes')
    links = incoming.get('links')

    # Upsert strategy by (asset_hub, source, value_date). If date missing, update latest or create new.
    lookup = {
        'asset_hub': srd.asset_hub,
        'source': source,
        'value_date': value_date,
    }
    defaults = {
        'asis_value': asis_value,
        'arv_value': arv_value,
        'rehab_est_total': rehab_total,
        # Detailed rehab estimates
        'roof_est': incoming.get('roof_est'),
        'kitchen_est': incoming.get('kitchen_est'),
        'bath_est': incoming.get('bath_est'),
        'flooring_est': incoming.get('flooring_est'),
        'windows_est': incoming.get('windows_est'),
        'appliances_est': incoming.get('appliances_est'),
        'plumbing_est': incoming.get('plumbing_est'),
        'electrical_est': incoming.get('electrical_est'),
        'landscaping_est': incoming.get('landscaping_est'),
        'notes': notes,
        'links': links,
    }

    if lookup['value_date'] is None:
        obj = (
            Valuation.objects
            .filter(asset_hub=srd.asset_hub, source=source)
            .order_by('-value_date', '-created_at')
            .first()
        )
        if obj:
            for k, v in defaults.items():
                if v is not None:
                    setattr(obj, k, v)
            obj.save()
        else:
            # Only pass non-None defaults to avoid unintended nulls
            clean_defaults = {k: v for k, v in defaults.items() if v is not None}
            obj = Valuation.objects.create(asset_hub=srd.asset_hub, source=source, **clean_defaults)
    else:
        obj, _ = Valuation.objects.update_or_create(defaults=defaults, **lookup)

    out = ser_cls().to_representation(obj)
    out.update({
        'seller_raw_data': srd.asset_hub_id,
        'source': source,
    })
    return Response(out, status=status.HTTP_200_OK)


class ValuationCompatSerializer(serializers.Serializer):
    """Back-compat serializer that supports both neutral and legacy alias fields.

    Write: accepts either neutral names (asis_value, arv_value, value_date, rehab_est_total)
    or legacy alias names (internal_uw_* or broker_*). If both are provided, neutral wins.

    Read: returns both neutral fields and legacy alias fields for the requested source.
    """
    # Context fields
    seller_raw_data = serializers.IntegerField(read_only=True)
    source = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Neutral fields (preferred)
    asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    value_date = serializers.DateField(required=False, allow_null=True)
    rehab_est_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    links = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    # Legacy internal aliases
    internal_uw_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_uw_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_uw_value_date = serializers.DateField(required=False, allow_null=True)
    internal_rehab_est_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    # Legacy broker aliases
    broker_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_rehab_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_value_date = serializers.DateField(required=False, allow_null=True)
    broker_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_links = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    def to_representation(self, instance: Optional[Valuation]):
        if instance is None:
            return {}
        data = {
            "source": instance.source,
            "asis_value": instance.asis_value,
            "arv_value": instance.arv_value,
            "value_date": instance.value_date,
            "rehab_est_total": getattr(instance, 'rehab_est_total', None),
            "notes": getattr(instance, 'notes', None),
            "links": getattr(instance, 'links', None),
        }
        # Add legacy aliases per source for UI compatibility
        if instance.source == 'internal':
            data.update({
                "internal_uw_asis_value": instance.asis_value,
                "internal_uw_arv_value": instance.arv_value,
                "internal_uw_value_date": instance.value_date,
                "internal_rehab_est_total": getattr(instance, 'rehab_est_total', None),
            })
        elif instance.source == 'broker':
            data.update({
                "broker_asis_value": instance.asis_value,
                "broker_arv_value": instance.arv_value,
                "broker_value_date": instance.value_date,
                "broker_rehab_est": getattr(instance, 'rehab_est_total', None),
                "broker_notes": getattr(instance, 'notes', None),
                "broker_links": getattr(instance, 'links', None),
            })
        return data

    def validated_neutral(self) -> dict:
        """Map incoming data (neutral or legacy aliases) to neutral field dict."""
        v = self.validated_data
        # Prefer neutral keys; fallback to aliases
        return {
            'asis_value': v.get('asis_value', v.get('internal_uw_asis_value', v.get('broker_asis_value'))),
            'arv_value': v.get('arv_value', v.get('internal_uw_arv_value', v.get('broker_arv_value'))),
            'value_date': v.get('value_date', v.get('internal_uw_value_date', v.get('broker_value_date'))),
            'rehab_est_total': v.get('rehab_est_total', v.get('internal_rehab_est_total', v.get('broker_rehab_est'))),
            'notes': v.get('notes', v.get('broker_notes')),
            'links': v.get('links', v.get('broker_links')),
        }


@api_view(['GET', 'PATCH', 'PUT'])
@permission_classes([AllowAny])
def internal_valuation_view(request, seller_id: int | str):
    """Backwards-compatible endpoint for valuation by SellerRawData id.

    URL: /api/acq/valuations/internal/<seller_id>/?source=<internal|broker|third_party|seller|appraisal>
    Defaults to source=internal for backwards compatibility.

    GET:
      - Returns the latest valuation for the requested source (by value_date then created_at), else nulls.

    PATCH/PUT:
      - Upserts the valuation row for the hub and source (keyed by date). If date is missing, updates latest or creates new.
    """
    srd = get_object_or_404(SellerRawData, pk=seller_id)
    ser_cls = ValuationCompatSerializer
    # Pick source (default internal)
    source = (request.query_params.get('source') or 'internal').strip().lower()
    if source not in {s for s, _ in Valuation.Source.choices}:
        source = 'internal'

    if request.method == 'GET':
        # Find latest valuation for hub/source
        obj = (
            Valuation.objects.filter(asset_hub=srd.asset_hub, source=source)
            .order_by('-value_date', '-created_at')
            .first()
        )
        data = ser_cls().to_representation(obj) if obj else {}
        data.update({
            'seller_raw_data': srd.asset_hub_id,
            'source': source,
        })
        return Response(data, status=status.HTTP_200_OK)

    # Write path
    ser = ser_cls(data=request.data or {})
    ser.is_valid(raise_exception=True)
    incoming = ser.validated_neutral()

    # Map incoming -> unified Valuation neutral fields
    asis_value = incoming.get('asis_value')
    arv_value = incoming.get('arv_value')
    value_date = incoming.get('value_date')
    rehab_total = incoming.get('rehab_est_total')
    notes = incoming.get('notes')
    links = incoming.get('links')

    # Upsert strategy by (asset_hub, source, value_date). If date missing, update latest or create new.
    lookup = {
        'asset_hub': srd.asset_hub,
        'source': source,
        'value_date': value_date,
    }
    defaults = {
        'asis_value': asis_value,
        'arv_value': arv_value,
        'rehab_est_total': rehab_total,
        'notes': notes,
        'links': links,
    }

    if lookup['value_date'] is None:
        obj = (
            Valuation.objects
            .filter(asset_hub=srd.asset_hub, source=source)
            .order_by('-value_date', '-created_at')
            .first()
        )
        if obj:
            for k, v in defaults.items():
                if v is not None:
                    setattr(obj, k, v)
            obj.save()
        else:
            # Only pass non-None defaults to avoid unintended nulls
            clean_defaults = {k: v for k, v in defaults.items() if v is not None}
            obj = Valuation.objects.create(asset_hub=srd.asset_hub, source=source, **clean_defaults)
    else:
        obj, _ = Valuation.objects.update_or_create(defaults=defaults, **lookup)

    out = ser_cls().to_representation(obj)
    out.update({
        'seller_raw_data': srd.asset_hub_id,
        'source': source,
    })
    return Response(out, status=status.HTTP_200_OK)
