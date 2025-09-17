# This file makes Python treat the directory as a package

"""
am_module.models package initializer

Important: Django only imports the package `am_module.models` by default, not
each module within it. To ensure Django discovers all model classes declared
in split files (e.g., `seller_boarded_data.py`, `asset_metrics.py`), we must
import those modules here so they are loaded during app initialization.

Docs reviewed:
- App loading: https://docs.djangoproject.com/en/stable/ref/applications/
- Model discovery: https://docs.djangoproject.com/en/stable/topics/db/models/
"""

# Explicitly import model modules so Django registers their model classes.
from .boarded_data import SellerBoardedData, BlendedOutcomeModel  # noqa: F401
from .asset_metrics import AssetMetrics  # noqa: F401
from .am_data import AMMetrics, AMMetricsChange, AMNote, REOData  # noqa: F401
