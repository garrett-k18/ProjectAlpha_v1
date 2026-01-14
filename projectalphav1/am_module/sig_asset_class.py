import logging

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _sync_asset_class_from_active_tracks(asset_hub_id: int) -> None:
    from core.models.model_co_assetIdHub import AssetDetails
    from am_module.models.model_am_tracksTasks import (
        PerformingTask,
        PerformingTrack,
        REOData,
        REOtask,
    )

    if not asset_hub_id:
        return

    reo_active = REOData.objects.filter(asset_hub_id=asset_hub_id).exists() and not REOtask.objects.filter(
        asset_hub_id=asset_hub_id,
        task_type='sold',
    ).exists()

    performing_active = PerformingTrack.objects.filter(asset_hub_id=asset_hub_id).exists() and not PerformingTask.objects.filter(
        asset_hub_id=asset_hub_id,
        task_type='note_sold',
    ).exists()

    if reo_active:
        AssetDetails.objects.filter(asset_id=asset_hub_id).update(asset_class=AssetDetails.AssetClass.REO)
    elif performing_active:
        AssetDetails.objects.filter(asset_id=asset_hub_id).update(asset_class=AssetDetails.AssetClass.PERFORMING)


@receiver(post_save, sender='am_module.REOData')
def sync_asset_class_on_reo_data_save(sender, instance, created: bool, **kwargs):
    transaction.on_commit(lambda: _sync_asset_class_from_active_tracks(getattr(instance, 'asset_hub_id', None) or instance.pk))


@receiver(post_save, sender='am_module.REOtask')
def sync_asset_class_on_reo_task_save(sender, instance, created: bool, **kwargs):
    transaction.on_commit(lambda: _sync_asset_class_from_active_tracks(getattr(instance, 'asset_hub_id', None)))


@receiver(post_save, sender='am_module.PerformingTrack')
def sync_asset_class_on_performing_track_save(sender, instance, created: bool, **kwargs):
    transaction.on_commit(lambda: _sync_asset_class_from_active_tracks(getattr(instance, 'asset_hub_id', None) or instance.pk))


@receiver(post_save, sender='am_module.PerformingTask')
def sync_asset_class_on_performing_task_save(sender, instance, created: bool, **kwargs):
    transaction.on_commit(lambda: _sync_asset_class_from_active_tracks(getattr(instance, 'asset_hub_id', None)))


@receiver(post_delete, sender='am_module.REOData')
def sync_asset_class_on_reo_data_delete(sender, instance, **kwargs):
    transaction.on_commit(lambda: _sync_asset_class_from_active_tracks(getattr(instance, 'asset_hub_id', None) or instance.pk))


@receiver(post_delete, sender='am_module.REOtask')
def sync_asset_class_on_reo_task_delete(sender, instance, **kwargs):
    transaction.on_commit(lambda: _sync_asset_class_from_active_tracks(getattr(instance, 'asset_hub_id', None)))


@receiver(post_delete, sender='am_module.PerformingTrack')
def sync_asset_class_on_performing_track_delete(sender, instance, **kwargs):
    transaction.on_commit(lambda: _sync_asset_class_from_active_tracks(getattr(instance, 'asset_hub_id', None) or instance.pk))


@receiver(post_delete, sender='am_module.PerformingTask')
def sync_asset_class_on_performing_task_delete(sender, instance, **kwargs):
    transaction.on_commit(lambda: _sync_asset_class_from_active_tracks(getattr(instance, 'asset_hub_id', None)))
