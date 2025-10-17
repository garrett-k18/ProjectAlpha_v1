from django.http import JsonResponse  # WHAT: Django helper for JSON responses returned to Vue clients
from rest_framework.decorators import api_view  # WHAT: DRF decorator enabling function-based API views
from rest_framework import status  # WHAT: HTTP status code constants for clarity
from ..models.seller import Trade  # WHAT: Trade model storing lifecycle status we need to mutate


def _serialize_choices():
    """Return Trade.Status choices as value/label dictionaries for UI consumption."""
    # WHAT: iterate over TextChoices pairs to build JSON-safe objects understood by dropdowns
    return [{"value": value, "label": label} for value, label in Trade.Status.choices]


@api_view(["GET"])  # WHY: ensure only safe reads hit this endpoint per DRF docs @api_view usage
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
    if trade.status != new_status:
        trade.status = new_status  # WHAT: stage assignment when status actually changed
        trade.save(update_fields=["status", "updated_at"])  # WHY: persist only touched columns for efficiency
    return JsonResponse(
        {
            "trade_id": trade.id,  # WHAT: echo id for clients synchronizing state
            "status": trade.status,  # WHAT: return final value after potential update
            "options": _serialize_choices(),  # WHAT: resend options so client stays aligned
        }
    )
