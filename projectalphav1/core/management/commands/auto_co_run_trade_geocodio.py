"""
Management command: trigger Geocod.io enrichment for a specific trade (and optional seller).

WHAT:
    - Provides a simple CLI wrapper around `core.services.geocoding.geocode_markers_for_seller_trade`.
    - Populates `LlDataEnrichment` with coordinates and MSA metadata using Geocod.io's census field append.
WHY:
    - Eliminates the need to craft long `manage.py shell -c` snippets.
    - Keeps operational workflows consistent with other commands (e.g., `import_msa_data`).
DOCS REVIEWED:
    - Django custom commands: https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/
    - Geocod.io Python client: https://pygeocodio.readthedocs.io/en/latest/geocode.html
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from acq_module.models.model_acq_seller import SellerRawData
from core.services.geocoding import geocode_markers_for_seller_trade


class Command(BaseCommand):
    """
    WHAT: Run Geocod.io enrichment for a specific trade.
    WHY:  Allows ops to refresh MSA/coordinate data on demand per trade.
    HOW:  Looks up all unique sellers in the trade, calls the geocoding service for each.
    DOCS: Geocod.io Python client: https://pygeocodio.readthedocs.io/en/latest/geocode.html
    """

    help = "Run Geocod.io enrichment for all SellerRawData rows in a trade."

    def add_arguments(self, parser) -> None:
        """
        WHAT: Register CLI arguments for trade selection.
        WHY:  Follow Django command conventions.
        """

        parser.add_argument(
            "trade_id",
            type=int,
            help="Trade ID whose SellerRawData addresses should be geocoded.",
        )

    def handle(self, *args, **options) -> None:
        """
        WHAT: Command entry point executed by Django.
        WHY:  Simple wrapper to call geocode_markers_for_seller_trade.
        HOW:  Fetches all unique sellers for the trade, processes each separately.
        """

        trade_id: int = options["trade_id"]

        # WHAT: Verify trade exists in database.
        # WHY: Fail fast if trade_id is invalid.
        exists = SellerRawData.objects.filter(trade_id=trade_id).exists()
        if not exists:
            raise CommandError(f"No SellerRawData rows found for trade {trade_id}.")

        # WHAT: Get all unique sellers for this trade.
        # WHY: geocode_markers_for_seller_trade expects (seller_id, trade_id) pair.
        sellers = list(
            SellerRawData.objects
            .filter(trade_id=trade_id)
            .values_list("seller_id", flat=True)
            .order_by("seller_id")
            .distinct("seller_id")
        )

        self.stdout.write(
            self.style.NOTICE(
                f"Starting Geocod.io enrichment for trade {trade_id} "
                f"({len(sellers)} unique seller(s))"
            )
        )

        total_markers = 0
        api_hits = 0
        
        for seller_id in sellers:
            self.stdout.write(f"  Seller {seller_id}...", ending=" ")
            self.stdout.flush()
            
            payload = geocode_markers_for_seller_trade(
                seller_id=seller_id,
                trade_id=trade_id,
            )
            count = payload.get("count", 0) or 0
            source = payload.get("source", "none")
            error = payload.get("error")
            
            total_markers += count
            if source == "api":
                api_hits += 1
            
            if error:
                self.stdout.write(self.style.ERROR(f"ERROR: {error}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"{count} markers ({source})"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone: trade {trade_id}, {len(sellers)} sellers, "
                f"{total_markers} total markers, {api_hits} API calls"
            )
        )

