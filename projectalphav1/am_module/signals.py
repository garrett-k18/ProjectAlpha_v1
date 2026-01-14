"""AM module signal registration.

This module is imported by am_module.apps.AmModuleConfig.ready() to ensure
all @receiver handlers are registered.
"""

import am_module.sig_note_summary  # noqa: F401
import am_module.sig_asset_class  # noqa: F401

