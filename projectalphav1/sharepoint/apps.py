from django.apps import AppConfig


class SharepointConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sharepoint'
    verbose_name = 'SharePoint Integration'
    
    def ready(self):
        """Import signals when app is ready"""
        import sharepoint.sig_sharepoint_folderTempCreate

