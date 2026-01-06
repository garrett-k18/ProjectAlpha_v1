"""
Django signals for AM module.

WHAT: Handles automatic regeneration of note summaries when notes are created or updated.
WHY: Ensures summaries stay current without manual intervention.
HOW: Uses Django post_save and post_delete signals to trigger summary regeneration.

Docs reviewed:
- Django signals: https://docs.djangoproject.com/en/stable/topics/signals/
- Django async signals: https://docs.djangoproject.com/en/stable/topics/signals/#asynchronous-signals
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from am_module.models.model_am_amData import AMNote
from am_module.services.serv_am_noteSummary import generate_note_summary

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AMNote)
def regenerate_summary_on_note_save(sender, instance: AMNote, created: bool, **kwargs):
    """
    WHAT: Regenerates note summary when a note is created or updated.
    WHY: Keeps summaries current with latest note content.
    HOW: Calls generate_note_summary service after note save.
    
    Args:
        sender: The AMNote model class
        instance: The AMNote instance that was saved
        created: True if this is a new note, False if it was updated
        **kwargs: Additional signal arguments
    """
    # WHAT: Get asset hub ID from note
    # WHY: Summary is keyed by asset hub
    # HOW: Access asset_hub_id from note instance
    asset_hub_id = getattr(instance, 'asset_hub_id', None)
    
    # WHAT: Guard against None asset hub
    # WHY: Notes should always have asset hub, but be defensive
    # HOW: Check if asset_hub_id exists before proceeding
    if not asset_hub_id:
        logger.warning(f"AMNote {instance.id} has no asset_hub_id, skipping summary regeneration")
        return
    
    try:
        # WHAT: Regenerate summary for this asset hub
        # WHY: Notes changed, summary needs update
        # HOW: Call generate_note_summary service with force_regenerate=True
        generate_note_summary(asset_hub_id, force_regenerate=True)
        logger.debug(f"Regenerated note summary for asset hub {asset_hub_id} after note {'creation' if created else 'update'}")
    except Exception as e:
        # WHAT: Log error but don't break note save
        # WHY: Summary generation failure shouldn't prevent note creation
        # HOW: Log exception and continue
        logger.exception(f"Failed to regenerate summary for asset hub {asset_hub_id} after note save: {e}")


@receiver(post_delete, sender=AMNote)
def regenerate_summary_on_note_delete(sender, instance: AMNote, **kwargs):
    """
    WHAT: Regenerates note summary when a note is deleted.
    WHY: Summary should reflect current notes, including deletions.
    HOW: Calls generate_note_summary service after note deletion.
    
    Args:
        sender: The AMNote model class
        instance: The AMNote instance that was deleted
        **kwargs: Additional signal arguments
    """
    # WHAT: Get asset hub ID from deleted note instance
    # WHY: Need to know which asset's summary to regenerate
    # HOW: Access asset_hub_id from instance (still available after delete)
    asset_hub_id = getattr(instance, 'asset_hub_id', None)
    
    # WHAT: Guard against None asset hub
    # WHY: Defensive programming
    # HOW: Check if asset_hub_id exists
    if not asset_hub_id:
        logger.warning(f"Deleted AMNote {instance.id} had no asset_hub_id, skipping summary regeneration")
        return
    
    try:
        # WHAT: Regenerate summary for this asset hub
        # WHY: Note was deleted, summary needs update
        # HOW: Call generate_note_summary service with force_regenerate=True
        generate_note_summary(asset_hub_id, force_regenerate=True)
        logger.debug(f"Regenerated note summary for asset hub {asset_hub_id} after note deletion")
    except Exception as e:
        # WHAT: Log error but don't break note deletion
        # WHY: Summary generation failure shouldn't prevent note deletion
        # HOW: Log exception and continue
        logger.exception(f"Failed to regenerate summary for asset hub {asset_hub_id} after note delete: {e}")

