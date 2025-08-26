"""
Legacy upload path helpers used by historical migrations.

We keep these here to decouple them from models/valuations.py, while
valuations.py re-exports their names to preserve the historical dotted path
(e.g., acq_module.models.valuations.get_broker_photo_path) required by older
migrations. See Django docs on migrations "Serializing values".
"""

import os
from datetime import datetime


def get_broker_photo_path(instance, filename):
    """Legacy helper referenced by old migrations.

    Delegates to unified path under 'photos/'.
    Expected legacy instance has attribute 'broker_valuation' with seller_raw_data.
    """
    srd = getattr(instance, 'broker_valuation', None)
    srd = getattr(srd, 'seller_raw_data', None)
    if srd is None:
        # Fallback for safety if called unexpectedly
        return os.path.join('photos', 'unknown', 'unknown', filename)
    seller_id = srd.seller.id
    trade_id = srd.trade.id
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"
    return os.path.join('photos', str(seller_id), str(trade_id), new_filename)


def get_public_photo_path(instance, filename):
    """Legacy helper referenced by old migrations.

    Delegates to unified path under 'photos/'.
    """
    seller_id = instance.seller_raw_data.seller.id
    trade_id = instance.seller_raw_data.trade.id
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}{ext}"
    return os.path.join('photos', str(seller_id), str(trade_id), new_filename)


def get_document_photo_path(instance, filename):
    """Legacy helper referenced by old migrations.

    Delegates to unified path under 'photos/' and appends page suffix if present.
    """
    seller_id = instance.seller_raw_data.seller.id
    trade_id = instance.seller_raw_data.trade.id
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(filename)
    page_suffix = f"_p{instance.page_number}" if getattr(instance, 'page_number', None) else ""
    new_filename = f"{name}_{timestamp}{page_suffix}{ext}"
    return os.path.join('photos', str(seller_id), str(trade_id), new_filename)
