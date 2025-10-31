from django.http import JsonResponse  # WHAT: Django helper for JSON responses returned to Vue clients
from django.views.decorators.csrf import ensure_csrf_cookie  # WHAT: forces CSRF cookie issuance on GET (docs: https://docs.djangoproject.com/en/5.1/ref/csrf/)
from django.db import transaction  # WHAT: ensure atomic updates across trade + asset rows (docs: https://docs.djangoproject.com/en/stable/topics/db/transactions/)
from rest_framework.decorators import api_view  # WHAT: DRF decorator enabling function-based API views
from rest_framework import status  # WHAT: HTTP status code constants for clarity
from ..models.model_acq_seller import Trade, SellerRawData  # WHAT: Trade drives lifecycle; SellerRawData holds per-asset acquisition status used by AM module


def _serialize_choices():
    """Return Trade.Status choices as value/label dictionaries for UI consumption."""
    # WHAT: iterate over TextChoices pairs to build JSON-safe objects understood by dropdowns
    return [{"value": value, "label": label} for value, label in Trade.Status.choices]


@api_view(["GET"])  # WHY: ensure only safe reads hit this endpoint per DRF docs @api_view usage
@ensure_csrf_cookie  # WHY: guarantees csrftoken cookie for subsequent POSTs from SPA per Django CSRF docs
def get_trade_status(request, trade_id: int):
    """Fetch the persisted trade status plus available options for selector rendering."""
    try:
        trade = Trade.objects.get(pk=trade_id)  # WHAT: load target trade row by primary key
    except Trade.DoesNotExist:
        # WHY: return 404 when supplied trade_id is invalid so UI can handle missing trades
        return JsonResponse({"detail": "Trade not found"}, status=status.HTTP_404_NOT_FOUND)
    return JsonResponse(
        {
            "trade_id": trade.id,  # WHAT: echo trade id so store can verify payload association
            "status": trade.status,  # WHAT: current lifecycle flag stored on the Trade model
            "options": _serialize_choices(),  # WHAT: full dropdown list so UI stays in sync with server
        }
    )


@api_view(["POST", "PUT"])  # WHY: allow both POST and PUT per DRF @api_view docs for write operations
def update_trade_status(request, trade_id: int):
    """Persist a new trade status value after validating against the TextChoices list."""
    try:
        trade = Trade.objects.get(pk=trade_id)  # WHAT: retrieve target trade for mutation
    except Trade.DoesNotExist:
        # WHY: consumer sent an invalid trade id; respond with 404 to prevent silent failures
        return JsonResponse({"detail": "Trade not found"}, status=status.HTTP_404_NOT_FOUND)
    # WHAT: DRF Request.data already parsed JSON; guard against non-dict payloads before lookup
    new_status = request.data.get("status") if isinstance(request.data, dict) else None
    if not new_status:
        # WHY: notify caller they must provide a value so UI can display validation errors
        return JsonResponse({"detail": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
    valid_values = {value for value, _ in Trade.Status.choices}  # WHAT: build set for O(1) membership check
    if new_status not in valid_values:
        # WHY: reject values outside enum to prevent corrupting status data
        return JsonResponse({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    assets_modified = 0  # WHAT: track how many SellerRawData rows we synchronize for observability/debugging
    if trade.status != new_status:
        with transaction.atomic():  # WHY: ensure trade + related asset updates commit together
            trade.status = new_status  # WHAT: stage assignment when status actually changed
            trade.save(update_fields=["status", "updated_at"])  # WHY: persist only touched columns for efficiency
            assets_modified = _sync_asset_acq_statuses(trade, new_status)  # WHAT: align SellerRawData.acq_status with lifecycle terminal states
    return JsonResponse(
        {
            "trade_id": trade.id,  # WHAT: echo id for clients synchronizing state
            "status": trade.status,  # WHAT: return final value after potential update
            "options": _serialize_choices(),  # WHAT: resend options so client stays aligned
            "assets_modified": assets_modified,  # WHAT: expose count so UI logs/test suites can assert synchronization occurred
        }
    )


def _sync_asset_acq_statuses(trade: Trade, new_status: str) -> int:
    """Synchronize `SellerRawData.acq_status` values with the trade lifecycle when toggling terminal states.

    WHAT: Asset Management now queries `SellerRawData` directly (docs: see AM refactor PR) and expects BOARD assets to surface there.
    WHY: Without this mapping, updating the trade to BOARD via the UI would leave SellerRawData rows AWARDED/DD so AM grids show zero results.
    HOW: Translate relevant trade statuses to acquisition statuses and bulk update related rows while avoiding unnecessary writes.
    """

    status_map = {
        Trade.Status.BOARD: SellerRawData.AcquisitionStatus.BOARD,
        Trade.Status.PASS: SellerRawData.AcquisitionStatus.PASS,
        Trade.Status.AWARDED: SellerRawData.AcquisitionStatus.AWARDED,
        Trade.Status.DD: SellerRawData.AcquisitionStatus.DD,
    }

    target_acq_status = status_map.get(new_status)
    if not target_acq_status:
        return 0  # WHAT: No-op for statuses we do not mirror (e.g., INDICATIVE)

    # WHY: Use queryset update per Django docs for efficient bulk mutation while skipping rows already aligned
    return trade.seller_raw_data.exclude(acq_status=target_acq_status).update(acq_status=target_acq_status)
