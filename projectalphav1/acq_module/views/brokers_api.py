"""
Broker detail and assigned-loans API endpoints.

Docs reviewed:
- Django ORM: https://docs.djangoproject.com/en/5.0/topics/db/queries/
- DRF function-based views: https://www.django-rest-framework.org/api-guide/views/

These endpoints expose Broker directory details (from `acq_module.Brokercrm`) and
list loans (SellerRawData) assigned to a broker via `user_admin.BrokerTokenAuth`.
Assignments are inferred from tokens with a non-null `broker` FK.
"""
from typing import List, Dict, Any

from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..models import Brokercrm, SellerRawData, BrokerValues
from user_admin.models import BrokerTokenAuth


@api_view(["GET"])  # Keep open for internal UI consistency; can be gated later
@permission_classes([AllowAny])
def broker_detail(request, broker_id: int):
    """Return basic broker directory info and quick stats.

    Args:
        request: DRF request object (unused here but standard signature)
        broker_id: Primary key of `acq_module.Brokercrm`

    Returns:
        JSON payload with broker fields and counts useful for UI header.
    """
    # Fetch the canonical broker directory entry or 404 if not found
    broker = get_object_or_404(Brokercrm, pk=broker_id)

    # Count invites (tokens) that explicitly reference this broker
    total_invites = BrokerTokenAuth.objects.filter(broker_id=broker_id).count()

    # Distinct loans assigned via tokens -> count unique SellerRawData
    # Using PostgreSQL's DISTINCT ON pattern: order then distinct by seller_raw_data
    assigned_qs = (
        BrokerTokenAuth.objects.filter(broker_id=broker_id)
        .order_by("seller_raw_data_id", "-created_at")
        .distinct("seller_raw_data_id")
    )
    assigned_loan_count = assigned_qs.count()

    # Count how many of those loans have BrokerValues submitted
    submissions_count = (
        BrokerValues.objects.filter(
            seller_raw_data__broker_tokens__broker_id=broker_id
        )
        .distinct("seller_raw_data_id")
        .count()
    )

    data = {
        "id": broker.id,
        "broker_name": broker.broker_name,
        "broker_email": broker.broker_email,
        "broker_firm": broker.broker_firm,
        "broker_city": broker.broker_city,
        "broker_state": broker.broker_state,
        "stats": {
            "total_invites": total_invites,
            "assigned_loan_count": assigned_loan_count,
            "submissions_count": submissions_count,
        },
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])  # Keep open for internal UI; adjust permissions as needed
@permission_classes([AllowAny])
def list_assigned_loans(request, broker_id: int):
    """List loans (SellerRawData) assigned to a broker via tokens.

    We resolve the latest token per loan for the broker and include basic loan
    context plus token status and whether any `BrokerValues` were submitted.

    Args:
        request: DRF request
        broker_id: Brokercrm primary key

    Returns:
        JSON with `results`: list of assigned loan entries
    """
    # Confirm broker exists for clearer error if not
    get_object_or_404(Brokercrm, pk=broker_id)

    # Latest token per loan for this broker (PostgreSQL DISTINCT ON usage)
    latest_tokens = (
        BrokerTokenAuth.objects.filter(broker_id=broker_id)
        .select_related(
            "seller_raw_data",
            "seller_raw_data__seller",
            "seller_raw_data__trade",
        )
        .order_by("seller_raw_data_id", "-created_at")
        .distinct("seller_raw_data_id")
    )

    results: List[Dict[str, Any]] = []
    # Optionally prefetch which SRD ids have BrokerValues for quick lookup
    srd_ids = [t.seller_raw_data_id for t in latest_tokens]
    submitted_ids = set(
        BrokerValues.objects.filter(seller_raw_data_id__in=srd_ids)
        .values_list("seller_raw_data_id", flat=True)
    )

    for token in latest_tokens:
        srd: SellerRawData = token.seller_raw_data
        results.append(
            {
                # Core identifiers
                "seller_raw_data": srd.id,
                "seller": {
                    "id": srd.seller_id,
                    "name": getattr(srd.seller, "name", None),
                },
                "trade": {
                    "id": srd.trade_id,
                    "name": getattr(srd.trade, "trade_name", None),
                },
                # Address context commonly needed in UI
                "address": {
                    "street_address": srd.street_address,
                    "city": srd.city,
                    "state": srd.state,
                    "zip": srd.zip,
                },
                # Financial snapshot field commonly surfaced
                "current_balance": str(srd.current_balance) if srd.current_balance is not None else None,
                # Token context and status flags
                "token": {
                    "value": token.token,
                    "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                    "single_use": token.single_use,
                    "used_at": token.used_at.isoformat() if token.used_at else None,
                    "is_expired": token.is_expired,
                    "is_used": token.is_used,
                },
                # Whether any values were submitted by a broker for this SRD
                "has_submission": srd.id in submitted_ids,
            }
        )

    return Response({"results": results}, status=status.HTTP_200_OK)
