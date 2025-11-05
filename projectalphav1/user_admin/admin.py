from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from datetime import timedelta
from django.utils import timezone

from .models.externalauth import BrokerTokenAuth, BrokerPortalToken
from .models.user_profile import UserProfile


@admin.register(BrokerTokenAuth)
class BrokerTokenAuthAdmin(admin.ModelAdmin):
    """Admin for broker invite tokens.

    Columns and filters are chosen to quickly find active tokens per broker/SRD.
    Docs: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/
    """

    # List columns shown in the changelist view
    list_display = (
        "token",
        "broker",
        "seller_raw_data",
        "expires_at",
        "used_at",
        "single_use",
        "created_at",
    )

    # Sidebar filters
    list_filter = ("single_use", "used_at", "expires_at", "broker")

    # Search across token string, broker name/email, and SRD id
    search_fields = (
        "token",
        "broker__broker_name",
        "broker__broker_email",
        "seller_raw_data__id",
    )

    # Default ordering: newest first
    ordering = ("-created_at",)
    
    # Exclude token from the add/change form; it will be auto-generated on save
    exclude = ("token",)
    list_per_page = 5

    def get_changeform_initial_data(self, request):
        """Provide sensible defaults on the add form.

        - expires_at: now + 15 days
        - single_use: True
        Docs: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_changeform_initial_data
        """
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("expires_at", timezone.now() + timedelta(days=15))
        initial.setdefault("single_use", True)
        return initial

    def save_model(self, request, obj: BrokerTokenAuth, form, change):
        """Auto-generate a unique token and default expiry if not provided.

        Avoids the need for a DB migration to add model-level defaults while
        keeping admin UX simple.
        Docs: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.save_model
        """
        # Generate token if missing
        if not obj.token:
            token = BrokerTokenAuth.generate_token()
            while BrokerTokenAuth.objects.filter(token=token).exists():
                token = BrokerTokenAuth.generate_token()
            obj.token = token

        # Default expiration to 15 days if not given
        if not obj.expires_at:
            obj.expires_at = timezone.now() + timedelta(days=15)

        super().save_model(request, obj, form, change)


@admin.register(BrokerPortalToken)
class BrokerPortalTokenAdmin(admin.ModelAdmin):
    """Admin for broker portal tokens (single URL per broker)."""

    list_display = (
        "token",
        "broker",
        "expires_at",
        "created_at",
    )
    list_filter = (
        "broker",
        "expires_at",
    )
    search_fields = (
        "token",
        "broker__broker_name",
        "broker__broker_email",
    )
    ordering = ("-created_at",)
    exclude = ("token",)
    list_per_page = 5

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("expires_at", timezone.now() + timedelta(days=15))
        return initial

    def save_model(self, request, obj: BrokerPortalToken, form, change):
        if not obj.token:
            token = BrokerPortalToken.generate_token()
            while BrokerPortalToken.objects.filter(token=token).exists():
                token = BrokerPortalToken.generate_token()
            obj.token = token

        if not obj.expires_at:
            obj.expires_at = timezone.now() + timedelta(days=15)

        super().save_model(request, obj, form, change)

