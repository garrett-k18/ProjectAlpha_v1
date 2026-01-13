## File Purpose:
## This file contains the models for the AM tracks and tasks.
## It is used to store the tracks and tasks for the AM module.
## 


from __future__ import annotations

from datetime import date

from django.apps import apps
from django.db import models
from django.utils import timezone


def _audit_log_model():
    return apps.get_model('am_module', 'AuditLog')


class REOData(models.Model):
    """Data about a REO property."""

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='reo_data',
        help_text='1:1 with hub; REO data keyed by AssetIdHub.',
    )

    # Note: CRM contacts are now managed via AssetCRMContact junction model
    # Access contacts via: asset_hub.crm_contacts.filter(role='broker')

    list_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="List price of the REO property (optional).",
    )

    list_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the property was listed (optional).",
    )

    under_contract_flag = models.BooleanField(
        default=False,
        help_text="Whether the property is under contract (optional).",
    )

    under_contract_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the property went under contract (optional).",
    )

    contract_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Contract price of the REO property (optional).",
    )

    estimated_close_date = models.DateField(
        null=True,
        blank=True,
        help_text="Estimated close date of the REO property (optional).",
    )

    actual_close_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual close date of the REO property (optional).",
    )

    seller_credit_amt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Seller credit amount (optional).",
    )

    # Enumerated purchase type options for clarity and data integrity
    PURCHASE_TYPE_CASH = "cash"
    PURCHASE_TYPE_FINANCING = "financing"
    PURCHASE_TYPE_SELLER_FINANCING = "seller_financing"

    PURCHASE_TYPE_CHOICES = (
        (PURCHASE_TYPE_CASH, "Cash"),
        (PURCHASE_TYPE_FINANCING, "Financing"),
        (PURCHASE_TYPE_SELLER_FINANCING, "Seller Financing"),
    )

    purchase_type = models.CharField(
        max_length=32,
        choices=PURCHASE_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="How the property was purchased (Cash, Financing, Seller Financing).",
    )

    gross_purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Gross purchase price of the REO property (optional).",
    )

    class Meta:
        verbose_name = "REO Data"
        verbose_name_plural = "REO Data"
        ordering = ["-list_date"]

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )

    def clean(self):
        """Model-level validation for REOScope.

        Rules enforced:
        - If `reo_task` is provided, it must belong to the same `asset_hub`.
        - If both `scope_kind` and `reo_task` are provided, they must match (trashout/renovation).

        Note: CRM contacts now managed via AssetCRMContact junction model
        """
        from django.core.exceptions import ValidationError

        errors = {}

        # REO task linkage integrity
        if getattr(self, 'reo_task_id', None):
            if getattr(self.reo_task, 'asset_hub_id', None) != getattr(self, 'asset_hub_id', None):
                errors['reo_task'] = 'Linked REO task must reference the same AssetIdHub.'
            tt = getattr(self.reo_task, 'task_type', None)
            if tt not in ('trashout', 'renovation'):
                errors['reo_task'] = 'Linked REO task must be type Trashout or Renovation.'
            if self.scope_kind and tt and self.scope_kind != tt:
                errors['scope_kind'] = 'Scope kind must match the linked REO task type.'

        if errors:
            raise ValidationError(errors)


