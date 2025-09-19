"""
Shared broker-related query helpers used by multiple API endpoints.

Plain-language overview:
- This module centralizes the database queries for broker pages so that
  both internal/admin endpoints and public/token endpoints can reuse the
  exact same logic without duplicating code.
- Nothing in here depends on Django REST Framework; it's pure ORM logic.
- Views import and call these helpers and then format HTTP responses.

Docs reviewed:
- Django ORM: https://docs.djangoproject.com/en/5.0/topics/db/queries/
"""
from typing import List, Dict, Any, Tuple

from django.db.models import QuerySet

from core.models.crm import Brokercrm
from ..models.seller import SellerRawData
from core.models.valuations import Valuation
from user_admin.models import BrokerTokenAuth


def get_broker_stats_dict(broker: Brokercrm) -> Dict[str, int]:
    """Return counts for invites, distinct assigned loans, and submissions.

    Args:
        broker: A `Brokercrm` instance (already fetched by the caller).

    Returns:
        A dict with keys: total_invites, assigned_loan_count, submissions_count
    """
    total_invites = BrokerTokenAuth.objects.filter(broker_id=broker.id).count()

    # Latest tokens per loan for DISTINCT ON (PostgreSQL)
    assigned_qs = (
        BrokerTokenAuth.objects.filter(broker_id=broker.id)
        .order_by("seller_raw_data_id", "-created_at")
        .distinct("seller_raw_data_id")
    )
    assigned_loan_count = assigned_qs.count()

    submissions_count = (
        Valuation.objects.filter(
            source='broker',
            asset_hub__acq_raw__broker_tokens__broker_id=broker.id
        )
        .distinct("asset_hub_id")
        .count()
    )

    return {
        "total_invites": total_invites,
        "assigned_loan_count": assigned_loan_count,
        "submissions_count": submissions_count,
    }


def list_latest_tokens_for_broker(broker: Brokercrm) -> QuerySet[BrokerTokenAuth]:
    """Return a queryset of the latest token per loan for the given broker.

    Uses PostgreSQL DISTINCT ON by ordering and then calling distinct on
    seller_raw_data_id.
    """
    return (
        BrokerTokenAuth.objects.filter(broker_id=broker.id)
        .select_related("seller_raw_data", "seller_raw_data__seller", "seller_raw_data__trade")
        .order_by("seller_raw_data_id", "-created_at")
        .distinct("seller_raw_data_id")
    )


def list_assigned_loan_entries(broker: Brokercrm) -> List[Dict[str, Any]]:
    """Build a list of assigned loan entries for UI consumption.

    Each entry includes SRD id, minimal seller/trade info, address, an optional
    current_balance field (stringified), latest token info, and a submission flag.
    """
    latest_tokens = list_latest_tokens_for_broker(broker)

    # Precompute which SRD ids have a broker Valuation row
    srd_ids = [t.seller_raw_data_id for t in latest_tokens]
    submitted_ids = set(
        Valuation.objects.filter(source='broker', asset_hub__acq_raw_id__in=srd_ids)
        .values_list("asset_hub__acq_raw_id", flat=True)
    )

    results: List[Dict[str, Any]] = []
    for invite in latest_tokens:
        srd: SellerRawData = invite.seller_raw_data
        results.append(
            {
                "seller_raw_data": srd.id,
                "seller": {"id": srd.seller_id, "name": getattr(srd.seller, "name", None)},
                "trade": {"id": srd.trade_id, "name": getattr(srd.trade, "trade_name", None)},
                "address": {
                    "street_address": srd.street_address,
                    "city": srd.city,
                    "state": srd.state,
                    "zip": srd.zip,
                },
                # Stringify decimal if present; use getattr for safety in schema changes
                "current_balance": (
                    str(getattr(srd, "current_balance", None))
                    if getattr(srd, "current_balance", None) is not None
                    else None
                ),
                "token": {
                    "value": invite.token,
                    "expires_at": invite.expires_at.isoformat() if invite.expires_at else None,
                    "single_use": invite.single_use,
                    "used_at": invite.used_at.isoformat() if invite.used_at else None,
                    "is_expired": invite.is_expired,
                    "is_used": invite.is_used,
                },
                "has_submission": srd.id in submitted_ids,
            }
        )

    return results
