"""Django signal handlers for the acquisitions module.

This module is intentionally small and declarative. It connects lightweight
signal receivers that forward work to dedicated logic/service modules. This
keeps models thin and avoids performing network I/O inside model.save().

Currently implemented:
    - Post-save hook for `SellerRawData`: triggers geocoding after the DB
      transaction commits by calling `logic.geocoding_logic.geocode_row`.
      The logic layer persists results to `LlDataEnrichment` so future
      requests reuse coordinates without hitting external APIs.
"""

from __future__ import annotations

from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver

from .models.seller import SellerRawData
from .logic.geocoding_logic import geocode_row


@receiver(post_save, sender=SellerRawData)
def sellerrawdata_post_save(sender, instance: SellerRawData, created: bool, **kwargs):
    """Post-save receiver for `SellerRawData`.

    Behavior:
    - Only fires enrichment when a row is freshly created (`created is True`).
    - Schedules geocoding with `transaction.on_commit` to ensure we run outside
      the current DB transaction (avoids slow writes / retries on rollbacks).
    - Delegates to `geocode_row(instance.pk)` which handles "DB -> cache -> API"
      resolution and persists coordinates to `LlDataEnrichment`.

    This signal is best-effort; failures are swallowed to avoid impacting
    the write-path for ingest flows.
    """
    if not created:
        return

    def _do_geocode():
        try:
            geocode_row(instance.pk)
        except Exception:
            # Fail silently; geocoding is a best-effort enrichment
            pass

    # Prefer after-commit execution to avoid network I/O inside DB tx
    try:
        transaction.on_commit(_do_geocode)
    except Exception:
        # Fallback: run immediately if on_commit is unavailable (edge envs)
        _do_geocode()
