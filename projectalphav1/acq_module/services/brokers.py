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

from core.models.model_co_crm import MasterCRM
from ..models.model_acq_seller import SellerRawData
from core.models.valuations import Valuation
from user_admin.models import BrokerTokenAuth


def get_broker_stats_dict(broker: MasterCRM) -> Dict[str, int]:
    """Return counts for invites, distinct assigned assets, and submissions.

    Args:
        broker: A `MasterCRM` instance (already fetched by the caller).

    Returns:
        A dict with keys: total_invites, assigned_loan_count, submissions_count
    
    WHAT: Hub-first architecture - all queries through AssetIdHub
    WHY: Consistent with project's hub-first join strategy
    HOW: Filter by asset_hub_id instead of seller_raw_data_id
    """
    total_invites = BrokerTokenAuth.objects.filter(broker_id=broker.id).count()

    # WHAT: Latest tokens per asset for DISTINCT ON (PostgreSQL)
    # WHY: One token per asset hub (not per SRD - they're 1:1 anyway)
    # HOW: PostgreSQL DISTINCT ON asset_hub_id with -created_at ordering
    assigned_qs = (
        BrokerTokenAuth.objects.filter(broker_id=broker.id)
        .order_by("asset_hub_id", "-created_at")
        .distinct("asset_hub_id")
    )
    assigned_loan_count = assigned_qs.count()

    # WHAT: Count distinct asset_hub_id values for broker submissions
    # WHY: Use values().distinct() to avoid PostgreSQL DISTINCT ON ordering conflicts with .count()
    # HOW: Filter through hub's broker_tokens reverse relation
    submissions_count = (
        Valuation.objects.filter(
            source='broker',
            asset_hub__broker_tokens__broker_id=broker.id
        )
        .values("asset_hub_id")
        .distinct()
        .count()
    )

    return {
        "total_invites": total_invites,
        "assigned_loan_count": assigned_loan_count,
        "submissions_count": submissions_count,
    }


def list_latest_tokens_for_broker(broker: MasterCRM) -> QuerySet[BrokerTokenAuth]:
    """Return a queryset of the latest token per asset for the given broker.

    WHAT: Hub-first query - uses asset_hub instead of seller_raw_data
    WHY: All joins go through AssetIdHub intentionally
    HOW: PostgreSQL DISTINCT ON asset_hub_id, access ACQ data via asset_hub__acq_raw
    """
    return (
        BrokerTokenAuth.objects.filter(broker_id=broker.id)
        .select_related("asset_hub__acq_raw", "asset_hub__acq_raw__seller", "asset_hub__acq_raw__trade")
        .order_by("asset_hub_id", "-created_at")
        .distinct("asset_hub_id")
    )


def list_assigned_loan_entries(broker: MasterCRM) -> List[Dict[str, Any]]:
    """Build a list of assigned asset entries for UI consumption.

    WHAT: Hub-first architecture - returns asset hub IDs and ACQ data
    WHY: All joins happen through AssetIdHub intentionally
    HOW: Access SellerRawData via asset_hub.acq_raw reverse relation
    
    Each entry includes asset_hub_id, minimal seller/trade info, address, an optional
    current_balance field (stringified), latest token info, and a submission flag.
    """
    latest_tokens = list_latest_tokens_for_broker(broker)

    # WHAT: Precompute which asset hub IDs have a broker Valuation row
    # WHY: Avoid N+1 queries when marking has_submission
    # HOW: Collect all hub IDs, filter Valuations, return as set
    hub_ids = [t.asset_hub_id for t in latest_tokens]
    submitted_ids = set(
        Valuation.objects.filter(source='broker', asset_hub_id__in=hub_ids)
        .values_list("asset_hub_id", flat=True)
    )

    results: List[Dict[str, Any]] = []
    for invite in latest_tokens:
        # WHAT: Access SellerRawData via hub's acq_raw reverse relation
        # WHY: Hub-first architecture - all domain data accessed through hub
        # HOW: invite.asset_hub.acq_raw gives us the SellerRawData instance
        srd: SellerRawData = invite.asset_hub.acq_raw
        results.append(
            {
                # WHAT: Return asset_hub_id as primary identifier (same value as srd.id since srd uses hub as PK)
                # WHY: Hub-first - frontend should reference by hub ID
                # HOW: Use asset_hub_id; keep "seller_raw_data" key for backward compat
                "seller_raw_data": invite.asset_hub_id,  # Same as srd.id (hub is PK)
                "asset_hub_id": invite.asset_hub_id,
                # WHAT: Include sellertape_id for display in broker portal
                # WHY: Brokers need to see the actual loan number, not just hub ID
                # HOW: Extract from SellerRawData.sellertape_id field
                "loan_number": srd.sellertape_id,
                "seller": {"id": srd.seller_id, "name": getattr(srd.seller, "name", None)},
                "trade": {"id": srd.trade_id, "name": getattr(srd.trade, "trade_name", None)},
                "address": {
                    "street_address": srd.street_address,
                    "city": srd.city,
                    "state": srd.state,
                    "zip": srd.zip,
                },
                # WHAT: Stringify decimal if present; use getattr for safety in schema changes
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
                "has_submission": invite.asset_hub_id in submitted_ids,
            }
        )

    return results
