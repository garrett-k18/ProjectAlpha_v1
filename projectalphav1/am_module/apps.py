from django.apps import AppConfig


class AmModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'am_module'
    
    def ready(self):
        """
        WHAT: Registers Django signals when app is ready.
        WHY: Signals need to be connected after models are loaded.
        HOW: Import signals module to trigger @receiver decorators.
        """
        # WHAT: Import signals module
        # WHY: This triggers the @receiver decorators to connect signals
        # HOW: Import at app ready time
        import am_module.signals  # noqa: F401