class REOtask(models.Model):
    """Simple REO task tracker using Django's TextChoices.

    We use a nested TextChoices enum to define the allowed task types with
    a single source of truth for value+label. Extend later with hub FK,
    due dates, assignee, status, etc.
    Docs reviewed: https://docs.djangoproject.com/en/stable/ref/models/fields/#enumeration-types
    """

    class TaskType(models.TextChoices):
        """Canonical REO task types and their display labels."""

        EVICTION = "eviction", "Eviction"
        TRASHOUT = "trashout", "Trashout"
        RENOVATION = "renovation", "Renovation"
        PRE_MARKETING = "pre_marketing", "Pre-Marketing"
        LISTED = "listed", "Listed"
        UNDER_CONTRACT = "under_contract", "Under Contract"
        SOLD = "sold", "Sold"

    # Selected task type (single-select). Use TaskType.<NAME> in code.
    task_type = models.CharField(
        max_length=20,  # fits the longest value 'under_contract'
        choices=TaskType.choices,  # built-in mapping of value->label
        help_text=(
            "Type of REO task (Eviction, Trashout, Renovation, Pre-Marketing, Listed, Under Contract, Sold)."
        ),
    )

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='reo_tasks',
        help_text='The asset hub this REO task belongs to.',
    )

    # Link to the REO outcome record (many tasks per REOData)
    reo_outcome = models.ForeignKey(
        'am_module.REOData',
        on_delete=models.PROTECT,  # prevent deleting outcome while tasks exist
        related_name='tasks',  # access via: reo_data.tasks.all()
        help_text='The REO outcome record this task is associated with (many-to-one).',
    )

    # User-editable start date for tracking when this task actually began
    task_started = models.DateField(
        null=True,
        blank=True,
        default=date.today,
        help_text='Date when this task was started (defaults to today).',
    )

    # Minimal audit timestamps (used by serializers)
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "REO Task"
        verbose_name_plural = "REO Tasks"
        ordering = ['-created_at', '-id']
        constraints = [
            models.UniqueConstraint(fields=['asset_hub', 'task_type'], name='reo_task_unique_type_per_asset'),
        ]

    # Change tracking (match pattern used by other task models)
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Default task_started to today if not provided
        if not self.task_started:
            self.task_started = timezone.now().date()

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )


class FCSale(models.Model):
    """Data about a foreclosure sale (hub-keyed 1:1)."""

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='fc_sale',
        help_text='1:1 with hub; foreclosure sale keyed by AssetIdHub.',
    )

    # Note: CRM contacts are now managed via AssetCRMContact junction model
    # Access contacts via: asset_hub.crm_contacts.filter(role='legal')
    # This allows multiple contacts per asset independent of outcome type
    nod_noi_sent_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date NOI was sent to NOD (optional).",
    )

    nod_noi_expire_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date NOI expires (optional).",
    )

    fc_sale_sched_date = models.DateField(
        null=True,
        blank=True,
        help_text="Scheduled date of the foreclosure sale (optional).",
    )

    fc_sale_actual_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual date of the foreclosure sale (optional).",
    )

    fc_bid_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Bid price of the foreclosure sale (optional).",
    )
    fc_sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Sale price of the foreclosure sale (optional).",
    )

    class Meta:
        verbose_name = "Foreclosure Sale"
        verbose_name_plural = "Foreclosure Sales"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )


class FCTask(models.Model):
    """Foreclosure workflow task linked to an `FCSale` record.

    Uses Django's TextChoices for well-defined stage values. Extend later with
    due dates, assignee, notes, etc.
    """

    class TaskType(models.TextChoices):
        NOD_NOI = "nod_noi", "NOD/NOI"
        FC_FILING = "fc_filing", "FC Filing"
        MEDIATION = "mediation", "Mediation"
        JUDGEMENT = "judgement", "Judgement"
        REDEMPTION = "redemption", "Redemption"
        SALE_SCHEDULED = "sale_scheduled", "Sale Scheduled"
        SOLD = "sold", "Sold"

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='fc_tasks',
        help_text='The asset hub this foreclosure task belongs to.',
    )

    # Link to the foreclosure sale record (many tasks per FCSale)
    fc_sale = models.ForeignKey(
        'am_module.FCSale',
        on_delete=models.PROTECT,  # prevent deleting sale while tasks exist
        related_name='tasks',  # access via: fc_sale.tasks.all()
        help_text='The FCSale record this task is associated with (many-to-one).',
    )

    # Selected stage
    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='Foreclosure workflow stage for this task.',
    )

    # User-editable start date for tracking when this task actually began
    task_started = models.DateField(
        null=True,
        blank=True,
        default=date.today,
        help_text='Date when this task was started (defaults to today).',
    )

    # Minimal audit timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "Foreclosure Task"
        verbose_name_plural = "Foreclosure Tasks"
        constraints = [
            models.UniqueConstraint(fields=['asset_hub', 'task_type'], name='fc_task_unique_type_per_asset'),
        ]

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Default task_started to today if not provided
        if not self.task_started:
            self.task_started = timezone.now().date()

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )

