"""
Broker portal endpoints: assign brokers in batch and serve a single broker portal URL.

Responsibilities:
- Internal batch assignment from AG Grid to a single broker (creates multiple invites)
- Maintain/return a single reusable portal token per broker (non-expired)
- Public portal fetch by portal token to show active invites
- Separation of concerns: single-invite flows live in `invites.py`; internal non-portal
  broker reads live in `internal.py`

Endpoints provided here:
- POST /api/acq/broker-portal/assign/      -> assign_broker_batch (internal)
- GET  /api/acq/broker-portal/<token>/     -> broker_portal_detail (public)

Docs reviewed:
- DRF Views/Permissions/Serializers
  https://www.django-rest-framework.org/api-guide/views/
  https://www.django-rest-framework.org/api-guide/permissions/
  https://www.django-rest-framework.org/api-guide/serializers/
- Django ORM queries
  https://docs.djangoproject.com/en/5.0/topics/db/queries/
"""
from datetime import timedelta
from typing import List

from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # TODO: tighten to IsAuthenticated for internal endpoints
from rest_framework.response import Response
from rest_framework import status, serializers

from ...models.model_acq_seller import SellerRawData
from core.models.valuations import Valuation
from core.models.crm import MasterCRM
from ...services.brokers import list_assigned_loan_entries
from user_admin.models import BrokerTokenAuth
from user_admin.models.externalauth import BrokerPortalToken


class AssignBrokerSerializer(serializers.Serializer):
    broker_id = serializers.IntegerField()
    seller_raw_data_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    # Optional overrides
    expires_in_hours = serializers.IntegerField(required=False)  # invites default
    portal_expires_in_hours = serializers.IntegerField(required=False)  # portal default


@api_view(["POST"])  # internal use; open for now
@permission_classes([AllowAny])
def assign_broker_batch(request):
    """Assign a broker to many SellerRawData rows and create tokens.

    Body:
    {
      "broker_id": 123,
      "seller_raw_data_ids": [1,2,3],
      "expires_in_hours": 360,            # optional, default 360 (15 days)
      "portal_expires_in_hours": 360      # optional, default 360 (15 days)
    }

    Behavior:
    - Ensure a valid (non-expired) portal token exists for the broker; create if needed.
    - For each SRD id provided, create a new BrokerTokenAuth token linked to broker.
    - Return portal token info and created invites summary.
    """
    serializer = AssignBrokerSerializer(data=request.data or {})
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    broker: MasterCRM = get_object_or_404(MasterCRM, pk=data["broker_id"]) 
    srd_ids: List[int] = data["seller_raw_data_ids"]

    invite_hours = int(data.get("expires_in_hours") or 360)
    portal_hours = int(data.get("portal_expires_in_hours") or 360)

    # Ensure a valid portal token exists (latest non-expired or create new)
    now = timezone.now()
    portal = (
        BrokerPortalToken.objects.filter(broker=broker, expires_at__gt=now)
        .order_by("-created_at")
        .first()
    )
    if not portal:
        # create new portal token
        token = BrokerPortalToken.generate_token()
        while BrokerPortalToken.objects.filter(token=token).exists():
            token = BrokerPortalToken.generate_token()
        portal = BrokerPortalToken.objects.create(
            broker=broker,
            token=token,
            expires_at=now + timedelta(hours=portal_hours),
        )

    # Create invites per SRD
    invites = []
    for srd_id in srd_ids:
        srd = get_object_or_404(SellerRawData, pk=srd_id)
        token = BrokerTokenAuth.generate_token()
        while BrokerTokenAuth.objects.filter(token=token).exists():
            token = BrokerTokenAuth.generate_token()
        invite = BrokerTokenAuth.objects.create(
            seller_raw_data=srd,
            broker=broker,
            token=token,
            expires_at=now + timedelta(hours=invite_hours),
            # Portal invites must be multi-use until expiration
            single_use=False,
        )
        invites.append(
            {
                "seller_raw_data": invite.seller_raw_data_id,
                "token": invite.token,
                "expires_at": invite.expires_at.isoformat(),
            }
        )

    return Response(
        {
            "portal": {
                "token": portal.token,
                "expires_at": portal.expires_at.isoformat(),
                "url": f"/brokerview/{portal.token}",
            },
            "invites": invites,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])  # public broker portal endpoint
@permission_classes([AllowAny])
def broker_portal_detail(request, token: str):
    """Return broker portal context and active invites by portal token.

    Response 200:
    {
      "valid": true,
      "broker": {"id": ..., "broker_name": ..., "broker_email": ..., "broker_firm": ...},
      "expires_at": "ISO",
      "active_invites": [ entries... ]
    }

    404 if token not found; 400 if expired.
    """
    try:
        portal = BrokerPortalToken.objects.select_related("broker").get(token=token)
    except BrokerPortalToken.DoesNotExist:
        return Response({"valid": False, "reason": "not_found"}, status=status.HTTP_404_NOT_FOUND)

    if portal.is_expired:
        return Response({"valid": False, "reason": "expired", "expires_at": portal.expires_at.isoformat()}, status=status.HTTP_400_BAD_REQUEST)

    broker = portal.broker

    # Build entries using shared service
    entries = list_assigned_loan_entries(broker)

    # Enrich with any saved broker Valuation so the UI can prefill even if the invite
    # is expired/used. This preserves previously submitted values in the portal.
    srd_ids = [e.get("seller_raw_data") for e in entries if e.get("seller_raw_data") is not None]
    # Map broker Valuation by SellerRawData id via hub: select_related to traverse hub -> acq_raw
    values_by_srd = {}
    for bv in (
        Valuation.objects
        .select_related("asset_hub__acq_raw")
        .filter(asset_hub__acq_raw_id__in=srd_ids, source='broker')
        .order_by('-value_date', '-created_at')
    ):
        raw = getattr(bv.asset_hub, 'acq_raw', None)
        if raw is not None:
            values_by_srd[raw.id] = bv

    enriched_entries = []
    for e in entries:
        srd_id = e.get("seller_raw_data")
        bv = values_by_srd.get(srd_id)
        if bv:
            e = {
                **e,
                "values": {
                    # Back-compat keys mapped from unified Valuation
                    "broker_asis_value": str(getattr(bv, 'asis_value', None)) if getattr(bv, 'asis_value', None) is not None else None,
                    "broker_arv_value": str(getattr(bv, 'arv_value', None)) if getattr(bv, 'arv_value', None) is not None else None,
                    "broker_rehab_est": str(getattr(bv, 'rehab_est_total', None)) if getattr(bv, 'rehab_est_total', None) is not None else None,
                    "broker_value_date": getattr(bv, 'value_date', None).isoformat() if getattr(bv, 'value_date', None) else None,
                    "broker_notes": getattr(bv, "notes", None),
                },
            }
        enriched_entries.append(e)

    # Filter to active invites for submission ability
    # Requirement: Portal invites remain usable until expiration, regardless of prior submissions.
    active_entries = [
        e for e in enriched_entries
        if not e["token"]["is_expired"]
    ]

    return Response(
        {
            "valid": True,
            "broker": {
                "id": broker.id,
                "broker_name": broker.broker_name,
                "broker_email": broker.broker_email,
                "broker_firm": broker.broker_firm,
            },
            "expires_at": portal.expires_at.isoformat(),
            # Active invites allow saving (contain valid token)
            "active_invites": active_entries,
            # Assigned entries include latest per SRD regardless of token status,
            # enriched with any saved values to display after submission/expiry.
            "assigned_entries": enriched_entries,
        },
        status=status.HTTP_200_OK,
    )
