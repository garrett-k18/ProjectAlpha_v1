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

    WHAT: Hub-first architecture - displays asset_hub instead of seller_raw_data
    WHY: All joins happen through AssetIdHub intentionally
    Columns and filters are chosen to quickly find active tokens per broker/asset hub.
    Docs: https://docs.djangoproject.com/en/5.0/ref/contrib/admin/
    """

    # List columns shown in the changelist view
    list_display = (
        "token",
        "broker",
        "asset_hub",  # Hub-first: renamed from seller_raw_data
        "expires_at",
        "used_at",
        "single_use",
        "created_at",
    )

    # Sidebar filters
    list_filter = ("single_use", "used_at", "expires_at", "broker")

    # WHAT: Search across token string, broker name/email, and asset hub id
    # WHY: Hub-first architecture
    # HOW: MasterCRM uses contact_name and email (not broker_name/broker_email)
    search_fields = (
        "token",
        "broker__contact_name",  # MasterCRM field
        "broker__email",         # MasterCRM field
        "asset_hub__id",         # Hub-first: renamed from seller_raw_data__id
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
    # WHAT: Search by token and broker contact info
    # WHY: MasterCRM uses contact_name and email fields
    # HOW: Update to use correct MasterCRM field names
    search_fields = (
        "token",
        "broker__contact_name",  # MasterCRM field (not broker_name)
        "broker__email",         # MasterCRM field (not broker_email)
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


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin for UserProfile model
    Includes must_change_password field for managing temporary passwords
    """
    
    # List columns shown in the changelist view
    list_display = (
        'user',
        'job_title',
        'department',
        'access_level',
        'must_change_password',  # Show if user needs to change password
        'created_at',
    )
    
    # Sidebar filters
    list_filter = (
        'must_change_password',  # Filter by users who need to change password
        'access_level',
        'department',
        'created_at',
    )
    
    # Search fields
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'job_title',
        'department',
    )
    
    # Fields to display in the form
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('job_title', 'department', 'phone_number', 'profile_picture')
        }),
        ('Access & Preferences', {
            'fields': ('access_level', 'theme_preference', 'notification_enabled')
        }),
        ('Password Management', {
            'fields': ('must_change_password',),
            'description': 'Set to True when creating a user with a temporary password. User will be required to change password on first login.'
        }),
    )
    
    # Default ordering
    ordering = ('-created_at',)
    
    # Read-only fields (check if fields exist to avoid errors)
    readonly_fields = ('created_at', 'updated_at') if hasattr(UserProfile, '_meta') and 'created_at' in [f.name for f in UserProfile._meta.get_fields()] else ()


# Inline admin for UserProfile to show in User admin
class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile
    Allows editing user profile directly from User admin page
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    
    # Fields to display in the inline form
    fieldsets = (
        ('Profile Details', {
            'fields': ('job_title', 'department', 'phone_number', 'profile_picture')
        }),
        ('Access & Preferences', {
            'fields': ('access_level', 'theme_preference', 'notification_enabled')
        }),
        ('Password Management', {
            'fields': ('must_change_password',),
            'description': 'Set to True when creating a user with a temporary password. User will be required to change password on first login.'
        }),
    )


# Unregister default User admin and register custom one with inline
# Only unregister if User is already registered
if admin.site.is_registered(User):
    admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with UserProfile inline
    Allows setting must_change_password when creating users with temporary passwords
    """
    inlines = (UserProfileInline,)
    
    def save_model(self, request, obj, form, change):
        """
        Override save to handle must_change_password flag
        When creating a new user, if must_change_password is set in the inline,
        it will be saved automatically via the inline save
        """
        super().save_model(request, obj, form, change)