class DIL(models.Model):
    """Data about a DIL (hub-keyed 1:1)."""

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='dil',
        help_text='1:1 with hub; DIL keyed by AssetIdHub.',
    )

    # Note: CRM contacts are now managed via AssetCRMContact junction model
    # Access contacts via: asset_hub.crm_contacts.filter(role='legal')

    dil_completion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Completion date of the DIL (optional).",
    )

    dil_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average cost of the DIL (optional).",
    )

    cfk_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="CFK cost of the DIL (optional).",
    )

    class Meta:
        verbose_name = "Deed in Lieu (DIL)"
        verbose_name_plural = "Deeds in Lieu (DILs)"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )


class ShortSale(models.Model):
    """Data about a short sale (hub-keyed 1:1)."""

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='short_sale',
        help_text='1:1 with hub; short sale keyed by AssetIdHub.',
    )

    # Note: CRM contacts are now managed via AssetCRMContact junction model
    # Access contacts via: asset_hub.crm_contacts.filter(role='legal')

    acceptable_min_offer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Acceptable minimum offer for the short sale (optional).",
    )

    short_sale_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the short sale (optional).",
    )
    gross_proceeds = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Gross proceeds of the short sale (optional).",
    )
    short_sale_list_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the short sale list (optional).",
    )

    short_sale_list_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="List price of the short sale (optional).",
    )

    class Meta:
        verbose_name = "Short Sale"
        verbose_name_plural = "Short Sales"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )


class ShortSaleTask(models.Model):
    """Short Sale workflow task linked to a `ShortSale` record.

    Uses Django's TextChoices for well-defined stage values.
    """

    class TaskType(models.TextChoices):
        LIST_PRICE_ACCEPTED = "list_price_accepted", "List Price Accepted"
        LISTED = "listed", "Listed"
        UNDER_CONTRACT = "under_contract", "Under-Contract"
        SOLD = "sold", "Sold"

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='short_sale_tasks',
        help_text='The asset hub this short sale task belongs to.',
    )

    # Link to the ShortSale record (many tasks per ShortSale)
    short_sale = models.ForeignKey(
        'am_module.ShortSale',
        on_delete=models.PROTECT,
        related_name='tasks',
        help_text='The ShortSale record this task is associated with (many-to-one).',
    )

    # Selected stage
    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='Short Sale workflow stage for this task.',
    )

    # User-editable start date for tracking when this task actually began
    task_started = models.DateField(
        null=True,
        blank=True,
        default=date.today,
        help_text='Date when this task was started (defaults to today).'
    )

    # Minimal audit timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "Short Sale Task"
        verbose_name_plural = "Short Sale Tasks"
        constraints = [
            models.UniqueConstraint(fields=['asset_hub', 'task_type'], name='short_sale_task_unique_type_per_asset'),
        ]

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Default task_started to today if not provided
        if not self.task_started:
            self.task_started = timezone.now().date()

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )


