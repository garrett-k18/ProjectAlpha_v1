"""Django AppConfig for the acquisitions module.

This file is responsible for runtime configuration of the `acq_module` Django
app. In particular, we use `AppConfig.ready()` to import and register
signal handlers (e.g., post_save hooks) once Django has finished loading
installed apps. Keeping signal hookup here centralizes side-effect wiring and
avoids accidental imports in random modules.

Docs reviewed:
- Django AppConfig: https://docs.djangoproject.com/en/5.2/ref/applications/
- Signals best practices: avoid heavy work in signal modules; only connect here
"""

from django.apps import AppConfig


class AcqModuleConfig(AppConfig):
    """Runtime configuration for `acq_module`.

    - Sets the default auto field
    - Wires up signal handlers in `ready()` (import-time side effects only)
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'acq_module'

    def ready(self) -> None:
        """Connect signal handlers for this app.

        We import `acq_module.signals` here so that any `@receiver` decorators
        are executed and signal handlers (like our SellerRawData post-save
        geocoding trigger) get registered exactly once per process.

        The import is wrapped in a try/except to be defensive during certain
        runtime situations (e.g., optional deps not installed in migrations),
        but in normal operation it should succeed silently.
        """
        try:
            # Import only for side effects (signal connection); attribute unused.
            from . import signals  # noqa: F401
        except Exception:
            # Avoid crashing Django on import issues; signals are best-effort.
            pass
        return super().ready()
