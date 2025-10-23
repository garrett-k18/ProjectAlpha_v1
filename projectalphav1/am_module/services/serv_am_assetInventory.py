"""
Service layer for composing Asset Inventory data for AM Module.

WHAT: Centralized business logic for asset inventory data preparation and enrichment
WHY: Separate data access/computation from serialization to improve testability and maintainability
HOW: Provide QuerySet building, data enrichment, and computed field resolution

Docs reviewed:
- Django QuerySet API: https://docs.djangoproject.com/en/stable/ref/models/querysets/
- DRF Filtering & Pagination: https://www.django-rest-framework.org/api-guide/filtering/
- Django Performance Optimization: https://docs.djangoproject.com/en/stable/topics/db/optimization/

This module isolates data-join logic and business rules so views and serializers remain thin.
"""
from __future__ import annotations

from typing import Iterable, Optional
from django.db.models import QuerySet, Q, F
from acq_module.models.seller import SellerRawData  # WHAT: Post-refactor boarded dataset source per docs (https://docs.djangoproject.com/en/stable/topics/db/models/)
from am_module.models.am_data import AMMetrics
from am_module.models.servicers import ServicerLoanData
from core.models.valuations import Valuation

# Fields used by quick filter 'q'
QUICK_FILTER_FIELDS = (
    "street_address",
    "city",
    "state",
    "zip",
    "seller__name",  # WHAT: Map friendly seller_name search to SellerRawData->Seller join
    "trade__trade_name",  # WHAT: Surfaced trade name via ForeignKey per Django join docs
)

# WHAT: Set of Valuation.source strings used by asset inventory
# WHY: Constrain valuation queries to only relevant sources for better performance
VALUATION_SOURCES = {
    'internalInitialUW',
    'seller',
}

# NOTE on ordering:
"""
Frontend may request ordering on any visible column. We expose a permissive
ordering strategy that passes unknown fields through directly to Django ORM so
long as they exist on the base model or related joins. We only translate a
couple of user-friendly aliases to actual DB fields.

Special cases:
- asset_id -> sellertape_id (friendly alias)
- hold_days -> asset_hub__created_at (proxy; monotonic inverse)
"""


def build_queryset(
    *,
    q: Optional[str] = None,
    filters: Optional[dict] = None,
    ordering: Optional[str] = None,
) -> QuerySet[SellerRawData]:
    """
    Return a QuerySet of SellerRawData (boarded assets) with optimized joins.

    WHAT: Build optimized queryset with all necessary joins and annotations
    WHY: Centralize query optimization to avoid N+1 queries across the application
    HOW: Use select_related for ForeignKey joins, annotate for computed fields

    Args:
        q: Quick search text applied across multiple fields
        filters: Dict of column filters (state, asset_status, seller_name, etc.)
        ordering: Comma-separated list of fields to order by (supports - prefix for desc)

    Returns:
        QuerySet of SellerRawData instances ready for serialization
    """
    qs = (
        SellerRawData.objects
        .filter(acq_status=SellerRawData.AcquisitionStatus.BOARD)  # WHAT: Limit to assets promoted into AM module
        .select_related("asset_hub")
        .select_related("asset_hub__blended_outcome_model")
        .select_related("asset_hub__ammetrics")  # WHAT: Join AMMetrics for delinquency status
        .select_related("seller", "trade")  # HOW: ensure seller/trade names resolve without extra queries
        .annotate(
            seller_name=F("seller__name"),  # WHAT: Expose friendly name aliases to match legacy serializer fields
            trade_name=F("trade__trade_name"),
        )
    )

    if q:
        q_obj = Q()
        for f in QUICK_FILTER_FIELDS:
            q_obj |= Q(**{f"{f}__icontains": q})
        # Also try to match numeric sellertape_id if q is digits per legacy UX contract
        if q.isdigit():
            q_obj |= Q(sellertape_id__icontains=q)
        qs = qs.filter(q_obj)

    if filters:
        # Shallow equality filters; extend as needed
        allowed = {}
        for key, value in filters.items():
            if value in (None, ""):
                continue
            if key == "seller_name":
                allowed["seller__name"] = value
            elif key == "trade_name":
                allowed["trade__trade_name"] = value
            elif key == "lifecycle_status":
                allowed["asset_hub__asset_status"] = value
            else:
                allowed[key] = value
        if allowed:
            qs = qs.filter(**allowed)

    if ordering:
        # Support multiple comma-separated fields
        order_fields: list[str] = []
        for part in str(ordering).split(","):
            part = part.strip()
            if not part:
                continue
            desc = part.startswith("-")
            key = part[1:] if desc else part

            # Translate friendly aliases to actual ORM paths
            if key == "asset_id":
                model_field = "sellertape_id"
            elif key == "hold_days":
                # Fallback to hub created_at when legacy metrics table is unavailable
                model_field = "asset_hub__created_at"
            else:
                model_field = key  # pass-through for any other field

            order_fields.append(f"-{model_field}" if desc else model_field)

        if order_fields:
            qs = qs.order_by(*order_fields)

    return qs