class Modification(models.Model):
    """Data about a modification (hub-keyed 1:1)."""

    # Enumerated payment type options for clarity and data integrity
    MOD_PAYMENT_PI = "pi"
    MOD_PAYMENT_IO = "io"
    MOD_PAYMENT_OTHER = "other"
    MODIFICATION_PAYMENT_CHOICES = (
        (MOD_PAYMENT_PI, "P&I"),
        (MOD_PAYMENT_IO, "Interest Only"),
        (MOD_PAYMENT_OTHER, "Other"),
    )

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='modification',
        help_text='1:1 with hub; modification keyed by AssetIdHub.',
    )

    # Note: CRM contacts are now managed via AssetCRMContact junction model
    # Access contacts via: asset_hub.crm_contacts.filter(role='legal')

    modification_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the modification (optional).",
    )

    modification_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost of the modification (optional).",
    )

    modification_upb = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="UPB of the modification (optional).",
    )

    modification_term = models.IntegerField(
        null=True,
        blank=True,
        help_text="Term of the modification (optional).",
    )

    modification_rate = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Rate of the modification (optional).",
    )

    modification_maturity_date = models.DateField(
        null=True,
        blank=True,
        help_text="Maturity date of the modification (optional).",
    )

    modification_pi = models.CharField(
        max_length=32,
        choices=MODIFICATION_PAYMENT_CHOICES,
        null=True,
        blank=True,
        help_text="Payment of the modification (optional).",
    )

    modification_down_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Down payment of the modification (optional).",
    )

    note_sale_proceeds = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Gross proceeds from note sale (when modification track leads to note sale).",
    )

    note_sale_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the note sale (optional).",
    )

    class Meta:
        verbose_name = "Loan Modification"
        verbose_name_plural = "Loan Modifications"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )


class ModificationTask(models.Model):
    """Modification workflow task linked to a `Modification` record.

    Uses Django's TextChoices for well-defined stage values.
    """

    class TaskType(models.TextChoices):
        Drafted = "mod_drafted", "Drafted"
        Executed = "mod_executed", "Executed"
        Re_Performing = "mod_rpl", "Re-Performing"
        Failed = "mod_failed", "Failed"
        Note_Sale = "note_sale", "Note Sale"

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='modification_tasks',
        help_text='The asset hub this modification task belongs to.',
    )

    # Link to the Modification record (many tasks per Modification)
    modification = models.ForeignKey(
        'am_module.Modification',
        on_delete=models.PROTECT,
        related_name='tasks',
        help_text='The Modification record this task is associated with (many-to-one).',
    )

    # Selected stage
    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='Modification workflow stage for this task.',
    )

    # User-editable start date for tracking when this task actually began
    task_started = models.DateField(
        null=True,
        blank=True,
        default=date.today,
        help_text='Date when this task was started (defaults to today).'
    )

    # Minimal audit timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "Modification Task"
        verbose_name_plural = "Modification Tasks"
        constraints = [
            models.UniqueConstraint(fields=['asset_hub', 'task_type'], name='modification_task_unique_type_per_asset'),
        ]

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Default task_started to today if not provided
        if not self.task_started:
            self.task_started = timezone.now().date()

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)
                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )


class NoteSale(models.Model):
    """
    WHAT: Data about a Note Sale outcome (hub-keyed 1:1).
    WHY: Track sale of performing or re-performing notes to trading partners
    WHERE: Asset Management module, separate outcome track
    HOW: Links to AssetIdHub with OneToOne relationship and MasterCRM for trading partner
    """

    # WHAT: Primary key linking to the asset hub
    # WHY: Ensures 1:1 relationship between asset and Note Sale outcome
    # HOW: OneToOneField with PROTECT to prevent orphaned data
    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='note_sale',
        help_text='1:1 with hub; Note Sale keyed by AssetIdHub.',
    )

    # WHAT: Date when the note was sold
    # WHY: Track timeline of note sale transaction
    # HOW: DateField with default to today, but can be edited if entered late
    sold_date = models.DateField(
        null=True,
        blank=True,
        default=date.today,
        help_text="Date when the note was sold (defaults to today).",
    )

    # WHAT: Gross proceeds received from note sale
    # WHY: Track financial outcome of the sale
    # HOW: DecimalField with precision for large dollar amounts
    proceeds = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Gross proceeds received from the note sale (optional).",
    )

    # WHAT: Trading partner who purchased the note
    # WHY: Track buyer relationship for future business
    # HOW: ForeignKey to MasterCRM filtered by trading_partner tag
    trading_partner = models.ForeignKey(
        'core.MasterCRM',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='note_sales',
        help_text="Trading partner who purchased the note (optional, filtered by tag='trading_partner').",
    )

    class Meta:
        verbose_name = "Note Sale"
        verbose_name_plural = "Note Sales"

    # WHAT: Change tracking infrastructure
    # WHY: Support audit logging for all field changes
    # HOW: Private attribute to hold acting user, accessed via set_actor() method
    _actor = None

    def set_actor(self, user):
        """
        WHAT: Set the user who is making changes to this record.
        WHY: Enable attribution of changes for audit logging
        HOW: Stores user in private _actor attribute
        """
        self._actor = user

    def save(self, *args, **kwargs):
        """
        WHAT: Save with automatic audit logging for all field changes.
        WHY: Maintain complete change history for compliance and debugging
        HOW: Capture original values, save record, then log diffs to AuditLog
        """
        # WHAT: Extract actor from kwargs or instance attribute
        # WHY: Support both passing actor as kwarg or via set_actor() method
        actor = kwargs.pop('actor', None) or self._actor

        # WHAT: Capture original field values before save
        # WHY: Need baseline to compute what changed after save
        # HOW: Fetch existing record from DB if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # WHAT: Persist the record to database
        # WHY: Save must happen before we can log changes
        super().save(*args, **kwargs)

        # WHAT: Log changes for all fields that actually changed
        # WHY: Create audit trail for compliance and debugging
        # HOW: Compare each field's old vs new value and create AuditLog entry if different
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )


class NoteSaleTask(models.Model):
    """
    WHAT: Note Sale workflow task linked to a NoteSale record.
    WHY: Track progression of note sale from initial interest through closing
    WHERE: Asset Management module, Note Sale outcome track
    HOW: Many-to-one relationship with NoteSale using Django TextChoices for stages

    Uses Django's TextChoices for well-defined stage values. Each stage represents
    a milestone in the note sale process.
    Docs reviewed: https://docs.djangoproject.com/en/stable/ref/models/fields/#enumeration-types
    """

    # WHAT: Enumeration of allowed task types for Note Sale workflow
    # WHY: Provide type-safe, well-defined stages with consistent value/label mapping
    # HOW: Django's TextChoices pattern for single source of truth
    class TaskType(models.TextChoices):
        """
        WHAT: Canonical Note Sale task types and their display labels.
        WHY: Define workflow stages for note sale process
        HOW: TextChoices provides value, label pairs
        """
        POTENTIAL_NOTE_SALE = "potential_note_sale", "Potential Note Sale"
        OUT_TO_MARKET = "out_to_market", "Out to Market"
        PENDING_SALE = "pending_sale", "Pending Sale"
        SOLD = "sold", "Sold"

    # WHAT: Direct link to the asset hub for simplified querying.
    # WHY: Enable efficient filtering of tasks by asset without joining through outcome
    # HOW: ForeignKey with related_name for reverse lookups
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='note_sale_tasks',
        help_text='The asset hub this note sale task belongs to.',
    )

    # WHAT: Link to the NoteSale outcome record
    # WHY: Many tasks can be associated with one Note Sale outcome
    # HOW: ForeignKey with PROTECT to prevent orphaned tasks
    note_sale = models.ForeignKey(
        'am_module.NoteSale',
        on_delete=models.PROTECT,
        related_name='tasks',
        help_text='The NoteSale record this task is associated with (many-to-one).',
    )

    # WHAT: Selected workflow stage for this task
    # WHY: Track which milestone this task represents
    # HOW: CharField with TaskType.choices constraint
    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='Note Sale workflow stage for this task.',
    )

    # WHAT: User-editable start date for tracking when this task actually began
    # WHY: Track timeline of each workflow stage
    # HOW: DateField with backend default to today
    task_started = models.DateField(
        null=True,
        blank=True,
        default=timezone.now,
        help_text='Date when this task was started (defaults to today).'
    )

    # WHAT: Minimal audit timestamps for record tracking
    # WHY: Track when tasks are created and modified
    # HOW: auto_now_add for creation, auto_now for updates
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "Note Sale Task"
        verbose_name_plural = "Note Sale Tasks"
        # WHAT: Unique constraint to prevent duplicate task types per asset
        # WHY: Each asset should only have one task per stage (e.g., only one "Sold" task)
        # HOW: UniqueConstraint on combination of asset_hub and task_type
        constraints = [
            models.UniqueConstraint(fields=['asset_hub', 'task_type'], name='note_sale_task_unique_type_per_asset'),
        ]

    # WHAT: Change tracking infrastructure
    # WHY: Support audit logging for all field changes
    # HOW: Private attribute to hold acting user, accessed via set_actor() method
    _actor = None

    def set_actor(self, user):
        """
        WHAT: Set the user who is making changes to this record.
        WHY: Enable attribution of changes for audit logging
        HOW: Stores user in private _actor attribute
        """
        self._actor = user

    def save(self, *args, **kwargs):
        """
        WHAT: Save with automatic audit logging for all field changes.
        WHY: Maintain complete change history for compliance and debugging
        HOW: Capture original values, save record, then log diffs to AuditLog
        """
        # WHAT: Extract actor from kwargs or instance attribute
        # WHY: Support both passing actor as kwarg or via set_actor() method
        actor = kwargs.pop('actor', None) or self._actor

        # WHAT: Capture original field values before save
        # WHY: Need baseline to compute what changed after save
        # HOW: Fetch existing record from DB if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # WHAT: Default task_started to today if not provided
        # WHY: Auto-populate start date for convenience
        # HOW: Check if task_started is None and set to current date
        if not self.task_started:
            self.task_started = timezone.now().date()

        # WHAT: Persist the record to database
        # WHY: Save must happen before we can log changes
        super().save(*args, **kwargs)

        # WHAT: Log changes for all fields that actually changed
        # WHY: Create audit trail for compliance and debugging
        # HOW: Compare each field's old vs new value and create AuditLog entry if different
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub
                    )