class AssetInventoryEnricher:
    """
    Enriches SellerRawData objects with computed fields for asset inventory display.

    WHAT: Service class that adds computed/aggregated fields to asset objects
    WHY: Separate business logic from serialization for better testability and reusability
    HOW: Cache expensive lookups (valuations) and provide helper methods for computed fields

    Usage:
        enricher = AssetInventoryEnricher()
        for asset in queryset:
            enricher.enrich(asset)
        # Now asset has _computed_* attributes
    """

    def __init__(self):
        """Initialize enricher with empty valuation cache."""
        # WHAT: Per-batch cache mapping asset_hub_id -> {source: Valuation}
        # WHY: Reusing the latest valuation per source avoids N x sources queries
        # HOW: Populated lazily on first valuation lookup for an asset
        self._valuation_cache: dict[int | str, dict[str, Valuation]] = {}

    def enrich(self, obj: SellerRawData) -> SellerRawData:
        """
        Add computed attributes to a SellerRawData instance.

        WHAT: Attach computed fields as _computed_* attributes on the object
        WHY: Allows serializer to access these via source='_computed_*' without business logic
        HOW: Call individual computation methods and cache results on the object

        Args:
            obj: SellerRawData instance to enrich

        Returns:
            Same object with added _computed_* attributes
        """
        # Basic computed fields
        obj._computed_asset_id = self.get_asset_id(obj)
        obj._computed_lifecycle_status = self.get_lifecycle_status(obj)
        obj._computed_delinquency_status = self.get_delinquency_status(obj)
        obj._computed_seller_name = self.get_seller_name(obj)
        obj._computed_trade_name = self.get_trade_name(obj)

        # Servicer data
        obj._computed_servicer_loan_data = self.get_servicer_loan_data(obj)

        # Valuation fields
        obj._computed_internal_initial_uw_asis_value = self.get_internal_initial_uw_asis_value(obj)
        obj._computed_internal_initial_uw_arv_value = self.get_internal_initial_uw_arv_value(obj)
        obj._computed_seller_asis_value = self.get_seller_asis_value(obj)
        obj._computed_seller_arv_value = self.get_seller_arv_value(obj)
        obj._computed_latest_uw_value = self.get_latest_uw_value(obj)

        return obj

    def enrich_queryset(self, qs: QuerySet[SellerRawData]) -> Iterable[SellerRawData]:
        """
        Enrich all objects in a queryset (generator for memory efficiency).

        WHAT: Iterate through queryset and enrich each object
        WHY: Provides generator interface for large datasets without loading all into memory
        HOW: Yield enriched objects one at a time, maintaining valuation cache across all

        Args:
            qs: QuerySet of SellerRawData objects

        Yields:
            Enriched SellerRawData instances
        """
        for obj in qs:
            yield self.enrich(obj)

    # ========== Basic Computed Fields ==========

    def get_asset_id(self, obj: SellerRawData) -> int | str | None:
        """
        Return display asset ID (sellertape_id or pk fallback).

        WHAT: Provide user-facing asset identifier
        WHY: Frontend displays this as the primary asset ID
        HOW: Prefer sellertape_id if available, fallback to pk
        """
        stid = getattr(obj, "sellertape_id", None)
        return stid if stid is not None else getattr(obj, "pk", None)

    def get_lifecycle_status(self, obj: SellerRawData) -> str | None:
        """
        Return the canonical lifecycle status stored on AssetIdHub.

        WHAT: Provide a friendly accessor for UI dropdowns that edit lifecycle state
        WHY: Asset status now lives on the hub so acquisitions/AM modules stay in sync
        HOW: Prefer the explicit hub field; fallback to legacy asset_status column for transitional data
        """
        hub = getattr(obj, 'asset_hub', None)
        if hub is not None:
            value = getattr(hub, 'asset_status', None)
            if value:
                return value
        return getattr(obj, 'asset_status', None)

    def get_delinquency_status(self, obj: SellerRawData) -> str | None:
        """
        Return the cached delinquency bucket from AMMetrics for this asset.

        WHAT: Expose denormalized delinquency status field
        WHY: Avoid recomputing the bucket on every serializer call (expensive calculation)
        HOW: Read from AMMetrics table which is refreshed by nightly jobs

        Note: Upstream nightly jobs (or manual refreshes) should call
        AMMetrics.refresh_delinquency_status() whenever new servicer data arrives
        so that this field stays in sync.
        """
        # Resolve hub from the row
        hub = getattr(obj, 'asset_hub', None)
        if not hub:
            return None

        # WHAT: Access AMMetrics (NOT deprecated AssetMetrics) via 'ammetrics' related name
        # WHY: AMMetrics uses ForeignKey with related_name='ammetrics' (see am_module.models.am_data line 57)
        # HOW: hub.ammetrics is a reverse ForeignKey manager; if select_related was used, access directly
        try:
            metrics = getattr(hub, 'ammetrics', None)
            if metrics is None:
                return None
            return getattr(metrics, 'delinquency_status', None)
        except AttributeError:
            return None

    def get_seller_name(self, obj: SellerRawData) -> str | None:
        """
        Return seller display name from annotation or FK fallback.

        WHAT: Get seller name for display
        WHY: Frontend displays seller in grid columns
        HOW: Check if queryset added annotation first (faster), fallback to FK traversal

        Docs: https://docs.djangoproject.com/en/stable/ref/models/instances/#django.db.models.Model.refresh_from_db
        """
        annotated = getattr(obj, 'seller_name', None)
        if annotated:
            return annotated
        seller = getattr(obj, 'seller', None)
        return getattr(seller, 'name', None)

    def get_trade_name(self, obj: SellerRawData) -> str | None:
        """
        Return trade display name from annotation or FK fallback.

        WHAT: Get trade name for display
        WHY: Frontend displays trade in grid columns and filters
        HOW: Check if queryset added annotation first (faster), fallback to FK traversal
        """
        annotated = getattr(obj, 'trade_name', None)
        if annotated:
            return annotated
        trade = getattr(obj, 'trade', None)
        return getattr(trade, 'trade_name', None)

    # ========== Servicer Data ==========

    def get_servicer_loan_data(self, obj: SellerRawData) -> ServicerLoanData | None:
        """
        Fetch and return the most recent ServicerLoanData record by asset_hub.

        WHAT: Get latest servicer loan snapshot
        WHY: Frontend displays current loan balance, payment status, etc.
        HOW: Query ServicerLoanData ordered by reporting period descending
        """
        # Resolve asset_hub consistently (obj may be an AssetIdHub or any model with asset_hub FK)
        hub = getattr(obj, 'asset_hub', None) or obj
        latest_servicer_record = (
            ServicerLoanData.objects
            .filter(asset_hub=hub)
            .order_by('-reporting_year', '-reporting_month', '-as_of_date')
            .first()
        )
        return latest_servicer_record

    # ========== Valuation Lookup Helpers ==========

    def _latest_val_by_source(self, obj: SellerRawData, source: str) -> Valuation | None:
        """
        Return latest Valuation row for the object's asset_hub and given source.

        WHAT: Fetch most recent valuation record for a specific source (internal, seller, etc.)
        WHY: Multiple valuation sources exist per asset; need to get latest for each
        HOW: Use per-batch cache to avoid repeated queries, order by value_date then created_at

        Args:
            obj: SellerRawData instance
            source: Valuation source string (e.g., 'internalInitialUW', 'seller')

        Returns:
            Latest Valuation instance for that source, or None if not found
        """
        hub = getattr(obj, 'asset_hub', None)
        if hub is None:
            return None  # WHAT: No hub means no valuations, short-circuit to prevent unnecessary work

        cache_key = getattr(hub, 'id', None) or getattr(obj, 'pk', None)
        if cache_key is None:
            return None  # WHAT: Without a stable id we cannot cache, so we cannot safely proceed

        asset_cache = self._valuation_cache.get(cache_key)
        if asset_cache is None:
            # WHAT: Batch-fetch all valuations for this asset across required sources once
            # WHY: Eliminates per-field database round-trips that caused pagination latency (~10s)
            # HOW: Order ensures first occurrence per source is the latest record
            # Docs: https://docs.djangoproject.com/en/stable/ref/models/querysets/#order-by
            queryset = (
                Valuation.objects
                .filter(asset_hub=hub, source__in=VALUATION_SOURCES)
                .order_by('-value_date', '-created_at')
            )
            asset_cache = {}
            for valuation in queryset:
                asset_cache.setdefault(valuation.source, valuation)
            self._valuation_cache[cache_key] = asset_cache

        return asset_cache.get(source)

    # ========== Internal Initial UW Valuation ==========

    def get_internal_initial_uw_asis_value(self, obj: SellerRawData):
        """Get as-is value from Internal Initial UW valuation source."""
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'asis_value', None) if v else None

    def get_internal_initial_uw_arv_value(self, obj: SellerRawData):
        """Get ARV value from Internal Initial UW valuation source."""
        v = self._latest_val_by_source(obj, 'internalInitialUW')
        return getattr(v, 'arv_value', None) if v else None

    # ========== Seller Valuation ==========

    def get_seller_asis_value(self, obj: SellerRawData):
        """Get as-is value from Seller valuation source."""
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'asis_value', None) if v else None

    def get_seller_arv_value(self, obj: SellerRawData):
        """Get ARV value from Seller valuation source."""
        v = self._latest_val_by_source(obj, 'seller')
        return getattr(v, 'arv_value', None) if v else None

    # ========== Latest UW Value (Prioritized) ==========

    def get_latest_uw_value(self, obj: SellerRawData):
        """
        Return the most recent as-is valuation across priority sources.

        WHAT: Provide single "latest underwriting value" for display
        WHY: Frontend needs one canonical value to show in summary cards
        HOW: Iterate through valuation sources ordered by underwriting relevance,
             return first non-null as-is value

        Priority order:
        1. Internal Initial UW (most recent internal underwriting)
        2. Seller (fallback if no internal UW available)
        """
        # WHAT: Iterate through valuation sources ordered by underwriting relevance
        # WHY: Internal Initial UW valuations should take precedence over seller values
        for source in ('internalInitialUW', 'seller'):
            valuation = self._latest_val_by_source(obj, source)
            # HOW: Only return when an as-is value exists to prevent None propagation
            if valuation and getattr(valuation, 'asis_value', None) is not None:
                return valuation.asis_value
        # WHERE: Default to None when no valuation carries an as-is value
        return None