class PerformingTrack(models.Model):
    """Track record for Performing / RPL / Note Sale workflow (hub-keyed 1:1)."""

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='performing_track',
        help_text='1:1 with hub; Performing Track keyed by AssetIdHub.',
    )

    class Meta:
        verbose_name = "Performing Track"
        verbose_name_plural = "Performing Tracks"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )


class PerformingTask(models.Model):
    """Performing workflow task linked to a `PerformingTrack` record."""

    class TaskType(models.TextChoices):
        PERF = "perf", "Performing"
        RPL = "rpl", "Re-Performing (RPL)"
        NOTE_SOLD = "note_sold", "Note Sold"

    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='performing_tasks',
        help_text='The asset hub this performing task belongs to.',
    )

    performing_track = models.ForeignKey(
        'am_module.PerformingTrack',
        on_delete=models.PROTECT,
        related_name='tasks',
        help_text='The PerformingTrack record this task is associated with (many-to-one).',
    )

    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='Performing workflow stage for this task.',
    )

    task_started = models.DateField(
        null=True,
        blank=True,
        default=date.today,
        help_text='Date when this task was started (defaults to today).'
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "Performing Task"
        verbose_name_plural = "Performing Tasks"
        constraints = [
            models.UniqueConstraint(fields=['asset_hub', 'task_type'], name='performing_task_unique_type_per_asset'),
        ]

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Default task_started to today if not provided
        if not self.task_started:
            self.task_started = timezone.now().date()

        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )


class DelinquentTrack(models.Model):
    """Track record for Delinquent workflow (hub-keyed 1:1)."""

    asset_hub = models.OneToOneField(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='delinquent_track',
        help_text='1:1 with hub; Delinquent Track keyed by AssetIdHub.',
    )

    class Meta:
        verbose_name = "Delinquent Track"
        verbose_name_plural = "Delinquent Tracks"

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )


class DelinquentTask(models.Model):
    """Delinquent workflow task linked to a `DelinquentTrack` record."""

    class TaskType(models.TextChoices):
        DQ_30 = "dq_30", "30 Days Delinquent"
        DQ_60 = "dq_60", "60 Days Delinquent"
        DQ_90 = "dq_90", "90 Days Delinquent"
        DQ_120_PLUS = "dq_120_plus", "120+ Days Delinquent"
        LOSS_MIT = "loss_mit", "Loss Mit"
        FC_DIL = "fc_dil", "FC/DIL"

    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='delinquent_tasks',
        help_text='The asset hub this delinquent task belongs to.',
    )

    delinquent_track = models.ForeignKey(
        'am_module.DelinquentTrack',
        on_delete=models.PROTECT,
        related_name='tasks',
        help_text='The DelinquentTrack record this task is associated with (many-to-one).',
    )

    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='Delinquent workflow stage for this task.',
    )

    task_started = models.DateField(
        null=True,
        blank=True,
        default=date.today,
        help_text='Date when this task was started (defaults to today).'
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "Delinquent Task"
        verbose_name_plural = "Delinquent Tasks"
        constraints = [
            models.UniqueConstraint(fields=['asset_hub', 'task_type'], name='delinquent_task_unique_type_per_asset'),
        ]

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Default task_started to today if not provided
        if not self.task_started:
            self.task_started = timezone.now().date()

        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )


class DILTask(models.Model):
    """DIL workflow task linked to a `DIL` record.

    Uses Django's TextChoices for well-defined stage values.
    """

    class TaskType(models.TextChoices):
        PURSUING_DIL = "pursuing_dil", "Pursuing DIL"
        OWNER_CONTACTED = "owner_contacted", "Owner/Heirs contacted"
        # Explicit tag when DIL process fails
        DIL_FAILED = "dil_failed", "DIL Failed"
        DRAFTED = "dil_drafted", "Drafted"
        EXECUTED = "dil_executed", "Executed"

    # Direct link to the asset hub for simplified querying.
    asset_hub = models.ForeignKey(
        'core.AssetIdHub',
        on_delete=models.PROTECT,
        related_name='dil_tasks',
        help_text='The asset hub this DIL task belongs to.',
    )

    # Link to the DIL record (many tasks per DIL)
    dil = models.ForeignKey(
        'am_module.DIL',
        on_delete=models.PROTECT,
        related_name='tasks',
        help_text='The DIL record this task is associated with (many-to-one).',
    )

    # Selected stage
    task_type = models.CharField(
        max_length=32,
        choices=TaskType.choices,
        help_text='DIL workflow stage for this task.',
    )

    # User-editable start date for tracking when this task actually began
    task_started = models.DateField(
        null=True,
        blank=True,
        default=date.today,
        help_text='Date when this task was started (defaults to today).'
    )

    # Minimal audit timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="When this task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="When this task was last updated.")

    class Meta:
        verbose_name = "DIL Task"
        verbose_name_plural = "DIL Tasks"
        constraints = [
            models.UniqueConstraint(fields=['asset_hub', 'task_type'], name='dil_task_unique_type_per_asset'),
        ]

    # Change tracking
    _actor = None

    def set_actor(self, user):
        """Set the user who is making changes to this record."""
        self._actor = user

    def save(self, *args, **kwargs):
        """Save with automatic audit logging for all field changes."""
        actor = kwargs.pop('actor', None) or self._actor

        # Get original values if this is an update
        if self.pk:
            try:
                original = self.__class__.objects.get(pk=self.pk)
                original_values = {field.name: getattr(original, field.name) for field in self._meta.fields}
            except self.__class__.DoesNotExist:
                original_values = {}
        else:
            original_values = {}

        # Default task_started to today if not provided
        if not self.task_started:
            self.task_started = timezone.now().date()

        # Save the record
        super().save(*args, **kwargs)

        # Log changes for all fields
        if original_values:
            AuditLog = _audit_log_model()
            for field in self._meta.fields:
                field_name = field.name
                old_value = original_values.get(field_name)
                new_value = getattr(self, field_name)

                # Only log if value actually changed
                if old_value != new_value:
                    AuditLog.log_change(
                        instance=self,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by=actor,
                        asset_hub=self.asset_hub,
                    )
